"""
Script 02: Filter Caribbean regional operators (Afinia / CaribeMar and Air-e / CaribeSol) from national SUI microdata.
Processes all national ZIP files for TC1 (1732) and TC2 (1743) and outputs regional Parquet files.
"""

from __future__ import annotations

import argparse
import csv
import io
import os
import pathlib
import sys
import zipfile

import pyarrow as pa
import pyarrow.parquet as pq

# Ensure repository root is on sys.path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from src.utils.paths import get_raw_sui_dir, get_intermediate_dir, REPO_ROOT

CARIBBEAN_DEPARTMENTS_DANE_PREFIXES = ("08", "13", "20", "23", "44", "47", "70")
CARIBBEAN_COMPANIES_KEYWORDS = ["AFINIA", "CARIBEMAR", "AIR-E", "AIRE", "ELECTRICARIBE"]
CARIBBEAN_COMPANY_IDS = {"48305", "48307"}  # Afinia and Air-e SSPD IDs


def is_caribbean_record(company_id_str: str, company_name_str: str, dane_code_str: str) -> bool:
    cid = str(company_id_str).strip()
    if cid in CARIBBEAN_COMPANY_IDS:
        return True

    c_upper = str(company_name_str).upper()
    for kw in CARIBBEAN_COMPANIES_KEYWORDS:
        if kw in c_upper:
            return True

    d_clean = str(dane_code_str).strip().zfill(5)
    return d_clean.startswith(CARIBBEAN_DEPARTMENTS_DANE_PREFIXES)


def find_zips(raw_dir: pathlib.Path, pattern: str) -> list[pathlib.Path]:
    """Finds matching zip files in raw_dir and standard subdirectories."""
    matches = list(raw_dir.glob(pattern)) + list(raw_dir.glob(pattern.lower()))
    sub = raw_dir / "via_a_moderno_creg015"
    if sub.exists():
        matches.extend(list(sub.glob(pattern)) + list(sub.glob(pattern.lower())))
    return sorted(list(set(matches)))


def process_tc1_archives(raw_dir: pathlib.Path, output_parquet: pathlib.Path):
    tc1_zips = find_zips(raw_dir, "ENERGIA_1732_*.zip")
    if not tc1_zips:
        print("[SKIP] No TC1 (1732) archives found in", raw_dir)
        return

    print(f"\n=======================================================")
    print(f"Processing TC1 (1732 - Caracterizacion de Usuarios)")
    print(f"Found {len(tc1_zips)} archives in {raw_dir}")
    print(f"=======================================================")

    writer = None
    total_records = 0

    for zip_path in tc1_zips:
        print(f"\n[STREAMING] {zip_path.name}...")
        batch_rows = []
        with zipfile.ZipFile(zip_path, "r") as z:
            for member in z.namelist():
                if not member.lower().endswith((".csv", ".txt")):
                    continue
                with z.open(member) as f:
                    wrapper = io.TextIOWrapper(f, encoding="utf-8", errors="replace")
                    reader = csv.DictReader(wrapper, delimiter="|")

                    for row in reader:
                        cid = row.get("ID_COMERCIALIZADOR", "") or row.get("IDENTIFICADOR_EMPRESA", "")
                        emp = row.get("COMERCIALIZADOR", "") or row.get("EMPRESA", "")
                        dane = row.get("DANE_NIU", "")

                        if is_caribbean_record(cid, emp, dane):
                            batch_rows.append(row)

                        if len(batch_rows) >= 100000:
                            table = pa.Table.from_pylist(batch_rows)
                            if writer is None:
                                output_parquet.parent.mkdir(parents=True, exist_ok=True)
                                writer = pq.ParquetWriter(output_parquet, table.schema, compression="zstd")
                            writer.write_table(table)
                            total_records += len(batch_rows)
                            print(f"  --> Streamed {total_records:,} Caribbean records so far...")
                            batch_rows = []

        if batch_rows:
            table = pa.Table.from_pylist(batch_rows)
            if writer is None:
                output_parquet.parent.mkdir(parents=True, exist_ok=True)
                writer = pq.ParquetWriter(output_parquet, table.schema, compression="zstd")
            writer.write_table(table)
            total_records += len(batch_rows)

    if writer:
        writer.close()
        print(f"\n[TC1 COMPLETE] Saved {total_records:,} Caribbean records to {output_parquet}")
    else:
        print(f"\n[TC1 WARNING] No Caribbean records matched across archives.")


def process_tc2_archives(raw_dir: pathlib.Path, output_parquet: pathlib.Path):
    tc2_zips = find_zips(raw_dir, "ENERGIA_1743_*.zip")
    if not tc2_zips:
        print("[SKIP] No TC2 (1743) archives found in", raw_dir)
        return

    print(f"\n=======================================================")
    print(f"Processing TC2 (1743 - Facturacion y Consumo por NIU)")
    print(f"Found {len(tc2_zips)} archives in {raw_dir}")
    print(f"=======================================================")

    writer = None
    total_records = 0

    for zip_path in tc2_zips:
        print(f"\n[STREAMING] {zip_path.name}...")
        batch_rows = []
        with zipfile.ZipFile(zip_path, "r") as z:
            for member in z.namelist():
                if not member.lower().endswith((".csv", ".txt")):
                    continue
                with z.open(member) as f:
                    wrapper = io.TextIOWrapper(f, encoding="utf-8", errors="replace")
                    reader = csv.DictReader(wrapper, delimiter="|")

                    for row in reader:
                        cid = row.get("ID_COMERCIALIZADOR", "") or row.get("IDENTIFICADOR_EMPRESA", "")
                        emp = row.get("COMERCIALIZADOR", "") or row.get("EMPRESA", "")
                        dane = row.get("DANE_NIU", "")

                        if is_caribbean_record(cid, emp, dane):
                            batch_rows.append(row)

                        if len(batch_rows) >= 100000:
                            table = pa.Table.from_pylist(batch_rows)
                            if writer is None:
                                output_parquet.parent.mkdir(parents=True, exist_ok=True)
                                writer = pq.ParquetWriter(output_parquet, table.schema, compression="zstd")
                            writer.write_table(table)
                            total_records += len(batch_rows)
                            print(f"  --> Streamed {total_records:,} Caribbean records so far...")
                            batch_rows = []

        if batch_rows:
            table = pa.Table.from_pylist(batch_rows)
            if writer is None:
                output_parquet.parent.mkdir(parents=True, exist_ok=True)
                writer = pq.ParquetWriter(output_parquet, table.schema, compression="zstd")
            writer.write_table(table)
            total_records += len(batch_rows)

    if writer:
        writer.close()
        print(f"\n[TC2 COMPLETE] Saved {total_records:,} Caribbean records to {output_parquet}")
    else:
        print(f"\n[TC2 WARNING] No Caribbean records matched across archives.")


def main():
    parser = argparse.ArgumentParser(description="Filter Caribbean records from national SUI modern microdata.")
    parser.add_argument("--raw-dir", type=pathlib.Path, default=None, help="Directory containing raw SUI ZIP archives.")
    parser.add_argument("--output-dir", type=pathlib.Path, default=None, help="Directory for output Parquet extracts.")
    args = parser.parse_args()

    raw_sui = args.raw_dir or get_raw_sui_dir()
    interm = args.output_dir or get_intermediate_dir()

    process_tc1_archives(raw_sui, interm / "sui_caribe_tc1_raw.parquet")
    process_tc2_archives(raw_sui, interm / "sui_caribe_tc2_raw.parquet")


if __name__ == "__main__":
    main()
