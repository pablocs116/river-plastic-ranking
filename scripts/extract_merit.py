#!/usr/bin/env python3
"""
MERIT Hydro extraction with nearest-valid-pixel sampling and slope computation.

Usage:
    conda activate riverplastic  (or any env with rasterio, scipy, pandas, numpy)
    python extract_merit.py /path/to/merit_hydro/15s

Arguments:
    MERIT_DIR: root directory containing elv/, upa/ subdirs with .tif tiles

What it does:
    1. Computes slope from elevation tiles using gdaldem (writes to slp/)
    2. Samples elv, slp, upa at 31,819 river outfall locations
    3. Uses nearest-valid-pixel search (up to ~5km / 50 pixels) for coastal outfalls
    4. Saves merit_extracted.csv to data/processed/
"""

import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from rasterio.errors import RasterioIOError

MERIT_DIR = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/raw/merit_15s_filtered/15s")
OUTFALLS_CSV = Path("river_outfalls.csv")
OUTPUT_CSV = Path("data/processed/merit_extracted.csv")

ELV_DIR = MERIT_DIR / "elv"
SLP_DIR = MERIT_DIR / "slp"
UPA_DIR = MERIT_DIR / "upa"

SEARCH_RADIUS_PX = 50  # ~5km at 15s resolution


def compute_slope_tiles():
    if SLP_DIR.exists() and any(SLP_DIR.glob("*.tif")):
        print(f"Slope tiles already exist in {SLP_DIR}, skipping gdaldem")
        return

    SLP_DIR.mkdir(parents=True, exist_ok=True)

    all_elv_tiles = sorted(ELV_DIR.glob("*.tif"))
    invalid_elv = [tif for tif in all_elv_tiles if tif.stat().st_size == 0]
    if invalid_elv:
        print(f"Warning: skipping {len(invalid_elv)} empty elv tile(s):")
        for tif in invalid_elv:
            print(f"  {tif.name}")

    elv_tiles = [tif for tif in all_elv_tiles if tif.stat().st_size > 0]
    print(f"Computing slope from {len(elv_tiles)} elevation tiles...")

    for i, tif in enumerate(elv_tiles):
        out = SLP_DIR / tif.name
        if out.exists():
            continue
        try:
            subprocess.run(
                ["gdaldem", "slope", str(tif), str(out), "-p"],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"  gdaldem failed for {tif.name}: {e.stderr.decode()[:200]}")
            continue
        if (i + 1) % 10 == 0:
            print(f"  {i+1}/{len(elv_tiles)} done")

    print(f"Slope tiles written to {SLP_DIR}")


def sample_nearest_valid(src, lons, lats, search_radius=SEARCH_RADIUS_PX):
    values = np.full(len(lons), np.nan)

    for i in range(len(lons)):
        try:
            row, col = src.index(lons[i], lats[i])
        except (ValueError, IndexError):
            continue

        h, w = src.height, src.width

        if 0 <= row < h and 0 <= col < w:
            window = src.read(1, window=rasterio.windows.Window(
                max(0, col - search_radius),
                max(0, row - search_radius),
                min(2 * search_radius + 1, w - max(0, col - search_radius)),
                min(2 * search_radius + 1, h - max(0, row - search_radius)),
            ))

            nodata = src.nodata if src.nodata is not None else -9999
            valid_mask = (window != nodata) & np.isfinite(window)

            if valid_mask.any():
                if window.shape[0] > 0 and window.shape[1] > 0:
                    local_row = min(row, h - 1) - max(0, row - search_radius)
                    local_col = min(col, w - 1) - max(0, col - search_radius)

                    if 0 <= local_row < window.shape[0] and 0 <= local_col < window.shape[1]:
                        if valid_mask[local_row, local_col]:
                            values[i] = window[local_row, local_col]
                            continue

                    r_idx, c_idx = np.indices(window.shape)
                    dist = np.sqrt((r_idx - local_row) ** 2 + (c_idx - local_col) ** 2)
                    dist[~valid_mask] = np.inf
                    nearest_idx = np.unravel_index(np.argmin(dist), window.shape)
                    if dist[nearest_idx] <= search_radius:
                        values[i] = window[nearest_idx]

    return values


def extract_variable(var_name, var_dir, df):
    tif_files = sorted(var_dir.glob("*.tif"))
    print(f"\nExtracting {var_name}: {len(tif_files)} tiles")
    values = np.full(len(df), np.nan)

    for tif in tif_files:
        if tif.stat().st_size == 0:
            print(f"  skipping empty {tif.name}")
            continue
        try:
            with rasterio.open(tif) as src:
                bounds = src.bounds
                mask = (
                    (df["lon"].values >= bounds.left - 1)
                    & (df["lon"].values <= bounds.right + 1)
                    & (df["lat"].values >= bounds.bottom - 1)
                    & (df["lat"].values <= bounds.top + 1)
                )
                if mask.sum() == 0:
                    continue

                idx = np.where(mask)[0]
                sampled = sample_nearest_valid(
                    src, df["lon"].values[idx], df["lat"].values[idx]
                )
                for j, ii in enumerate(idx):
                    if np.isfinite(sampled[j]):
                        values[ii] = sampled[j]
        except RasterioIOError as e:
            print(f"  skipping unreadable {tif.name}: {e}")
            continue

    valid = np.isfinite(values)
    print(f"  Valid: {valid.sum():,}/{len(df)} ({valid.mean()*100:.1f}%)")
    if valid.sum() > 0:
        print(f"  Range: [{np.nanmin(values):.2f}, {np.nanmax(values):.2f}]")
    return values


def main():
    df = pd.read_csv(OUTFALLS_CSV)
    print(f"Outfalls: {len(df):,}")

    compute_slope_tiles()

    results = {}
    for var_name, var_dir in [("elv", ELV_DIR), ("slp", SLP_DIR), ("upa", UPA_DIR)]:
        if not var_dir.exists() or not any(var_dir.glob("*.tif")):
            print(f"WARNING: {var_dir} not found or empty, skipping {var_name}")
            results[var_name] = np.full(len(df), np.nan)
            continue
        results[var_name] = extract_variable(var_name, var_dir, df)

    out = pd.DataFrame({
        "lon": df["lon"],
        "lat": df["lat"],
        "elevation_m": results["elv"],
        "slope_pct": results["slp"],
        "upstream_area_km2_merit": results["upa"],
    })

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUTPUT_CSV, index=False)
    print(f"\nSaved {len(out):,} rows to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
