"""
Download ERA5-Land monthly mean runoff from CDS.
Requires: pip install cdsapi
Credentials: add to .env as CDS_KEY=UID:API-KEY
  or create ~/.cdsapirc with:
    url: https://cds.climate.copernicus.eu/api/v2
    key: UID:API-KEY

IMPORTANT: You must accept the ERA5-Land licence on the CDS website
before the API will work: https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-land
"""

import os
from pathlib import Path

import cdsapi
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
ERA5_DIR = DATA_RAW / "era5"

YEARS = [str(y) for y in range(2015, 2026)]
MONTHS = [f"{m:02d}" for m in range(1, 13)]


def download_era5_runoff():
    print("=== ERA5-Land Monthly Mean Runoff ===")
    print(f"  Period: 2015-2025")
    print(f"  Output: {ERA5_DIR / 'era5_land_monthly_runoff_2015_2025.nc'}")
    print(f"  Size: ~15-20 GB (queued, may take several hours)\n")

    ERA5_DIR.mkdir(parents=True, exist_ok=True)
    out_file = ERA5_DIR / "era5_land_monthly_runoff_2015_2025.nc"

    if out_file.exists():
        print(f"  [skip] {out_file.name} already exists")
        return

    c = cdsapi.Client()

    c.retrieve(
        "reanalysis-era5-land-monthly-means",
        {
            "product_type": ["monthly_averaged_reanalysis"],
            "variable": ["runoff", "sub_surface_runoff", "surface_runoff"],
            "year": [str(y) for y in range(2015, 2027)],
            "month": [f"{m:02d}" for m in range(1, 13)],
            "time": ["00:00"],
            "data_format": "netcdf",
            "download_format": "unarchived",
        },
        str(out_file),
    )
    print("  Done.")


if __name__ == "__main__":
    download_era5_runoff()
