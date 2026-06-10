# River Plastic Ranking — Development Notes

## Project Goal

Re-run Meijer et al. (2021) with updated inputs (WaW 3.0 waste, ERA5-Land precip), calibrate against observations, diagnose structural overestimation, and produce an updated global ranking.

---

## Phase 1: Search (Done)

Established that Meijer overestimates. Linear calibration: slope=0.72 [0.55, 0.88], R²=0.57 (n=64). Confirmed by Mani et al. (2026). Key vulnerability: only 64 calibration rivers, 58% Japanese.

## Phase 2: Diagnose & Improve (Current)

### Key Diagnostics

1. **No single model term explains the overestimation** — Partial correlations of P(O), P(M), log(W×PR) with log(obs/Meijer) are all ~0 when controlling for emission magnitude. Slope < 1 is a *structural* feature of the multiplicative cascade, not a broken parameter.

2. **P(O) retention is nearly inert** — ι=0.999, μ=0.99 → P(O)≈1 for all rivers. Optimizing P(O) params drops ι→0.91, μ→0.90, adds retention, but R²=0.51 (worse than log-log calibration at 0.60). Catchment-level approximation limits parameter optimization.

3. **Plastic fraction is the biggest input error** — Meijer assumed 12% constant. WaW 3.0 ranges 1.6–30% per country. This alone reorders the top 20: Malaysia rises 2x (24% vs 12%), Philippines drops 0.88x (10.5% vs 12%), Cameroon drops 0.28x (3.3% vs 12%).

4. **Nightlight signal survives controlling for mismanagement** — r=-0.35 (p=0.005) with log(obs/Meijer); partial r=-0.34 (p=0.017) controlling for mismanaged_pct. Not just a Japan artifact — developed-country rivers are systematically more overestimated.

5. **Waste data is 9 years newer** — Jambeck (2015) → WaW 3.0 (2024). Precip is 25+ years newer — WorldClim (1970-2000) → ERA5-Land (2015-2025).

### Robustness of Core Claims (Bootstrap, n=2000)

| Claim | P(direction correct) |
|---|---|
| Slope < 1.0 | 100% |
| Top 1000 < 71.8% of total | 100% |
| Rivers for 80% > 1,659 | 100% |
| Exact concentration (46.3%) | 95% CI: [30.8%, 61.3%] |
| Exact rivers for 80% (5,367) | 95% CI: [2,828, 9,679] |

Even in the most conservative scenario (drop Japan, no small-river inflation): top 1000 = 59.3%, rivers for 80% = 2,580.

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

Note: `baseline.py` PARAMS_S9 values (epsilon=0.01, tau=0.005, theta=0.07, iota=0.01, kappa=0.001, mu=0.95) do NOT match Run 5 — they are a separate catchment-level parameterization. The code was never executed end-to-end.

---

## Data Inventory

| Dataset | Vintage | Status | Coverage |
|---|---|---|---|
| Meijer 2021 shapefile | 2021 | Done | 31,819 outfalls |
| HydroRIVERS v10 | — | Done | 31,792/31,819 |
| WorldClim v2.1 precip | 1970-2000 | Done | 31,819/31,819 |
| WaW3.0 country waste | 2024 | Done | 20,833/31,819 (78.4% of emissions) |
| ERA5-Land runoff | 2015-2025 | Done | 19,042/31,819 |
| VIIRS VNL v2.1 | 2021 | Done | 31,710/31,819 |
| MERIT Hydro | — | Blocked | NaN (on other PC) |
| LandScan population | — | Needed | Not downloaded |
| Jambeck 2015 waste | 2015 | Needed | Must download from Science supplementary |

---

## Next Steps

1. Download Jambeck 2015 supplementary data → compute W_new/W_old ratio per country
2. Extract ERA5-Land precipitation per catchment from existing .nc file
3. Download LandScan or GPW population → full waste term computation
4. Build notebook 07: Meijer re-run with updated inputs → new ranking
5. Integrate: updated ranking + calibration + diagnosis → paper

---

## Technical Gotchas

- ERA5 uses `valid_time` not `time`, variables `ro`/`ssro`/`sro`
- WaW3.0 `plastic_pct` and `mismanaged_pct` are percentages (0-100) in feature matrix; `mpw_kg_cap_day = waste × (plastic/100) × (mismanaged/100)`
- `naturalearth_lowres` deprecated; use naciscdn.org direct download
- `sjoin_nearest` can produce duplicates — deduplicate with `~df.index.duplicated(keep="first")`
- Meijer `dots_exten` = annual midpoint emission (tons/yr)
- Meijer R²=0.71 is on MONTHLY obs (52 points from 16 rivers)
- Numpy arrays from `.values` are read-only; use `.values.copy()` before mutation
- pandas Series needs `.values.reshape(-1,1)` not `.reshape(-1,1)` for sklearn
