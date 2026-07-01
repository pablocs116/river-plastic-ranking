#!/usr/bin/env python3
"""Sample VIIRS VNL v2.1 nightlight radiance at each outfall.

Produces the pre-extracted intermediate notebook 02 expects
(data/processed/viirs_nightlight_at_outfalls.csv, column `nightlight_intensity`),
in the same row order as the Meijer outfalls shapefile.

The raw VIIRS raster is gzipped (~300 MB) and expands to ~11.6 GB; it is gunzipped once
to data/raw/viirs/ and sampled window-by-window (low memory).

Run:  .river-env/bin/python scripts/sample_viirs_at_outfalls.py
"""
import gzip
import shutil
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio

ROOT = Path(__file__).resolve().parent.parent
GZ = ROOT / "data/raw/viirs/VNL_v21_npp_2021_global_vcmslcfg_c202205302300.median_masked.dat.tif.gz"
OUT = ROOT / "data/processed/viirs_nightlight_at_outfalls.csv"


def main() -> None:
    tif = GZ.with_suffix("")  # drop .gz
    if not tif.exists():
        print("gunzipping VIIRS raster (~11.6 GB uncompressed)...")
        with gzip.open(GZ, "rb") as fi, open(tif, "wb") as fo:
            shutil.copyfileobj(fi, fo, length=1 << 24)

    shp = gpd.read_file(ROOT / "data/raw/meijer2021/Meijer2021_midpoint_emissions.shp").to_crs(4326)
    lon, lat = shp.geometry.x.values, shp.geometry.y.values
    print(f"outfalls: {len(shp):,}")

    with rasterio.open(tif) as src:
        vals = np.array([v[0] for v in src.sample(zip(lon, lat))], dtype=float)
        if src.nodata is not None:
            vals[vals == src.nodata] = np.nan

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame({"lon": lon, "lat": lat, "nightlight_intensity": vals}).to_csv(OUT, index=False)
    print(f"VIIRS: {np.isfinite(vals).sum():,}/{len(vals):,} valid -> {OUT}")


if __name__ == "__main__":
    main()
