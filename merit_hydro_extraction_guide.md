# MERIT Hydro Data Extraction Guide

## What We Need

We need to extract **3 variables** from MERIT Hydro at **31,819 river outfall locations** (point sampling, not catchment averaging). Two of these are 100% missing in our current feature matrix — this is the primary motivation.

| Variable | MERIT Product | Layer | Current Status | Priority |
|---|---|---|---|---|
| Elevation (m) | MERIT Hydro | `elv` | 100% missing (31,819) | **HIGH** |
| Slope (%) | MERIT Hydro | `slp` | 100% missing (31,819) | **HIGH** |
| Flow accumulation | MERIT Hydro | `upa` (upstream drainage area) | Partially missing (27) | **MEDIUM** |

**We do NOT need:** `dir` (flow direction), `wth` (river width), `cnt` (flow accumulation count).

## Resolution

- **Use 15 arc-second (~500m) tiles** — sufficient for point extraction at outfall locations
- **Do NOT download the 3 arc-second (~90m) tiles** — 9x more data, no benefit for point sampling
- MERIT Hydro 15s tiles are available at: `http://hydro.iis.u-tokyo.ac.jp/~yamadai/MERIT_Hydro/`

## Tile Selection

Our rivers span lat [-54.88, 59.80] and lon [-135.33, 179.95]. That means we need all tiles between lat -60 to +60 and lon -150 to +180. The tile naming convention is:

```
15s/  {variable}/  {variable}{lat}{lon}.tar
```

Where `lat` is formatted as `n00`-`n90` or `s00`-`s90` and `lon` as `e000`-`e180` or `w000`-`w180`.

**Tiles needed** (each is 30° × 30°):

| Latitude band | Longitude bands needed | Rivers in band |
|---|---|---|
| s30–s60 | e000–e030, e030–e060 | 714 |
| s00–s30 | w150–w120, w120–w090, w090–w060, w060–w030, w030–w000, e000–e030, e030–e060, e060–e090, e090–e120, e120–e150, e150–e180 | 8,186 |
| n00–n30 | w150–w120, w120–w090, w090–w060, w060–w030, w030–w000, e000–e030, e030–e060, e060–e090, e090–e120, e120–e150, e150–e180 | 17,406 |
| n30–n60 | w150–w120, w120–w090, w090–w060, w060–w030, w030–w000, e000–e030, e030–e060, e060–e090, e090–e120, e120–e150, e150–e180 | 5,513 |

**Total tiles: ~3 variables × ~40 tiles = ~120 .tar files.** Each 15s tile is ~50-100 MB uncompressed. Total download ~5-10 GB (not 200 GB).

## Extraction Script

Once the tiles are downloaded and extracted, run this Python script to sample values at the 31,819 outfall locations:

```python
import rasterio
import pandas as pd
import numpy as np
from pathlib import Path

# CONFIG — adjust these paths
MERIT_DIR = Path("/path/to/merit_hydro/15s")  # root dir with elv/, slp/, upa/ subdirs
OUTFALLS_CSV = Path("/path/to/river_outfalls.csv")  # lon, lat columns
OUTPUT_CSV = Path("/path/to/merit_extracted.csv")

# Load outfall coordinates
df = pd.read_csv(OUTFALLS_CSV)
print(f"Outfalls: {len(df):,}")

# For each variable, open all tiles and sample
results = {}
for var in ["elv", "slp", "upa"]:
    var_dir = MERIT_DIR / var
    values = np.full(len(df), np.nan)

    # Collect all .tif files for this variable
    tif_files = sorted(var_dir.glob("*.tif"))
    print(f"\n{var}: {len(tif_files)} tiles found")

    for tif in tif_files:
        with rasterio.open(tif) as src:
            # Get tile bounds
            bounds = src.bounds
            # Select points within this tile
            mask = (
                (df["lon"] >= bounds.left) & (df["lon"] <= bounds.right) &
                (df["lat"] >= bounds.bottom) & (df["lat"] <= bounds.top)
            )
            if mask.sum() == 0:
                continue

            # Sample at point locations
            coords = list(zip(df.loc[mask, "lon"], df.loc[mask, "lat"]))
            sampled = list(src.sample(coords))
            for i, (idx, val) in enumerate(zip(df.index[mask], sampled)):
                v = val[0]
                if src.nodata is None or v != src.nodata:
                    values[idx] = v

    results[var] = values
    valid = np.isfinite(values)
    print(f"  Valid: {valid.sum():,}/{len(df)}")
    print(f"  Range: [{np.nanmin(values):.1f}, {np.nanmax(values):.1f}]")

# Save
out = pd.DataFrame({
    "lon": df["lon"],
    "lat": df["lat"],
    "elevation_m": results["elv"],
    "slope_pct": results["slp"],
    "upstream_area_km2_merit": results["upa"],
})
out.to_csv(OUTPUT_CSV, index=False)
print(f"\nSaved to {OUTPUT_CSV}")
```

## Outfall Coordinates File

Generate this on the current PC and transfer:

```python
import pandas as pd
fm = pd.read_csv("data/processed/feature_matrix_v1.csv")
fm[["lon", "lat"]].to_csv("river_outfalls.csv", index=False)
```

## Alternative: Pre-filtered Extraction

If bandwidth/storage is constrained, you can extract ONLY the tiles that contain outfalls. Here's how to determine which tiles are needed:

```python
import pandas as pd
fm = pd.read_csv("data/processed/feature_matrix_v1.csv")
# MERIT 15s tiles are 30x30 degrees
def tile_name(lat, lon):
    ns = "n" if lat >= 0 else "s"
    ew = "e" if lon >= 0 else "w"
    t_lat = abs(int(lat // 30) * 30)
    t_lon = abs(int(lon // 30) * 30)
    return f"{ns}{t_lat:02d}{ew}{t_lon:03d}"

tiles = set()
for _, row in fm.iterrows():
    tiles.add(tile_name(row["lat"], row["lon"]))

print(f"Unique tiles needed: {len(tiles)}")
for t in sorted(tiles):
    print(f"  {t}")
```

This should print ~40 tile names. You only need to download these tiles for `elv`, `slp`, and `upa`.

## Expected Output Format

A CSV with 31,819 rows and columns: `lon, lat, elevation_m, slope_pct, upstream_area_km2_merit`

Transfer this single CSV back to the main project PC. Expected size: ~2 MB.

## Why These Variables Matter

1. **Elevation + Slope**: Critical for P(R) — the river transport probability in Meijer's model. Currently 100% missing, so our model can't diagnose slope-related overestimation. Also needed for the paper's discussion of terrain controls.

2. **Upstream area (upa)**: Independent validation of our existing `UPLAND_SKM` from HydroRIVERS. MERIT Hydro's flow accumulation is derived from a higher-quality DEM and may differ from HydroRIVERS at small catchments.

## License Note

MERIT Hydro is CC-BY-NC 4.0 — non-commercial use only. This is fine for academic research but must be noted in the paper.
