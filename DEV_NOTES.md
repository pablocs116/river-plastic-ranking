# River Plastic Ranking — Development Notes

## Project Status

Recalibrating Meijer et al. (2021) global river plastic emission model with observed flux data.

**Core result**: Linear calibration slope=0.72 [0.55, 0.88], R²=0.57 (n=64). Models overestimate by ~28% on average.

**Key blocker**: Only 64 calibration rivers (37 Japan, 27 rest-of-world). 0 African, 0 South American.

---

## Publishable Claims

### 1. Models overestimate (slope < 1) — STRONG
- log₁₀(obs) = 0.720 × log₁₀(Meijer) + 0.624, 95% CI on slope: [0.554, 0.881]
- Independently confirmed by Mani et al. (2026): observed fluxes 34-98% lower than models
- Must report sensitivity: with Japan slope=0.720, without Japan slope=0.852

### 2. Episodic transport explains monthly vs annual R² gap — SECONDARY
- Monthly R²=0.73 >> annual R²=0.50-0.57
- Mani Table 1: 50% of annual flux occurs in 7-12% of the year
- Monthly obs capture flushes; annualizing dilutes the signal

### 3. Tidal retention is a known overestimation mechanism — CITE MANI
- Mani: 26-43% of days have zero/reverse flow in tidal estuaries
- This is their finding, not ours — cite as supporting evidence for Claim 1
- DO NOT attribute European overprediction to tidal retention — Besos/Llobregat are microtidal Mediterranean rivers, yet most overpredicted. Likely cause: waste management (Europe <5% mismanaged waste).

## Non-publishable
- European overprediction: n=9, outlier-driven, likely waste management
- Waste data no improvement: null result, insufficient power (ΔR²=0.002, P>0.4)
- Waste-adjusted ranking: no validation

## Must Disclose
- Japan dominates calibration (58%); without Japan slope=0.852, R²=0.678
- Only 27 non-Japanese calibration rivers
- Cannot validate waste data updates or regional differences

---

## Notebooks & Key Files

| Notebook | Description | Status |
|---|---|---|
| 01_baseline_reproduction | Meijer 2021 shapefile, 31,819 rivers | Done |
| 02_feature_engineering | HydroRIVERS, WorldClim, WaW3.0, ERA5-Land, VIIRS → 31,819×43 matrix | Done |
| 03_model_training | XGBoost on Meijer predictions — circular (R²=0.58) | Done (not useful) |
| 04_observed_flux_model | XGBoost failed (R²=-0.03), linear calibration R²=0.57 | Done |
| 05_updated_ranking | Calibrated ranking, waste adjustment exploratory, residual analysis | Done |

| File | Description |
|---|---|
| `data/processed/feature_matrix_v1.csv` | 31,819 × 43 feature matrix |
| `data/processed/observed_flux_matched_S3.csv` | 66 observed rivers (64 unique) |
| `data/processed/final_ranking_all_rivers.csv` | Calibrated + waste-adjusted ranking |
| `data/processed/final_top1000_ranking.csv` | Top 1000 |
| `data/processed/meijer_calibration_model.pkl` | Linear calibration (slope=0.72) |
| `scripts/build_observed_flux_s3.py` | Table S3 extraction from Meijer PDF |
| `src/models/baseline.py` | Meijer Run 5 reimplemention |
| `data/raw/mani2026_S1_RMS.xlsx` | Mani camera data (4 sheets) |
| `data/raw/mani2026_S3_Model.xlsx` | Mani model simulations (3 sheets) |

---

## Data Inventory

| Dataset | Status | Coverage | Location |
|---|---|---|---|
| Meijer 2021 shapefile | Done | 31,819 outfalls | `data/raw/meijer2021/` |
| HydroRIVERS v10 | Done | 31,792/31,819 | `data/raw/hydrorivers/` |
| WorldClim v2.1 precip | Done | 31,819/31,819 | `data/raw/worldclim/` |
| WaW3.0 country xlsx | Done | 20,833/31,819 | `data/raw/worldbank_waste/` |
| ERA5-Land runoff | Done | 19,042/31,819 | `data/raw/era5/` |
| VIIRS VNL v2.1 | Done | 31,710/31,819 | `data/processed/` |
| MERIT Hydro | Blocked | NaN (on other PC) | `data/raw/merit_hydro/` |
| OSM road density | Skipped | — | VIIRS covers similar signal |

---

## What More Data Unblocks

| Blocked? | Improvement | Why |
|---|---|---|
| YES | ML model | n=64 is 2-3× too small for XGBoost |
| YES | Validate waste updates | Can't detect signal with n=64 |
| YES | Regional calibration | 0 African, 0 South American rivers |
| YES | Robust slope estimate | Japan (58%) distorts it |
| PARTLY | Grid-level model | Can build it, but can't validate it |

---

## MERIT Hydro

**Why needed**: Meijer's P(R) and P(O) require per-cell flow path accumulation at ~1km. Catchment-level approximation failed (R²=-0.03, all predictions ~640 ton/yr).

| Tile | Variable | Unlocks |
|---|---|---|
| `upa` | Upstream area | Cross-check for HydroRIVERS |
| `chw` | Channel width | P(O) with width instead of stream order |
| `elv` | Elevation | Slope → real P(R) instead of constant ζ=0.4 |
| `dir` | Flow direction | Cell-by-cell flow path tracing |

**Status**: ~200GB on other PC. Transfer when possible.
**Alternative**: GEE has MERIT Hydro but requires account.

---

## Mani et al. (2026) — Key Findings

"Three rivers to the test" — Rio Ozama (Dominican Republic), Umgeni (South Africa), Chao Phraya (Thailand)
- 196 GPS drifters, 41 cameras, 3 years (2020-2022)
- **Observed fluxes 34-98% lower than global model estimates**
- 50% of annual flux in 7-12% of the year (episodic)
- 26-43% of days have zero/reverse flow (tidal retention)
- Cannot add as calibration points: RMS measures surface daylight-only, not total 24h flux

---

## Next Steps (Priority Order)

1. **Search for more observed flux data** — #1 bottleneck. Target 100+ rivers.
2. **Read Mani main paper** — check if their calibrated total-flux estimates can be calibration points
3. **Transfer MERIT Hydro** — enables grid-level model
4. **Regional calibration** — separate slope per continent (need more data first)
5. **Monte Carlo UQ** — bootstrap already computed (10K slopes)

---

## Meijer Model Parameters (Run 5, R²=0.71)

| Param | Symbol | Value | Role |
|---|---|---|---|
| Precip coeff | α | 1.5E-4 | P(M) = min(P×α, 1) |
| Wind coeff | β | 0.02 | P(M) += min(W×β, 1) |
| Slope threshold | ζ | 0.4 | P(R) = ν × min(ε×S + ζ, η) |
| Slope upper | η | 1.0 | clips slope probability |
| Stream order coeff | θ | 1.0E-4 | P(O) = min(θ×SO + ι, 1) × min(κ×Q + μ, 1) |
| SO lower threshold | ι | 0.999 | minimum SO probability |
| Discharge coeff | κ | 5.0E-8 | scales Q contribution |
| Q lower threshold | μ | 0.99 | minimum discharge probability |
| Landuse coeff | ν | 0.75 | scales landuse roughness |

---

## Technical Gotchas

- ERA5 uses `valid_time` not `time`, variables `ro`/`ssro`/`sro`
- WaW3.0 `plastic_pct` and treatment values are 0-1 fractions, not 0-100
- `naturalearth_lowres` from `gpd.datasets` deprecated; use naciscdn.org direct download
- `sjoin_nearest` can produce duplicates — deduplicate with `~df.index.duplicated(keep="first")`
- Meijer `dots_exten` = annual midpoint emission (tons/yr)
- Meijer R²=0.71 is on MONTHLY obs (52 points from 16 rivers)
- Numpy arrays from `.values` are read-only; use `.values.copy()` before mutation
- pandas Series needs `.values.reshape(-1,1)` not `.reshape(-1,1)` for sklearn
- S3 "year" period values are already monthly; annualize by ×12
