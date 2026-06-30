#!/usr/bin/env python3
"""Derive MERIT slope (.tif) from extracted elevation tiles.

If you have extracted MERIT 15s elevation tiles but not slope tiles, this script
computes a local slope percent map from the elevation raster and writes the
results to a new slp directory.
"""
import argparse
from pathlib import Path
import numpy as np
import rasterio


def compute_slope_percent(elevation, transform, nodata=None):
    elevation = elevation.astype(np.float64)
    if nodata is not None:
        mask = elevation == nodata
        elevation = elevation.astype(np.float64)
        elevation[mask] = np.nan
    else:
        mask = np.isnan(elevation)

    h, w = elevation.shape
    if h < 2 or w < 2:
        return np.full_like(elevation, np.nan, dtype=np.float32)

    # Pixel size in degrees
    dx_deg = abs(transform.a)
    dy_deg = abs(transform.e)

    # Latitude of each row center
    lats = transform.f + (np.arange(h) + 0.5) * transform.e
    # Convert degrees to meters
    lon_meters_per_deg = 111320.0 * np.cos(np.deg2rad(lats))
    dy_m = dy_deg * 111132.0

    dzdy = np.empty_like(elevation)
    dzdx = np.empty_like(elevation)

    dzdy[1:-1, :] = (elevation[:-2, :] - elevation[2:, :]) / (2.0 * dy_m)
    dzdy[0, :] = (elevation[0, :] - elevation[1, :]) / dy_m
    dzdy[-1, :] = (elevation[-2, :] - elevation[-1, :]) / dy_m

    dx_m = dx_deg * lon_meters_per_deg
    dzdx[:, 1:-1] = (elevation[:, 2:] - elevation[:, :-2]) / (2.0 * dx_m[:, None])
    dzdx[:, 0] = (elevation[:, 1] - elevation[:, 0]) / dx_m[:, None]
    dzdx[:, -1] = (elevation[:, -1] - elevation[:, -2]) / dx_m[:, None]

    slope_pct = 100.0 * np.hypot(dzdx, dzdy)
    slope_pct[mask] = np.nan
    return slope_pct.astype(np.float32)


def process_tile(src_path, dst_path):
    with rasterio.open(src_path) as src:
        profile = src.profile.copy()
        profile.update(dtype='float32', count=1, nodata=np.nan)
        elevation = src.read(1)
        slope = compute_slope_percent(elevation, src.transform, nodata=src.nodatavals[0])

    dst_path.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(dst_path, 'w', **profile) as dst:
        dst.write(slope, 1)


def main():
    parser = argparse.ArgumentParser(description='Derive MERIT slp tiles from elv tiles.')
    parser.add_argument('--elv-dir', required=True, help='Directory containing MERIT elv .tif tiles')
    parser.add_argument('--out-dir', required=True, help='Directory to write MERIT slp .tif tiles')
    args = parser.parse_args()

    elv_dir = Path(args.elv_dir)
    out_dir = Path(args.out_dir)

    tif_paths = sorted(elv_dir.glob('*.tif'))
    if not tif_paths:
        raise SystemExit(f'No .tif files found in {elv_dir}')

    print(f'Found {len(tif_paths)} elevation tiles in {elv_dir}')
    for src_path in tif_paths:
        dst_path = out_dir / src_path.name
        print(f'Processing {src_path.name} -> {dst_path}')
        process_tile(src_path, dst_path)

    print(f'Derived slope tiles written to {out_dir}')


if __name__ == '__main__':
    main()
