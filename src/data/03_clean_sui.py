"""Clean and standardize SUI billing data for econometric estimation.

Vía A (TC1/TC2) keeps the original in-memory implementation.  Vía B is
processed as Arrow batches because the historical F2 extract contains more
than 50 million rows.  Its required filters are deliberately narrow:

* standard billing cycle: 25 <= billed days <= 35;
* actual meter reading: historical code ``R``;
* numeric consumption and a parseable billing start date.

No Vía-A consumption cap is imposed on Vía B.  The closed climate interval is
``[T_INICIO, T_FIN]``, where ``T_FIN = T_INICIO + billed_days - 1``.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
import os
import pathlib
import sys
from typing import Iterable

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


F2_INPUT_NAMES = (
    "sui_caribe_f2_2018.parquet",
    "sui_caribe_f2_2019.parquet",
    "sui_caribe_f2_2020.parquet",
)
F2_OUTPUT_NAME = "sui_caribe_f2_clean.parquet"
F2_ATTRITION_NAME = "sui_caribe_f2_attrition.json"

F2_DAYS_FIELDS = ("DIAS_FACTURADOS", "CAR_T440_DIAS_FACT")
F2_READING_FIELDS = ("TIPO_DE_LECTURA", "CAR_T440_TIPO_LECT")
F2_CONSUMPTION_FIELDS = ("CONSUMOS",)
F2_START_FIELDS = (
    "FECHA_DE_INICIO_DEL_PERIODO_DE_FACTURACION",
    "CAR_T440_FEC_INI",
)


def clean_tc1_attributes(tc1_path: pathlib.Path) -> pd.DataFrame:
    if not tc1_path.exists():
        print(f"[SKIP] TC1 input not found: {tc1_path}")
        return pd.DataFrame()

    df = pd.read_parquet(tc1_path)
    initial_len = len(df)

    df["NIU"] = df["NIU"].astype(str).str.strip()
    df = df[df["NIU"] != ""].drop_duplicates(subset=["NIU"])

    df["ESTRATO_SECTOR"] = pd.to_numeric(df["ESTRATO_SECTOR"], errors="coerce")
    df = df[df["ESTRATO_SECTOR"].isin([1, 2, 3, 4, 5, 6])]

    df["DANE_NIU"] = df["DANE_NIU"].astype(str).str.strip().str.zfill(5)
    df["DPTO_CODE"] = df["DANE_NIU"].str[:2]
    df = df[df["DPTO_CODE"].isin(["08", "13", "20", "23", "44", "47", "70"])]

    print(
        f"[TC1 CLEAN] Retained {len(df):,} of {initial_len:,} users "
        f"({len(df) / max(1, initial_len):.1%})"
    )
    return df[
        [
            "NIU",
            "DANE_NIU",
            "DPTO_CODE",
            "ESTRATO_SECTOR",
            "UBICACION",
            "COD_CIRCUITO_LINEA",
            "COD_TRANSFORMADOR",
            "EMPRESA",
        ]
    ]


def clean_tc2_billing(tc2_path: pathlib.Path) -> pd.DataFrame:
    if not tc2_path.exists():
        print(f"[SKIP] TC2 input not found: {tc2_path}")
        return pd.DataFrame()

    df = pd.read_parquet(tc2_path)
    initial_len = len(df)

    df["TIPO_LECTURA"] = df["TIPO_LECTURA"].astype(str).str.upper().str.strip()
    df = df[df["TIPO_LECTURA"].isin(["REAL", "R"])]

    df["CAR_T1743_DIAS_FACTURADOS"] = pd.to_numeric(
        df["CAR_T1743_DIAS_FACTURADOS"], errors="coerce"
    )
    df = df[
        (df["CAR_T1743_DIAS_FACTURADOS"] >= 25)
        & (df["CAR_T1743_DIAS_FACTURADOS"] <= 35)
    ]

    df["CONS_USUARIO"] = pd.to_numeric(df["CONS_USUARIO"], errors="coerce")
    df = df[(df["CONS_USUARIO"] > 0) & (df["CONS_USUARIO"] <= 3000)]

    df["kwh_per_day"] = df["CONS_USUARIO"] / df["CAR_T1743_DIAS_FACTURADOS"]
    df["log_kwh_per_day"] = np.log(df["kwh_per_day"])

    df["FCH_LECTURA_ANT"] = pd.to_datetime(
        df["FCH_LECTURA_ANT"], errors="coerce", dayfirst=True
    )
    df["FCH_LECTURA_ACT"] = pd.to_datetime(
        df["FCH_LECTURA_ACT"], errors="coerce", dayfirst=True
    )
    df = df[df["FCH_LECTURA_ACT"] > df["FCH_LECTURA_ANT"]]

    print(
        f"[TC2 CLEAN] Retained {len(df):,} of {initial_len:,} billing cycles "
        f"({len(df) / max(1, initial_len):.1%})"
    )
    return df


def _coalesce_text(frame: pd.DataFrame, fields: Iterable[str]) -> pd.Series:
    """Return the first nonblank value across historical schema aliases."""
    result = pd.Series(pd.NA, index=frame.index, dtype="string")
    for field in fields:
        values = frame[field].astype("string").str.strip()
        values = values.mask(values.eq(""))
        result = result.fillna(values)
    return result


def _parse_f2_start_dates(values: pd.Series) -> pd.Series:
    """Parse documented F2 date encodings without ambiguous day/month guesses."""
    text = values.astype("string").str.strip()
    # Second resolution supports malformed far-future years long enough for us
    # to classify them explicitly instead of failing with a nanosecond overflow.
    parsed = pd.Series(pd.NaT, index=text.index, dtype="datetime64[s]")
    # The descriptive SUI exports use U.S. month/day ordering.  CAR_T440 uses ISO.
    for date_format in ("%m/%d/%Y", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        candidate = pd.to_datetime(text, format=date_format, errors="coerce").astype(
            "datetime64[s]"
        )
        parsed = parsed.fillna(candidate)
    plausible = parsed.between("2000-01-01", "2030-12-31", inclusive="both")
    parsed = parsed.mask(~plausible.fillna(False))
    return parsed


def _new_attrition(year: int) -> dict:
    return {
        "source_year": year,
        "input_rows": 0,
        "standard_cycle_rows": 0,
        "dropped_nonstandard_or_invalid_days": 0,
        "real_reading_rows_after_cycle_filter": 0,
        "dropped_non_real_after_cycle_filter": 0,
        "numeric_consumption_rows_after_quality_filters": 0,
        "dropped_invalid_consumption_after_quality_filters": 0,
        "valid_interval_rows": 0,
        "dropped_invalid_start_date": 0,
        "output_rows": 0,
        "zero_consumption_output_rows": 0,
        "negative_consumption_output_rows": 0,
        "reading_type_counts_all_rows": Counter(),
    }


def _add_metrics(target: dict, source: dict) -> None:
    for key, value in source.items():
        if key in {"source_year", "reading_type_counts_all_rows"}:
            continue
        target[key] += int(value)
    target["reading_type_counts_all_rows"].update(
        source["reading_type_counts_all_rows"]
    )


def _serializable_attrition(metrics: dict) -> dict:
    result = dict(metrics)
    result["reading_type_counts_all_rows"] = dict(
        sorted(metrics["reading_type_counts_all_rows"].items())
    )
    input_rows = result["input_rows"]
    result["retention_rate"] = (
        result["output_rows"] / input_rows if input_rows else None
    )
    return result


def clean_f2_billing(
    input_paths: Iterable[pathlib.Path],
    output_path: pathlib.Path,
    attrition_path: pathlib.Path,
    batch_size: int = 131_072,
) -> dict:
    """Stream-clean historical F2 partitions and write one atomic Parquet."""
    paths = list(input_paths)
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing Vía B input(s): {missing}")

    parquet_files = [pq.ParquetFile(path) for path in paths]
    base_schema = parquet_files[0].schema_arrow
    for path, parquet_file in zip(paths[1:], parquet_files[1:]):
        if parquet_file.schema_arrow != base_schema:
            raise ValueError(f"Vía B schema differs from first partition: {path}")

    required = set(
        F2_DAYS_FIELDS + F2_READING_FIELDS + F2_CONSUMPTION_FIELDS + F2_START_FIELDS
    )
    absent = sorted(required.difference(base_schema.names))
    if absent:
        raise KeyError(f"Vía B inputs lack required schema aliases: {absent}")

    derived_fields = [
        pa.field("F2_DIAS_FACTURADOS", pa.int16()),
        pa.field("F2_TIPO_LECTURA", pa.string()),
        pa.field("F2_CONSUMO_KWH", pa.float64()),
        pa.field("Y_KWH_DIA", pa.float64()),
        pa.field("T_INICIO", pa.date32()),
        pa.field("T_FIN", pa.date32()),
    ]
    collisions = [field.name for field in derived_fields if field.name in base_schema.names]
    if collisions:
        raise ValueError(f"Derived Vía B columns already exist: {collisions}")
    output_schema = pa.schema(list(base_schema) + derived_fields)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_output = output_path.with_name(output_path.name + ".tmp")
    if temporary_output.exists():
        temporary_output.unlink()

    overall = _new_attrition(0)
    annual: list[dict] = []
    writer = pq.ParquetWriter(
        temporary_output,
        output_schema,
        compression="zstd",
        use_dictionary=True,
        write_statistics=True,
    )
    try:
        for path, parquet_file in zip(paths, parquet_files):
            year = int(path.stem.rsplit("_", 1)[-1])
            metrics = _new_attrition(year)
            for batch in parquet_file.iter_batches(batch_size=batch_size):
                table = pa.Table.from_batches([batch])
                helper = table.select(sorted(required)).to_pandas()

                days = pd.to_numeric(
                    _coalesce_text(helper, F2_DAYS_FIELDS), errors="coerce"
                )
                reading = (
                    _coalesce_text(helper, F2_READING_FIELDS).str.upper().str.strip()
                )
                consumption = pd.to_numeric(
                    _coalesce_text(helper, F2_CONSUMPTION_FIELDS), errors="coerce"
                )
                start = _parse_f2_start_dates(
                    _coalesce_text(helper, F2_START_FIELDS)
                )

                rows = len(helper)
                standard_cycle = days.between(25, 35, inclusive="both")
                real_reading = reading.eq("R").fillna(False)
                numeric_consumption = consumption.notna() & np.isfinite(consumption)
                valid_start = start.notna()

                after_cycle = standard_cycle
                after_reading = after_cycle & real_reading
                after_consumption = after_reading & numeric_consumption
                final_mask = after_consumption & valid_start

                read_labels = reading.fillna("<MISSING>").value_counts(dropna=False)
                metrics["reading_type_counts_all_rows"].update(
                    {str(key): int(value) for key, value in read_labels.items()}
                )
                metrics["input_rows"] += rows
                metrics["standard_cycle_rows"] += int(after_cycle.sum())
                metrics["dropped_nonstandard_or_invalid_days"] += int(
                    rows - after_cycle.sum()
                )
                metrics["real_reading_rows_after_cycle_filter"] += int(
                    after_reading.sum()
                )
                metrics["dropped_non_real_after_cycle_filter"] += int(
                    after_cycle.sum() - after_reading.sum()
                )
                metrics["numeric_consumption_rows_after_quality_filters"] += int(
                    after_consumption.sum()
                )
                metrics["dropped_invalid_consumption_after_quality_filters"] += int(
                    after_reading.sum() - after_consumption.sum()
                )
                metrics["valid_interval_rows"] += int(final_mask.sum())
                metrics["dropped_invalid_start_date"] += int(
                    after_consumption.sum() - final_mask.sum()
                )

                if not final_mask.any():
                    continue

                selected = final_mask.to_numpy(dtype=bool)
                filtered = table.filter(pa.array(selected))
                kept_days = days[selected].astype("int16")
                kept_consumption = consumption[selected].astype("float64")
                kept_start = start[selected]
                kept_finish = kept_start + pd.to_timedelta(kept_days - 1, unit="D")

                metrics["output_rows"] += int(selected.sum())
                metrics["zero_consumption_output_rows"] += int(
                    kept_consumption.eq(0).sum()
                )
                metrics["negative_consumption_output_rows"] += int(
                    kept_consumption.lt(0).sum()
                )

                filtered = filtered.append_column(
                    "F2_DIAS_FACTURADOS",
                    pa.array(kept_days, type=pa.int16()),
                )
                filtered = filtered.append_column(
                    "F2_TIPO_LECTURA",
                    pa.array(["R"] * len(kept_days), type=pa.string()),
                )
                filtered = filtered.append_column(
                    "F2_CONSUMO_KWH",
                    pa.array(kept_consumption, type=pa.float64()),
                )
                filtered = filtered.append_column(
                    "Y_KWH_DIA",
                    pa.array(kept_consumption / kept_days, type=pa.float64()),
                )
                filtered = filtered.append_column(
                    "T_INICIO",
                    pa.array(kept_start.dt.date, type=pa.date32()),
                )
                filtered = filtered.append_column(
                    "T_FIN",
                    pa.array(kept_finish.dt.date, type=pa.date32()),
                )
                writer.write_table(filtered, row_group_size=batch_size)

            _add_metrics(overall, metrics)
            annual.append(_serializable_attrition(metrics))
            print(
                f"[F2 {year}] retained {metrics['output_rows']:,} of "
                f"{metrics['input_rows']:,} rows "
                f"({metrics['output_rows'] / max(1, metrics['input_rows']):.1%})"
            )
    except BaseException:
        writer.close()
        if temporary_output.exists():
            temporary_output.unlink()
        raise
    else:
        writer.close()
        os.replace(temporary_output, output_path)

    report = {
        "track": "Vía B / SUI Formato 2 (439)",
        "filters": {
            "standard_billing_days_inclusive": [25, 35],
            "required_reading_type": "R",
            "consumption_rule": "numeric and finite; zero/negative values retained and reported",
            "date_rule": (
                "parseable billing start date between 2000-01-01 and 2030-12-31"
            ),
        },
        "climate_interval": {
            "convention": "closed interval [T_INICIO, T_FIN]",
            "formula": "T_FIN = T_INICIO + F2_DIAS_FACTURADOS - 1 day",
        },
        "inputs": [str(path) for path in paths],
        "output": str(output_path),
        "by_year": annual,
        "overall": _serializable_attrition(overall),
    }
    attrition_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"[F2 CLEAN] wrote {overall['output_rows']:,} rows to {output_path}\n"
        f"[F2 ATTRITION] {attrition_path}"
    )
    return report


# Ensure repository root is on sys.path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from src.utils.paths import get_intermediate_dir, REPO_ROOT


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--track",
        choices=("a", "b", "both"),
        default="both",
        help="Data track to clean (default: both).",
    )
    parser.add_argument(
        "--intermediate-dir",
        type=pathlib.Path,
        default=None,
        help="Directory containing intermediate Parquet inputs and outputs.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=131_072,
        help="Arrow rows per Vía B processing batch.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    interm = args.intermediate_dir or get_intermediate_dir()

    if args.track in {"a", "both"}:
        tc1_in = interm / "sui_caribe_tc1_raw.parquet"
        tc2_in = interm / "sui_caribe_tc2_raw.parquet"

        df_tc1 = clean_tc1_attributes(tc1_in)
        if not df_tc1.empty:
            df_tc1.to_parquet(
                interm / "sui_caribe_tc1_clean.parquet",
                index=False,
                compression="zstd",
            )

        df_tc2 = clean_tc2_billing(tc2_in)
        if not df_tc2.empty:
            df_tc2.to_parquet(
                interm / "sui_caribe_tc2_clean.parquet",
                index=False,
                compression="zstd",
            )

    if args.track in {"b", "both"}:
        clean_f2_billing(
            [interm / name for name in F2_INPUT_NAMES],
            interm / F2_OUTPUT_NAME,
            interm / F2_ATTRITION_NAME,
            batch_size=args.batch_size,
        )


if __name__ == "__main__":
    main()
