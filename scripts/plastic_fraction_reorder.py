#!/usr/bin/env python3
"""Reproduce the plastic-fraction reordering — the short-paper's core result.

This is the lightweight, low-memory path to the headline table: it does NOT need the
full feature matrix, HydroRIVERS (1.5 GB, OOMs on <8 GB RAM), or the rasters. It applies
notebook 08's `E_corrected` step directly to the recovered inputs:

    HI-mismanagement fix: mismanaged_pct == 50 & high-income country -> x 3/50
    plastic_ratio       = country plastic_pct / 12          (Meijer's constant 12%)
    E_corrected         = meijer_ton_yr * plastic_ratio

Country assignment: spatial join of outfalls to Natural Earth 110m countries
(nearest for coastal points). Downloaded once to data/raw/ne_110m_admin_0_countries/.

NOT included (immaterial for the top-20, all of which are coastal):
  - endorheic zeroing (~45 inland rivers; needs HydroRIVERS ENDORHEIC field)
  - the nightlight calibration layer (E_final); that is a separate step.

Inputs  (recovered from Zenodo 10.5281/zenodo.20793131):
  data/processed/recalibrated_emissions_v1.csv   (meijer_ton_yr, lat, lon)
  data/raw/worldbank_waste/what_a_waste_3.0_processed.csv
Output:
  data/processed/plastic_fraction_reordering.csv

Run with the project venv:  .river-env/bin/python scripts/plastic_fraction_reorder.py
"""
import io
import zipfile
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

ROOT = Path(__file__).resolve().parent.parent
NE_URL = "https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip"

# High-income countries whose WaW default 50% mismanaged rate is implausible (notebook 08).
HIGH_INCOME = {
    "USA", "GBR", "ITA", "CAN", "AUS", "FRA", "DEU", "ESP", "NLD", "BEL", "AUT", "CHE",
    "SWE", "NOR", "DNK", "FIN", "IRL", "NZL", "PRT", "GRC", "CZE", "KOR", "SGP", "TWN",
    "ISR", "SAU", "UAE", "QAT", "KWT", "BHR", "OMN",
}


def load_countries() -> gpd.GeoDataFrame:
    ne_dir = ROOT / "data/raw/ne_110m_admin_0_countries"
    shp = list(ne_dir.glob("*.shp"))
    if not shp:
        print("downloading Natural Earth 110m countries...")
        data = urllib.request.urlopen(NE_URL, timeout=60).read()
        ne_dir.mkdir(parents=True, exist_ok=True)
        zipfile.ZipFile(io.BytesIO(data)).extractall(ne_dir)
        shp = list(ne_dir.glob("*.shp"))
    return gpd.read_file(shp[0])[["ADM0_A3", "geometry"]].rename(columns={"ADM0_A3": "iso3"})


def main() -> None:
    cal = pd.read_csv(ROOT / "data/processed/recalibrated_emissions_v1.csv")
    waw = pd.read_csv(ROOT / "data/raw/worldbank_waste/what_a_waste_3.0_processed.csv")
    waw = waw[waw["iso3"] != "iso3c"].copy()
    waw["plastic_pct"] = pd.to_numeric(waw["plastic_pct"], errors="coerce")
    waw["mismanaged_pct"] = pd.to_numeric(waw["mismanaged_pct"], errors="coerce")
    print(f"outfalls: {len(cal):,} | WaW countries: {len(waw)}")

    # Country assignment. Both frames are EPSG:4326; sjoin_nearest only matters for the
    # handful of coastal points that miss every polygon, where degree vs metre distance
    # does not change the nearest country.
    pts = gpd.GeoDataFrame(
        cal.copy(),
        geometry=[Point(xy) for xy in zip(cal["lon"], cal["lat"])],
        crs="EPSG:4326",
    )
    joined = gpd.sjoin_nearest(pts, load_countries(), how="left")
    joined = joined[~joined.index.duplicated(keep="first")].copy()
    print(f"country assigned: {joined['iso3'].notna().sum():,} / {len(joined):,}")

    df = joined.merge(
        waw[["iso3", "plastic_pct", "mismanaged_pct", "income_group"]], on="iso3", how="left"
    )

    # HI-mismanagement fix, then plastic-fraction correction.
    meijer = df["meijer_ton_yr"].astype(float).values.copy()
    hi_mask = (df["mismanaged_pct"] == 50.0) & df["iso3"].isin(HIGH_INCOME)
    meijer[hi_mask.values] *= 3.0 / 50.0

    df["meijer_adj"] = meijer
    df["plastic_ratio"] = (df["plastic_pct"] / 12.0).values
    df["E_corrected"] = df["meijer_adj"] * df["plastic_ratio"]

    valid = df["E_corrected"].notna()
    print(f"\nMeijer total:    {df['meijer_ton_yr'].sum():,.0f} t/yr")
    print(f"Corrected total: {df.loc[valid, 'E_corrected'].sum():,.0f} t/yr "
          f"(where country known, {int(valid.sum()):,} rivers)")

    d = df[valid].copy()
    d["rank_meijer"] = d["meijer_ton_yr"].rank(ascending=False)
    d["rank_corr"] = d["E_corrected"].rank(ascending=False)
    d["rank_change"] = (d["rank_meijer"] - d["rank_corr"]).astype(int)

    cols = ["iso3", "lat", "lon", "meijer_ton_yr", "plastic_pct", "plastic_ratio",
            "E_corrected", "rank_meijer", "rank_corr", "rank_change"]
    out = ROOT / "data/processed/plastic_fraction_reordering.csv"
    d.sort_values("E_corrected", ascending=False)[cols].to_csv(out, index=False)

    top = d.sort_values("E_corrected", ascending=False).head(20)[cols].copy()
    top["meijer_ton_yr"] = top["meijer_ton_yr"].round(0)
    top["E_corrected"] = top["E_corrected"].round(0)
    top["plastic_ratio"] = top["plastic_ratio"].round(2)
    pd.set_option("display.width", 200, "display.max_columns", 20)
    print("\n=== TOP 20 by corrected emission (plastic-fraction reordering) ===")
    print(top.to_string(index=False))
    print(f"\nsaved -> {out}")


if __name__ == "__main__":
    main()
