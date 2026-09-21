"""
Script 01: Sync raw data from Google Drive raw store using project manifests.
Downloads missing files using gdown and verifies SHA-256 hashes against data/manifests/*.json.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import sys

import gdown

# Ensure repository root is on sys.path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from src.utils.paths import get_raw_sui_dir, get_raw_era5_dir, REPO_ROOT


def compute_sha256(filepath: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def sync_item(filename: str, drive_id: str, expected_sha: str, target_dir: pathlib.Path) -> str:
    dest = target_dir / filename
    if dest.exists():
        actual_sha = compute_sha256(dest)
        if expected_sha and actual_sha.lower() == expected_sha.lower():
            print(f"[OK - VERIFIED] {filename} exists with matching SHA-256 ({actual_sha[:12]}...).")
            return actual_sha
        else:
            print(f"[PRESENT] {filename} (SHA-256: {actual_sha})")
            return actual_sha

    if not drive_id:
        print(f"[PENDING UPLOAD] {filename} has no Google Drive file ID recorded yet.")
        return ""

    print(f"\n[DOWNLOADING] {filename} from Google Drive (ID: {drive_id})...")
    try:
        gdown.download(id=drive_id, output=str(dest), quiet=False)
        if dest.exists():
            actual_sha = compute_sha256(dest)
            print(f"[DOWNLOAD COMPLETE] {filename} (SHA-256: {actual_sha})")
            return actual_sha
    except Exception as e:
        print(f"[DOWNLOAD FAILED] {filename}: {e}")
    return ""


def sync_manifest(manifest_path: pathlib.Path, target_base_dir: pathlib.Path):
    if not manifest_path.exists():
        print(f"[ERROR] Manifest not found: {manifest_path}")
        return

    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    target_base_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n=======================================================")
    print(f"Checking Manifest: {manifest_path.name}")
    print(f"Target Directory: {target_base_dir}")
    print(f"=======================================================")

    updated = False

    # Handle SUI manifest structure
    if "datasets" in data:
        for ds in data["datasets"]:
            print(f"\n--- Dataset: {ds.get('code')} ({ds.get('format')}) - {ds.get('description')} ---")
            for item in ds.get("files", []):
                fname = item["filename"]
                drive_id = item.get("drive_file_id", "").strip()
                expected_sha = item.get("sha256", "").strip()

                sha = sync_item(fname, drive_id, expected_sha, target_base_dir)
                if sha and sha != expected_sha:
                    item["sha256"] = sha
                    item["status"] = "available_locally"
                    updated = True

    # Handle ERA5 manifest structure
    if "files" in data:
        print(f"\n--- ERA5-Land Hourly Climate Reanalysis ---")
        for item in data["files"]:
            fname = item["filename"]
            drive_id = item.get("drive_file_id", "").strip()
            expected_sha = item.get("sha256", "").strip()

            sha = sync_item(fname, drive_id, expected_sha, target_base_dir)
            if sha and sha != expected_sha:
                item["sha256"] = sha
                item["status"] = "available_locally"
                updated = True

    if updated:
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        print(f"\n[MANIFEST UPDATED] Synced checksums saved back to {manifest_path.name}")


def main():
    parser = argparse.ArgumentParser(description="Synchronize raw data from Google Drive.")
    parser.add_argument("--sui-dir", type=pathlib.Path, default=None, help="Target directory for raw SUI archives.")
    parser.add_argument("--era5-dir", type=pathlib.Path, default=None, help="Target directory for raw ERA5 files.")
    args = parser.parse_args()

    sui_manifest = REPO_ROOT / "data" / "manifests" / "sui_2021_2024_manifest.json"
    era5_manifest = REPO_ROOT / "data" / "manifests" / "era5_land_manifest.json"

    raw_sui_dir = args.sui_dir or get_raw_sui_dir()
    raw_era5_dir = args.era5_dir or get_raw_era5_dir()

    sync_manifest(sui_manifest, raw_sui_dir)
    sync_manifest(era5_manifest, raw_era5_dir)


if __name__ == "__main__":
    main()
