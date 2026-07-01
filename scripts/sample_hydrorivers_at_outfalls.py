#!/usr/bin/env python3
"""Nearest HydroRIVERS reach attributes for each outfall — memory-bounded (tiled).

Notebook 02 loaded the entire 1.5 GB HydroRIVERS geodatabase into memory and reprojected
it, which OOMs on <8 GB machines. This does the identical nearest-reach join but reads
reaches in bbox tiles (via pyogrio), so peak memory stays small. Output feeds notebook 02
as a pre-extracted CSV, mirroring how VIIRS/MERIT are already handled.

Output columns match what notebook 02 cell 5 consumes:
  lon, lat, HYRIV_ID, DIS_AV_CMS, UPLAND_SKM, CATCH_SKM, ORD_STRA, LENGTH_KM, ENDORHEIC,
  dist_to_reach_m   (rows in the SAME order as the Meijer outfalls shapefile)

Run:  .river-env/bin/python scripts/sample_hydrorivers_at_outfalls.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

ROOT = Path(__file__).resolve().parent.parent
GDB = ROOT / "data/raw/hydrorivers/HydroRIVERS_v10.gdb"
LAYER = "HydroRIVERS_v10"
OUT = ROOT / "data/processed/hydrorivers_at_outfalls.csv"

ATTRS = ["HYRIV_ID", "LENGTH_KM", "UPLAND_SKM", "CATCH_SKM",
         "DIS_AV_CMS", "ORD_STRA", "ENDORHEIC"]
TILE = 15.0      # degrees
MARGIN = 0.25    # degrees (~27 km) > max_distance so the true nearest reach is in-bbox
MAX_DIST_M = 20000


def main() -> None:
    shp = gpd.read_file(ROOT / "data/raw/meijer2021/Meijer2021_midpoint_emissions.shp").to_crs(4326)
    lon = shp.geometry.x.values
    lat = shp.geometry.y.values
    n = len(shp)
    print(f"outfalls: {n:,}")

    # result columns, filled by oid (= shapefile row order)
    res = {c: np.full(n, np.nan, dtype=float) for c in ATTRS}
    res_dist = np.full(n, np.nan, dtype=float)

    tx = np.floor(lon / TILE).astype(int)
    ty = np.floor(lat / TILE).astype(int)
    tiles = pd.DataFrame({"oid": np.arange(n), "tx": tx, "ty": ty})

    groups = list(tiles.groupby(["tx", "ty"]))
    print(f"tiles with outfalls: {len(groups)}")
    for k, ((gx, gy), grp) in enumerate(groups):
        bbox = (gx * TILE - MARGIN, gy * TILE - MARGIN,
                (gx + 1) * TILE + MARGIN, (gy + 1) * TILE + MARGIN)
        try:
            hr = gpd.read_file(GDB, layer=LAYER, bbox=bbox, columns=ATTRS)
        except Exception as e:  # noqa: BLE001
            print(f"  tile {gx},{gy}: read failed ({e}); {len(grp)} outfalls unmatched")
            continue
        if len(hr) == 0:
            continue
        hr = hr.to_crs(3857)
        oids = grp["oid"].values
        pts = gpd.GeoDataFrame(
            {"oid": oids},
            geometry=[Point(lon[o], lat[o]) for o in oids],
            crs="EPSG:4326",
        ).to_crs(3857)
        j = gpd.sjoin_nearest(pts, hr, how="left", max_distance=MAX_DIST_M,
                              distance_col="dist_to_reach_m")
        j = j[~j["oid"].duplicated(keep="first")]
        for _, row in j.iterrows():
            o = int(row["oid"])
            if pd.notna(row.get("HYRIV_ID")):
                for c in ATTRS:
                    res[c][o] = row[c]
                res_dist[o] = row["dist_to_reach_m"]
        if (k + 1) % 20 == 0:
            done = np.isfinite(res["HYRIV_ID"]).sum()
            print(f"  {k+1}/{len(groups)} tiles | matched so far: {done:,}")

    out = pd.DataFrame({"lon": lon, "lat": lat, **{c: res[c] for c in ATTRS},
                        "dist_to_reach_m": res_dist})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(OUT, index=False)
    matched = np.isfinite(res["HYRIV_ID"]).sum()
    print(f"\nmatched {matched:,}/{n:,} ({100*matched/n:.1f}%) -> {OUT}")


if __name__ == "__main__":
    main()
