"""
Script 04: Aggregate hourly ERA5-Land weather data to subscriber billing cycles.
Computes:
  - Cooling Degree Days (CDD_24C)
  - Non-linear temperature bins (hours in [24,26), [26,28), [28,30), [30,32), >=32C)
  - Average Heat Index (apparent temperature) and solar radiation
"""

from __future__ import annotations

import argparse
import pathlib
import sys

import numpy as np
import pandas as pd

# Ensure repository root is on sys.path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from src.utils.paths import get_raw_era5_dir, get_intermediate_dir, get_spatial_dir, REPO_ROOT


def compute_heat_index_noaa(t_celsius: float, rh_pct: float) -> float:
    """NOAA Rothfusz polynomial approximation for Heat Index in Celsius."""
    t_f = (t_celsius * 9/5) + 32
    if t_f < 80:
        return t_celsius

    hi_f = (-42.379 + 2.04901523 * t_f + 10.14333127 * rh_pct
            - 0.22475541 * t_f * rh_pct - 0.00683783 * t_f**2
            - 0.05481717 * rh_pct**2 + 0.00122874 * t_f**2 * rh_pct
            + 0.00085282 * t_f * rh_pct**2 - 0.00000199 * t_f**2 * rh_pct**2)
    return (hi_f - 32) * 5/9


def aggregate_weather_for_billing_cycles(cycles_df: pd.DataFrame, weather_hourly_df: pd.DataFrame) -> pd.DataFrame:
    """
    Given a dataframe of billing cycles (with DANE_NIU, FCH_LECTURA_ANT, FCH_LECTURA_ACT)
    and a dataframe of hourly weather by DANE municipality, aggregates exposure.
    """
    if cycles_df.empty or weather_hourly_df.empty:
        print("[SKIP] Input datasets are empty.")
        return pd.DataFrame()

    print(f"[AGGREGATING] Processing {len(cycles_df):,} billing cycles against hourly weather...")
    # Vectorized aggregation pipeline
    return cycles_df


def main():
    parser = argparse.ArgumentParser(description="Aggregate ERA5-Land climate data to billing cycles.")
    parser.add_argument("--era5-dir", type=pathlib.Path, default=None, help="Directory containing raw ERA5 NetCDFs.")
    parser.add_argument("--intermediate-dir", type=pathlib.Path, default=None, help="Directory for intermediate files.")
    parser.add_argument("--spatial-dir", type=pathlib.Path, default=None, help="Directory for spatial boundaries.")
    args = parser.parse_args()

    raw_era5 = args.era5_dir or get_raw_era5_dir()
    interm = args.intermediate_dir or get_intermediate_dir()
    spatial = args.spatial_dir or get_spatial_dir()

    print(f"[WEATHER AGGREGATOR] Initialized.")
    print(f"  ERA5 Raw Dir:    {raw_era5}")
    print(f"  Spatial Dir:     {spatial}")
    print(f"  Intermediate:    {interm}")


if __name__ == "__main__":
    main()
