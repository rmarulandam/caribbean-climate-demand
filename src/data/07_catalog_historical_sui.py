"""Catalog official historical SUI Formato 1/2 archives in a reproducible manifest."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import pathlib
import re
import sys
import zipfile

# Ensure repository root is on sys.path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from src.utils.paths import get_raw_sui_dir, REPO_ROOT


ARCHIVE_RE = re.compile(r"Energia_(438|439)_M_(\d{1,2})_(\d{4})\.csv\.zip$", re.I)
SOURCE_BASE = "https://sui.superservicios.gov.co/sites/default/files/datosAbiertos"
SOURCE_PAGES = {
    "438": "https://sui.superservicios.gov.co/datos-abiertos/Energia/"
    "Energia-Formato-1-Vinculo-usuario-alimentador-usuario-transformador",
    "439": "https://sui.superservicios.gov.co/datos-abiertos/Energia/"
    "Energia-Formato-2-Informacion-Comercial-Residencial",
}


def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_header(archive: pathlib.Path) -> tuple[str, int, list[str]]:
    with zipfile.ZipFile(archive) as zf:
        members = [item for item in zf.infolist() if item.filename.lower().endswith((".csv", ".txt"))]
        if len(members) != 1:
            raise ValueError(f"Expected one CSV/TXT member in {archive}; found {len(members)}")
        member = members[0]
        with zf.open(member) as raw:
            line = raw.readline().decode("utf-8-sig", errors="replace")
        header = next(csv.reader([line]))
        return member.filename, member.file_size, header


def build_manifest(raw_root: pathlib.Path, years: set[int]) -> dict:
    datasets = []
    for code, subfolder_name, label in (
        ("438", "formato1_438", "Formato 1"),
        ("439", "formato2_439", "Formato 2"),
    ):
        candidates = [
            raw_root / "via_b_historico_creg097" / subfolder_name,
            raw_root / subfolder_name,
            raw_root / "formato1" if code == "438" else raw_root / "formato2",
        ]
        folder = next((p for p in candidates if p.exists()), candidates[0])

        files = []
        for archive in sorted(folder.rglob("*.zip")):
            match = ARCHIVE_RE.fullmatch(archive.name)
            if not match or match.group(1) != code:
                continue
            month, year = int(match.group(2)), int(match.group(3))
            if year not in years:
                continue
            member, uncompressed_bytes, columns = read_header(archive)
            files.append(
                {
                    "year": year,
                    "month": month,
                    "filename": archive.name,
                    "relative_path": f"00_raw_sui/via_b_historico_creg097/{subfolder_name}/{archive.name}",
                    "source_url": f"{SOURCE_BASE}/{archive.name}",
                    "compressed_bytes": archive.stat().st_size,
                    "uncompressed_bytes": uncompressed_bytes,
                    "zip_member": member,
                    "columns": columns,
                    "sha256": sha256(archive),
                }
            )
        files.sort(key=lambda item: (item["year"], item["month"]))
        datasets.append(
            {
                "code": code,
                "format": label,
                "source_page": SOURCE_PAGES[code],
                "expected_months": len(years) * 12,
                "available_months": len(files),
                "files": files,
            }
        )
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "project": "caribbean-climate-demand",
        "regime": "CREG 097/2008",
        "coverage": {"years": sorted(years), "periodicity": "monthly", "geography": "national"},
        "operator": {
            "name": "Electrificadora del Caribe S.A. E.S.P. (Electricaribe)",
            "verified_id_empresa": "2249",
            "legacy_requested_id": "2238",
            "note": "SSPD sources identify Electricaribe as 2249; 2238 is retained only for audit compatibility.",
        },
        "caribbean_dane_department_prefixes": ["08", "13", "20", "23", "44", "47", "70"],
        "historical_availability": {
            "438": {
                "published_from": "2010-09",
                "published_to": "2021-06",
                "pre_2018_acquired": False,
            },
            "439": {
                "published_from": "2007-01",
                "published_to": "2021-06",
                "pre_2018_acquired": False,
            },
        },
        "datasets": datasets,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--years", nargs="+", type=int, default=[2018, 2019, 2020])
    parser.add_argument("--raw-dir", type=pathlib.Path, default=None, help="Directory containing raw SUI historical archives.")
    parser.add_argument("--output", type=pathlib.Path)
    args = parser.parse_args()

    raw_root = args.raw_dir or get_raw_sui_dir()
    manifest = build_manifest(raw_root, set(args.years))
    output = args.output or REPO_ROOT / "data" / "manifests" / "sui_2018_2020_manifest.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote manifest with {sum(len(d['files']) for d in manifest['datasets'])} entries to {output}")


if __name__ == "__main__":
    main()
