"""
Download auxiliary datasets that require manual registration or browser interaction.
This script provides instructions and, where possible, programmatic download helpers.

Datasets:
  - MERIT Hydro v1.0.1 (requires Google Form signup)
  - HydroRIVERS v1.0 (requires free HydroSHEDS account)
  - NASA VIIRS Nighttime Lights (requires NASA Earthdata login)
  - OSM road network (no auth, uses osmnx for targeted extraction)
"""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"


def merit_hydro_instructions():
    print("=" * 60)
    print("MERIT Hydro v1.0.1 — MANUAL DOWNLOAD")
    print("=" * 60)
    print()
    print("1. Fill in the Google Form:")
    print("   https://goo.gl/forms/6VwfnasNjkYm0Wqu2")
    print()
    print("2. You'll receive a Dropbox link by email (usually same day)")
    print()
    print("3. For global analysis, download ALL 30x30 degree tiles for:")
    print("   - upa:  upstream drainage area")
    print("   - chw:  channel width")
    print("   - elv:  elevation")
    print("   - dir:  flow direction")
    print()
    print("4. Save tiles to:")
    print(f"   {DATA_RAW / 'merit_hydro'}")
    print()
    print("Alternatively, use Google Earth Engine (no download):")
    print("  import ee")
    print('  merit = ee.Image("MERIT/Hydro/v1_0_1")')
    print()


def hydrorivers_instructions():
    print("=" * 60)
    print("HydroRIVERS v1.0 — MANUAL DOWNLOAD")
    print("=" * 60)
    print()
    print("1. Register at https://www.hydrosheds.org (free)")
    print()
    print("2. Go to https://www.hydrosheds.org/products/hydrorivers")
    print("   Download the global shapefile (HydroRIVERS_v10_shp.zip)")
    print()
    print("3. Save to:")
    print(f"   {DATA_RAW / 'hydrorivers'}")
    print()


def viirs_instructions():
    print("=" * 60)
    print("NASA VIIRS Nighttime Lights — MANUAL / GEE")
    print("=" * 60)
    print()
    print("Option A: NASA Earthdata (manual)")
    print("  1. Register at https://earthdata.nasa.gov (free)")
    print('  2. Search "VNP46A4" and download annual composites 2015-2023')
    print(f"  3. Save to: {DATA_RAW / 'viirs'}")
    print()
    print("Option B: Google Earth Engine (programmatic, recommended)")
    print("  import ee")
    print('  viirs = ee.ImageCollection("NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG")')
    print()


def download_osm_sample():
    """Download OSM data for a sample region using osmnx (if available)."""
    print("=" * 60)
    print("OSM Road Network — osmnx targeted extraction")
    print("=" * 60)
    print()
    print("For global analysis, download continental extracts from:")
    print("  https://download.geofabrik.de")
    print()
    print("For targeted extraction by country/city, use osmnx:")
    print()
    print("  import osmnx as ox")
    print('  G = ox.graph_from_place("Philippines", network_type="drive")')
    print()
    print(f"Save raw .osm.pbf files to: {DATA_RAW / 'osm'}")
    print()
    print("NOTE: Full global OSM data is ~70 GB.")
    print("      Consider extracting road density per catchment in batches.")
    print()


if __name__ == "__main__":
    merit_hydro_instructions()
    print()
    hydrorivers_instructions()
    print()
    viirs_instructions()
    print()
    download_osm_sample()
