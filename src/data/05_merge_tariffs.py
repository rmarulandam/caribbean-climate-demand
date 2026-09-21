"""
Script 05: Merge published CREG unit cost tariffs and DANE macroeconomic deflators.
Computes real energy costs per kWh by operator, stratum, and billing month.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

import pandas as pd

# Ensure repository root is on sys.path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from src.utils.paths import get_tariffs_dir, get_intermediate_dir, REPO_ROOT


def load_tariffs(tariffs_path: pathlib.Path) -> pd.DataFrame:
    if not tariffs_path.exists():
        print(f"[SKIP] Tariffs file not found: {tariffs_path}")
        return pd.DataFrame()
    df = pd.read_excel(tariffs_path, sheet_name="CU_HISTORICO")
    print(f"[LOADED] {len(df)} tariff records from {tariffs_path.name}")
    return df


def load_ipc(ipc_path: pathlib.Path) -> pd.DataFrame:
    if not ipc_path.exists():
        print(f"[SKIP] IPC file not found: {ipc_path}")
        return pd.DataFrame()
    df = pd.read_csv(ipc_path)
    # Calculate deflator relative to base Dec 2023
    dec_2023_rows = df[(df["year"] == 2023) & (df["month"] == 12)]
    if not dec_2023_rows.empty:
        dec_2023_val = dec_2023_rows["ipc_index_base_2018"].values[0]
        df["deflator_dec_2023"] = df["ipc_index_base_2018"] / dec_2023_val
    print(f"[LOADED] {len(df)} IPC monthly records from {ipc_path.name}")
    return df


def main():
    parser = argparse.ArgumentParser(description="Merge CREG tariffs and DANE IPC deflators.")
    parser.add_argument("--tariffs-dir", type=pathlib.Path, default=None, help="Directory containing tariff Excel and IPC CSV.")
    parser.add_argument("--intermediate-dir", type=pathlib.Path, default=None, help="Directory for intermediate files.")
    args = parser.parse_args()

    tariffs_dir = args.tariffs_dir or get_tariffs_dir()
    interm_dir = args.intermediate_dir or get_intermediate_dir()

    df_tariffs = load_tariffs(tariffs_dir / "CREG_CU_Tarifas_2021_2024.xlsx")
    df_ipc = load_ipc(tariffs_dir / "dane_ipc_2021_2024.csv")

    if not df_tariffs.empty and not df_ipc.empty:
        merged = pd.merge(df_tariffs, df_ipc, left_on=["ANNO", "MES"], right_on=["year", "month"], how="left")
        if "deflator_dec_2023" in merged.columns:
            merged["CU_REAL_DEC2023"] = merged["CU_COSTO_UNITARIO"] / merged["deflator_dec_2023"]
        out_file = interm_dir / "tariffs_deflated_clean.parquet"
        interm_dir.mkdir(parents=True, exist_ok=True)
        merged.to_parquet(out_file, index=False)
        print(f"[SAVED] Deflated tariffs written to {out_file}")


if __name__ == "__main__":
    main()
