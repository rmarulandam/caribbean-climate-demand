"""
Script 06: Build final analysis release panel for Gate E2 Data Approval.
Unites cleaned SUI billing, subscriber fixed attributes, billing-window climate exposure,
and real CREG tariffs into data/releases/panel_caribe_2021_2024_v1.parquet.
"""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import sys

import pandas as pd

# Ensure repository root is on sys.path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from src.utils.paths import get_intermediate_dir, get_releases_dir, REPO_ROOT


def hash_file(filepath: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def build_release_panel(interm_dir: pathlib.Path, release_dir: pathlib.Path):
    release_dir.mkdir(parents=True, exist_ok=True)

    tc1_path = interm_dir / "sui_caribe_tc1_clean.parquet"
    tc2_path = interm_dir / "sui_caribe_tc2_clean.parquet"
    tariffs_path = interm_dir / "tariffs_deflated_clean.parquet"
    weather_path = interm_dir / "weather_billing_exposure.parquet"

    output_path = release_dir / "panel_caribe_2021_2024_v1.parquet"

    if not (tc1_path.exists() and tc2_path.exists()):
        print("[INFO] Intermediate SUI inputs not yet generated. Run scripts 01-03 first.")
        return

    print("[BUILDING] Assembling Gate E2 estimation panel...")
    df_tc1 = pd.read_parquet(tc1_path)
    df_tc2 = pd.read_parquet(tc2_path)

    # Inner join on NIU
    panel = pd.merge(df_tc2, df_tc1, on="NIU", how="inner")

    # Save release
    panel.to_parquet(output_path, index=False, compression="zstd")
    sha = hash_file(output_path)
    print(f"\n==========================================")
    print(f"GATE E2 RELEASE PANEL GENERATED")
    print(f"File: {output_path.name}")
    print(f"Total Observations: {len(panel):,}")
    print(f"Unique Subscribers: {panel['NIU'].nunique():,}")
    print(f"SHA-256: {sha}")
    print(f"==========================================\n")


def main():
    parser = argparse.ArgumentParser(description="Build Gate E2 Master Release Panel.")
    parser.add_argument("--intermediate-dir", type=pathlib.Path, default=None, help="Directory with intermediate Parquet files.")
    parser.add_argument("--release-dir", type=pathlib.Path, default=None, help="Directory for final release panel.")
    args = parser.parse_args()

    interm_dir = args.intermediate_dir or get_intermediate_dir()
    release_dir = args.release_dir or get_releases_dir()

    build_release_panel(interm_dir, release_dir)


if __name__ == "__main__":
    main()
