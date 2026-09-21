"""
Central Path and Configuration Management for caribbean-climate-demand.

Resolves paths dynamically across collaborators and environments using:
1. `config/paths.local.toml` (ignored in Git, personal machine configuration)
2. Environment variables (e.g. CARIBBEAN_DRIVE_ROOT, SUI_RAW_DIR)
3. `config/paths.example.toml` defaults / repository fallbacks
"""

from __future__ import annotations

import os
import pathlib
import sys
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None  # type: ignore


# Repository root (two levels up from src/utils/ or three from src/data/)
REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent


def _load_toml(path: pathlib.Path) -> dict[str, Any]:
    if not path.exists() or tomllib is None:
        return {}
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except Exception as e:
        print(f"[WARN] Could not parse {path}: {e}")
        return {}


def load_config() -> dict[str, Any]:
    """Loads configuration merging example defaults with local user overrides."""
    example_cfg = _load_toml(REPO_ROOT / "config" / "paths.example.toml")
    local_cfg = _load_toml(REPO_ROOT / "config" / "paths.local.toml")

    # Merge top-level sections
    merged = example_cfg.copy()
    for k, v in local_cfg.items():
        if isinstance(v, dict) and isinstance(merged.get(k), dict):
            merged[k] = {**merged[k], **v}
        else:
            merged[k] = v
    return merged


def _resolve_path(raw_value: str | pathlib.Path | None, fallback_relative: str) -> pathlib.Path:
    if not raw_value:
        return REPO_ROOT / fallback_relative
    p = pathlib.Path(raw_value)
    if p.is_absolute():
        return p
    return REPO_ROOT / p


def get_repo_root() -> pathlib.Path:
    """Returns absolute path to the Git repository root."""
    return REPO_ROOT


def get_drive_root() -> pathlib.Path | None:
    """
    Returns the root Google Drive store path if configured.
    Checks environment variable CARIBBEAN_DRIVE_ROOT first, then paths.local.toml.
    """
    env_val = os.environ.get("CARIBBEAN_DRIVE_ROOT") or os.environ.get("CARIBBEAN_RAW_STORE")
    if env_val:
        return pathlib.Path(env_val)

    cfg = load_config()
    # Check top-level drive_root or [drive] root
    drive_val = cfg.get("drive_root") or (cfg.get("drive", {}).get("root") if isinstance(cfg.get("drive"), dict) else None)
    if drive_val:
        return pathlib.Path(drive_val)
    return None


def get_raw_sui_dir() -> pathlib.Path:
    """
    Returns directory holding raw SUI archives (Track A and Track B).
    Prioritizes:
    1. SUI_RAW_DIR environment variable
    2. config [raw] sui
    3. <drive_root>/00_raw_sui
    4. <repo_root>/data/raw/sui
    """
    env_val = os.environ.get("SUI_RAW_DIR")
    if env_val:
        return pathlib.Path(env_val)

    cfg = load_config()
    raw_cfg = cfg.get("raw", {})
    if "sui" in raw_cfg and raw_cfg["sui"]:
        return _resolve_path(raw_cfg["sui"], "data/raw/sui")

    drive_root = get_drive_root()
    if drive_root and (drive_root / "00_raw_sui").exists():
        return drive_root / "00_raw_sui"
    if drive_root:
        return drive_root / "00_raw_sui"

    return REPO_ROOT / "data" / "raw" / "sui"


def get_raw_era5_dir() -> pathlib.Path:
    """Returns directory holding raw hourly ERA5-Land NetCDF files."""
    env_val = os.environ.get("ERA5_RAW_DIR")
    if env_val:
        return pathlib.Path(env_val)

    cfg = load_config()
    raw_cfg = cfg.get("raw", {})
    if "era5" in raw_cfg and raw_cfg["era5"]:
        return _resolve_path(raw_cfg["era5"], "data/raw/era5")

    drive_root = get_drive_root()
    if drive_root and (drive_root / "01_raw_climate_era5").exists():
        return drive_root / "01_raw_climate_era5"
    if drive_root:
        return drive_root / "01_raw_climate_era5"

    return REPO_ROOT / "data" / "raw" / "era5"


def get_raw_gis_dir() -> pathlib.Path:
    """Returns directory holding raw GIS bundles (DANE MGN, etc.)."""
    env_val = os.environ.get("GIS_RAW_DIR")
    if env_val:
        return pathlib.Path(env_val)

    cfg = load_config()
    raw_cfg = cfg.get("raw", {})
    if "gis" in raw_cfg and raw_cfg["gis"]:
        return _resolve_path(raw_cfg["gis"], "data/raw/gis")

    drive_root = get_drive_root()
    if drive_root and (drive_root / "02_raw_spatial_gis").exists():
        return drive_root / "02_raw_spatial_gis"
    if drive_root:
        return drive_root / "02_raw_spatial_gis"

    return REPO_ROOT / "data" / "raw" / "gis"


def get_intermediate_local_dir() -> pathlib.Path:
    """Returns the repository local data/intermediate directory."""
    cfg = load_config()
    val = cfg.get("managed", {}).get("intermediate") or "data/intermediate"
    return _resolve_path(val, "data/intermediate")


def get_intermediate_drive_dir() -> pathlib.Path | None:
    """Returns Google Drive intermediate directory if drive_root is configured."""
    drive_root = get_drive_root()
    if drive_root:
        return drive_root / "03_intermediate"
    return None


def get_intermediate_dir(prefer_drive: bool = False) -> pathlib.Path:
    """
    Returns the intermediate directory.
    If prefer_drive is True and drive_root is configured, returns Drive path;
    otherwise returns local data/intermediate.
    """
    if prefer_drive:
        drive_dir = get_intermediate_drive_dir()
        if drive_dir:
            return drive_dir
    return get_intermediate_local_dir()


def get_tariffs_dir() -> pathlib.Path:
    """Returns the local data/tariffs directory (managed in Git LFS)."""
    cfg = load_config()
    val = cfg.get("managed", {}).get("tariffs") or "data/tariffs"
    return _resolve_path(val, "data/tariffs")


def get_spatial_dir() -> pathlib.Path:
    """Returns the local data/spatial directory (managed in Git LFS)."""
    cfg = load_config()
    val = cfg.get("managed", {}).get("spatial") or "data/spatial"
    return _resolve_path(val, "data/spatial")


def get_releases_dir() -> pathlib.Path:
    """Returns the local data/releases directory (managed in Git LFS)."""
    cfg = load_config()
    val = cfg.get("managed", {}).get("releases") or "data/releases"
    return _resolve_path(val, "data/releases")


def resolve_raw_archive(filename: str, code: str | None = None) -> pathlib.Path | None:
    """
    Searches for a raw archive filename across possible Google Drive subdirectories and local raw dirs.
    """
    sui_dir = get_raw_sui_dir()
    candidates = [
        sui_dir / filename,
        sui_dir / "via_a_moderno_creg015" / filename,
        sui_dir / "via_b_historico_creg097" / filename,
        sui_dir / "via_b_historico_creg097" / "formato1_438" / filename,
        sui_dir / "via_b_historico_creg097" / "formato2_439" / filename,
        REPO_ROOT / "data" / "raw" / "sui" / filename,
    ]
    # Check years subfolders in formato2
    for year in ("2018", "2019", "2020"):
        candidates.append(sui_dir / "via_b_historico_creg097" / "formato2_439" / year / filename)

    for cand in candidates:
        if cand.exists():
            return cand

    # Recursive search within sui_dir if it exists
    if sui_dir.exists():
        matches = list(sui_dir.rglob(filename))
        if matches:
            return matches[0]

    return None
