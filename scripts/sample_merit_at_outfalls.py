#!/usr/bin/env python3
"""Sample MERIT .tif tiles at outfall locations and write CSV with elv/slp/upa values.

Usage:
  python scripts/sample_merit_at_outfalls.py \
    --merit-dir data/raw/merit_15s_filtered/15s \
    --outfalls river_outfalls.csv \
    --out csv/merit_extracted.csv

The script searches for .tif files under `--merit-dir/{var}/` for var in elv,slp,upa.
It will sample each tile only for outfalls that fall within the tile bounds.
"""
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
import rasterio


def sample_var(var_dir, coords_df):
    values = np.full(len(coords_df), np.nan)
    tif_files = sorted(Path(var_dir).glob('*.tif'))
    print(f"{var_dir.name}: found {len(tif_files)} .tif files")
    for tif in tif_files:
        try:
            with rasterio.open(tif) as src:
                bounds = src.bounds
                mask = (
                    (coords_df['lon'] >= bounds.left) & (coords_df['lon'] <= bounds.right) &
                    (coords_df['lat'] >= bounds.bottom) & (coords_df['lat'] <= bounds.top)
                )
                if mask.sum() == 0:
                    continue
                coords = list(zip(coords_df.loc[mask, 'lon'], coords_df.loc[mask, 'lat']))
                sampled = list(src.sample(coords))
                for idx, val in zip(coords_df.index[mask], sampled):
                    v = val[0]
                    if src.nodata is None or v != src.nodata:
                        values[idx] = v
        except Exception as e:
            print(f"Failed to read {tif}: {e}")
    return values


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--merit-dir', required=True, help='Path to directory containing 15s/elv, 15s/slp, 15s/upa')
    p.add_argument('--outfalls', required=True, help='CSV with lon,lat columns (river_outfalls.csv)')
    p.add_argument('--out', required=True, help='Output CSV path')
    args = p.parse_args()

    merit_dir = Path(args.merit_dir)
    outfalls = Path(args.outfalls)
    out_csv = Path(args.out)

    df = pd.read_csv(outfalls)
    if not {'lon','lat'}.issubset(df.columns):
        raise SystemExit('Outfalls CSV must contain lon and lat columns')

    results = {}
    for var in ['elv','slp','upa']:
        var_dir = merit_dir / var
        if not var_dir.exists():
            print(f"Warning: {var_dir} does not exist — skipping {var}")
            results[var] = np.full(len(df), np.nan)
            continue
        results[var] = sample_var(var_dir, df)

    out = pd.DataFrame({
        'lon': df['lon'],
        'lat': df['lat'],
        'elevation_m': results['elv'],
        'slope_pct': results['slp'],
        'upstream_area_km2_merit': results['upa'],
    })
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(out_csv, index=False)
    print(f"Saved sampled values to {out_csv}")
