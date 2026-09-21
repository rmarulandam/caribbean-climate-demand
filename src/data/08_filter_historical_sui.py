"""Create Caribbean historical extracts from national SUI Formato 1/2 archives.

The source files cover the CREG 097/2008 reporting regime. All source values are
kept as strings; provenance columns identify the archive, year, month, and format.
"""

from __future__ import annotations

import argparse
import csv
import gc
import json
import pathlib
import re
import sys
import tempfile
import unicodedata
import zipfile

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.csv as pacsv
import pyarrow.parquet as pq

# Ensure repository root is on sys.path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from src.utils.paths import get_raw_sui_dir, get_intermediate_dir, resolve_raw_archive, REPO_ROOT


CARIBBEAN_DANE_PREFIXES = ("08", "13", "20", "23", "44", "47", "70")
VERIFIED_ELECTRICARIBE_IDS = {"2249"}
LEGACY_REQUESTED_IDS = {"2238"}
ELECTRICARIBE_NAME_PATTERN = r"ELECTRIFICADORA\s+DEL\s+CARIBE|ELECTRICARIBE"


def canonical_name(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^A-Za-z0-9]+", "_", value.strip()).strip("_")
    return value.upper()


def source_header(zf: zipfile.ZipFile, member: zipfile.ZipInfo) -> list[str]:
    with zf.open(member) as raw:
        line = raw.readline().decode("utf-8-sig", errors="replace")
    return next(csv.reader([line]))


def select_archives(raw_dir: pathlib.Path, manifest_path: pathlib.Path) -> list[dict]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    archives = []
    for dataset in manifest["datasets"]:
        code = dataset["code"]
        subfolder = "formato1_438" if code == "438" else "formato2_439"
        for item in dataset["files"]:
            fname = item["filename"]
            # Try multiple resolution candidates
            candidates = [
                resolve_raw_archive(fname, code),
                raw_dir / fname,
                raw_dir / "via_b_historico_creg097" / subfolder / fname,
                raw_dir / subfolder / fname,
                raw_dir / item.get("relative_path", ""),
                REPO_ROOT / item.get("relative_path", ""),
            ]
            # Formato 2 year subfolders
            if "year" in item:
                candidates.append(raw_dir / "via_b_historico_creg097" / subfolder / str(item["year"]) / fname)
                candidates.append(raw_dir / subfolder / str(item["year"]) / fname)

            found = next((p for p in candidates if p is not None and p.exists()), None)
            if not found:
                raise FileNotFoundError(f"Could not locate {fname} in {raw_dir} or Google Drive raw store.")
            archives.append({**item, "code": code, "path": found})
    return sorted(archives, key=lambda item: (item["code"], item["year"], item["month"]))


def output_columns(archives: list[dict]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {"438": [], "439": []}
    for item in archives:
        columns = result[item["code"]]
        for name in item["columns"]:
            canonical = canonical_name(name)
            if canonical not in columns:
                columns.append(canonical)
    for columns in result.values():
        columns.extend(["SOURCE_FILE", "SOURCE_YEAR", "SOURCE_MONTH", "SOURCE_FORMAT"])
    return result


def is_caribbean_dane(series: pa.ChunkedArray | pa.Array) -> pc.Expression:
    clean = pc.utf8_lpad(pc.utf8_trim_whitespace(series), 5, "0")
    mask = pc.equal(pc.scalar(False), pc.scalar(True))
    for prefix in CARIBBEAN_DANE_PREFIXES:
        mask = pc.or_(mask, pc.starts_with(clean, prefix))
    return mask


def record_mask(table: pa.Table, code: str) -> pa.ChunkedArray:
    names = set(table.column_names)
    mask = None

    id_candidates = [
        "ID_EMPRESA",
        "ID_COMERCIALIZADOR",
        "IDENTIFICADOR_DE_LA_EMPRESA",
        "IDENTIFICADOR_EMPRESA",
        "CAR_T440_ID_COMER",
    ]
    for name in id_candidates:
        if name in names:
            series = pc.utf8_trim_whitespace(table[name])
            cond = pc.is_in(series, pa.array(sorted(VERIFIED_ELECTRICARIBE_IDS | LEGACY_REQUESTED_IDS)))
            mask = cond if mask is None else pc.or_(mask, cond)

    name_candidates = [
        "NOMBRE_DE_LA_EMPRESA",
        "NOMBRE_EMPRESA",
        "EMPRESA",
        "COMERCIALIZADOR",
        "CAR_T440_NOM_COMER",
    ]
    for name in name_candidates:
        if name in names:
            series = pc.utf8_upper(pc.utf8_trim_whitespace(table[name]))
            cond = pc.match_substring_regex(series, ELECTRICARIBE_NAME_PATTERN)
            mask = cond if mask is None else pc.or_(mask, cond)

    dane_candidates = [
        "CODIGO_DANE_DEL_MUNICIPIO",
        "CODIGO_DANE_MUNICIPIO",
        "DANE_MUNICIPIO",
        "MUNICIPIO",
        "DANE_NIU",
        "CAR_T440_COD_MUNI",
    ]
    for name in dane_candidates:
        if name in names:
            cond = is_caribbean_dane(table[name])
            mask = cond if mask is None else pc.or_(mask, cond)

    if mask is None:
        raise ValueError(f"Could not build a Caribbean filter mask for table with columns {table.column_names}")
    return mask


def align_table(table: pa.Table, columns: list[str], item: dict) -> pa.Table:
    arrays = []
    n_rows = table.num_rows
    for name in columns:
        if name == "SOURCE_FILE":
            arrays.append(pa.array([item["filename"]] * n_rows, type=pa.string()))
        elif name == "SOURCE_YEAR":
            arrays.append(pa.array([str(item["year"])] * n_rows, type=pa.string()))
        elif name == "SOURCE_MONTH":
            arrays.append(pa.array([f"{item['month']:02d}"] * n_rows, type=pa.string()))
        elif name == "SOURCE_FORMAT":
            arrays.append(pa.array([item["code"]] * n_rows, type=pa.string()))
        elif name in table.column_names:
            arrays.append(table[name].cast(pa.string()))
        else:
            arrays.append(pa.nulls(n_rows, type=pa.string()))
    return pa.Table.from_arrays(arrays, names=columns)


def stream_zip_member(zip_path: pathlib.Path, member_name: str, batch_size_bytes: int = 64 * 1024 * 1024):
    with zipfile.ZipFile(zip_path) as zf:
        with zf.open(member_name) as raw:
            line_iter = iter(raw)
            try:
                header = next(line_iter)
            except StopIteration:
                return
            while True:
                chunk = [header]
                size = len(header)
                while size < batch_size_bytes:
                    try:
                        line = next(line_iter)
                    except StopIteration:
                        break
                    chunk.append(line)
                    size += len(line)
                if len(chunk) == 1:
                    break
                yield b"".join(chunk)


def filter_csv_chunk(chunk_bytes: bytes, delimiter: str = ",") -> bytes:
    reader = csv.reader(io.StringIO(chunk_bytes.decode("utf-8-sig", errors="replace")), delimiter=delimiter)
    try:
        header = next(reader)
    except StopIteration:
        return b""
    header_canon = [canonical_name(c) for c in header]

    col_map = {name: i for i, name in enumerate(header_canon)}
    id_idxs = [col_map[c] for c in ["ID_EMPRESA", "IDENTIFICADOR_DE_LA_EMPRESA", "IDENTIFICADOR_EMPRESA", "ID_COMERCIALIZADOR", "CAR_T440_ID_COMER"] if c in col_map]
    name_idxs = [col_map[c] for c in ["NOMBRE_DE_LA_EMPRESA", "NOMBRE_EMPRESA", "EMPRESA", "COMERCIALIZADOR", "CAR_T440_NOM_COMER"] if c in col_map]
    dane_idxs = [col_map[c] for c in ["CODIGO_DANE_DEL_MUNICIPIO", "CODIGO_DANE_MUNICIPIO", "DANE_MUNICIPIO", "MUNICIPIO", "DANE_NIU", "CAR_T440_COD_MUNI"] if c in col_map]

    out_rows = [header]
    re_elec = re.compile(ELECTRICARIBE_NAME_PATTERN, re.I)
    target_ids = VERIFIED_ELECTRICARIBE_IDS | LEGACY_REQUESTED_IDS

    for row in reader:
        matched = False
        for idx in id_idxs:
            if idx < len(row) and row[idx].strip() in target_ids:
                matched = True
                break
        if not matched:
            for idx in name_idxs:
                if idx < len(row) and re_elec.search(row[idx].strip()):
                    matched = True
                    break
        if not matched:
            for idx in dane_idxs:
                if idx < len(row):
                    dane_clean = row[idx].strip().zfill(5)
                    if any(dane_clean.startswith(p) for p in CARIBBEAN_DANE_PREFIXES):
                        matched = True
                        break
        if matched:
            out_rows.append(row)

    if len(out_rows) <= 1:
        return b""

    out_io = io.StringIO()
    writer = csv.writer(out_io, delimiter=delimiter)
    writer.writerows(out_rows)
    return out_io.getvalue().encode("utf-8")


def process_format(archives: list[dict], code: str, columns: list[str], output: pathlib.Path) -> int:
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = output.with_suffix(".tmp")
    schema = pa.schema([pa.field(name, pa.string()) for name in columns])
    writer = pq.ParquetWriter(temp, schema, compression="zstd")
    total = 0
    try:
        for item in archives:
            if item["code"] != code:
                continue
            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_path = pathlib.Path(tmp_dir)
                filtered_csv = tmp_path / "filtered.csv"
                with filtered_csv.open("wb") as out_f:
                    for chunk_idx, chunk_bytes in enumerate(stream_zip_member(item["path"], item["zip_member"])):
                        filtered_bytes = filter_csv_chunk(chunk_bytes, delimiter=",")
                        if filtered_bytes:
                            if chunk_idx > 0:
                                lines = filtered_bytes.split(b"\n", 1)
                                if len(lines) > 1:
                                    out_f.write(lines[1])
                            else:
                                out_f.write(filtered_bytes)

                if not filtered_csv.exists() or filtered_csv.stat().st_size == 0:
                    print(f"{code} {item['year']}-{item['month']:02d}: 0 Caribbean rows (chunk-filtered)")
                    continue

                read_options = pacsv.ReadOptions(block_size=32 * 1024 * 1024)
                parse_options = pacsv.ParseOptions(delimiter=",", invalid_row_handler=lambda row: "skip")
                convert_options = pacsv.ConvertOptions(
                    column_types={canonical_name(name): pa.string() for name in item["columns"]},
                    strings_can_be_null=True,
                )
                input_stream = filtered_csv.open("rb")
                reader = pacsv.open_csv(
                    input_stream,
                    read_options=read_options,
                    parse_options=parse_options,
                    convert_options=convert_options,
                )
                file_rows = 0
                try:
                    for batch in reader:
                        table = pa.Table.from_batches([batch])
                        table = table.rename_columns([canonical_name(name) for name in table.column_names])
                        filtered = table.filter(record_mask(table, code))
                        if filtered.num_rows:
                            aligned = align_table(filtered, columns, item)
                            writer.write_table(aligned)
                            file_rows += aligned.num_rows
                    total += file_rows
                    print(f"{code} {item['year']}-{item['month']:02d}: {file_rows:,} Caribbean rows")
                finally:
                    if reader is not None:
                        reader.close()
                    if input_stream is not None:
                        input_stream.close()
                    reader = None
                    input_stream = None
                    gc.collect()
                    filtered_csv.unlink(missing_ok=True)
    finally:
        writer.close()
    temp.replace(output)
    print(f"Wrote {total:,} rows to {output}")
    return total


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=("438", "439", "both"), default="both")
    parser.add_argument("--raw-dir", type=pathlib.Path, default=None, help="Directory containing raw SUI historical archives.")
    parser.add_argument("--manifest", type=pathlib.Path)
    parser.add_argument("--years", nargs="+", type=int)
    parser.add_argument("--output-dir", type=pathlib.Path)
    parser.add_argument("--output", type=pathlib.Path)
    args = parser.parse_args()

    if args.output and args.format == "both":
        parser.error("--output requires a single --format")

    raw_dir = args.raw_dir or get_raw_sui_dir()
    manifest = args.manifest or REPO_ROOT / "data" / "manifests" / "sui_2018_2020_manifest.json"
    archives = select_archives(raw_dir, manifest)
    columns = output_columns(archives)
    if args.years:
        years = set(args.years)
        archives = [item for item in archives if item["year"] in years]
    targets = ("438", "439") if args.format == "both" else (args.format,)

    interm = args.output_dir or get_intermediate_dir()
    outputs = {
        "438": interm / "sui_caribe_f1_raw.parquet",
        "439": interm / "sui_caribe_f2_raw.parquet",
    }
    if args.output:
        outputs[args.format] = args.output
    for code in targets:
        process_format(archives, code, columns[code], outputs[code])


if __name__ == "__main__":
    main()
