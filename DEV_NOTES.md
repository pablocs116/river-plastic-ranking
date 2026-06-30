# River Plastic Ranking — Development Notes

## Project Goal

Re-run Meijer et al. (2021) with updated inputs (WaW 3.0 waste, nightlight proxy), calibrate against observations, diagnose structural overestimation, and produce an updated global ranking.

---

## Phase 1: Search (Done)

Established that Meijer overestimates. Linear calibration: slope=0.72 [0.55, 0.88], R²=0.57 (n=64). Confirmed by Mani et al. (2026). Key vulnerability: only 64 calibration rivers, 58% Japanese.

## Phase 2: Diagnose & Improve (Done)

### Key Diagnostics

1. **No single model term explains the overestimation** — Partial correlations of P(O), P(M), log(W×PR) with log(obs/Meijer) are all ~0 when controlling for emission magnitude. Slope < 1 is a *structural* feature of the multiplicative cascade, not a broken parameter.

2. **P(O) retention is nearly inert** — ι=0.999, μ=0.99 → P(O)≈1 for all rivers. Optimizing P(O) params drops ι→0.91, μ→0.90, adds retention, but R²=0.51 (worse than log-log calibration at 0.60). Catchment-level approximation limits parameter optimization.

3. **Plastic fraction is the biggest input error** — Meijer assumed 12% constant. WaW 3.0 ranges 1.6–30% per country. This alone reorders the top 20: Malaysia rises 2x (24% vs 12%), Philippines drops 0.88x (10.5% vs 12%), Cameroon drops 0.28x (3.3% vs 12%).

4. **Nightlight signal survives controlling for mismanagement** — r=-0.35 (p=0.005) with log(obs/Meijer); partial r=-0.34 (p=0.017) controlling for mismanaged_pct. Not just a Japan artifact — developed-country rivers are systematically more overestimated.

5. **Waste data is 9 years newer** — Jambeck (2015) → WaW 3.0 (2024). Precip update (WorldClim → ERA5-Land) adds no new information (r=0.74, no climate trend 2015-2025, p=0.26).

### Data Quality Fixes

| Fix | Rivers | Impact | Physical basis |
|---|---|---|---|
| Endorheic → zero | 45 | Remove inland drainage | Cannot emit to ocean |
| High-income mismanaged 50%→3% | 2,147 | Reduces HI emissions ~17x | USA/UK/Italy etc. don't have 50% mismanagement |
| Nearest-country spatial join | 9,042 | Enables plastic correction for 82% of unmatched | Coastal outfalls missed country polygons |

Country coverage: 65.5% → 93.9% after fixes.

---

## Phase 3: Improved Model (Done — Notebook 08)

### Correction Pipeline

1. **Data quality fixes** (endorheic, mismanagement defaults, country assignment)
2. **Plastic fraction correction**: Replace Meijer's 12% with WaW 3.0 country-specific values
3. **Observational calibration with nightlight**: log₁₀(obs) = 0.540 + 0.761 × log₁₀(E) − 0.008 × ΔNL

### Nightlight-Adjusted Waste

Within-country nightlight deviation (ΔNL = river NL − country mean NL) captures waste management quality:
- Spearman ρ = −0.38 (p=0.006) with log(obs/Meijer residual)
- Urban rivers (high NL) have 1.2x lower emission per 10 NL units above country mean
- Adds ΔR² = +0.019 over log-log calibration alone (0.589 → 0.608)
- Physical mechanism: better waste collection in urban areas reduces effective mismanaged_pct

### Final Results

| Model | Total (ton/yr) | Top 100 | Top 1000 | n80 |
|---|---|---|---|---|
| Meijer (2021) | 1,005,984 | 34.4% | 71.8% | 1,659 |
| **This work (full)** | **889,196** | **16.4%** | **50.7%** | **4,407** |
| Without Japan | 668,824 | — | 68.0% | 1,991 |

### Bootstrap Uncertainty (n=2000)

| Metric | Median | 95% CI |
|---|---|---|
| Top 1000 concentration | 51.1% | [36.3%, 66.2%] |
| Rivers for 80% | 4,341 | [2,184, 7,731] |
| P(top1000 < 71.8%) | 99.8% | — |
| P(n80 > 1,659) | 99.8% | — |

### Top 5 Updated Ranking

| # | Country | Lat | Lon | Meijer (ton/yr) | Updated (ton/yr) | Ratio |
|---|---|---|---|---|---|---|
| 1 | MYS | 3.0 | 101.4 | 12,816 | 5,952 | 0.46 |
| 2 | IND | 19.3 | 72.9 | 13,433 | 5,713 | 0.43 |
| 3 | PHL | 14.6 | 121.0 | 62,592 | 5,636 | 0.09 |
| 4 | PHL | 14.7 | 120.9 | 12,398 | 4,092 | 0.33 |
| 5 | BGD | 23.2 | 90.6 | 6,222 | 3,582 | 0.58 |

### Japan Sensitivity

Without Japan (n=27): slope=0.977, R²=0.756. Total=668,824, top1000=68.0%, n80=1,991. Direction holds but concentration is weaker. Japan is the main driver of the overestimation signal.

---

## ERA5-Land Assessment (Not Used)

ERA5-Land monthly runoff extracted from existing .nc file. Units are meters/month. After conversion to mm/yr, values are ~35 mm/yr vs existing ~1019 mm/yr in feature matrix — unit mismatch with existing data. Correlation r=0.74, no significant trend (p=0.26). **Decision: not used** — doesn't add information beyond WorldClim.

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
| WaW3.0 country waste | 2024 | Done | 29,875/31,819 (93.9%) |
| ERA5-Land runoff | 2015-2025 | Not used | Unit mismatch |
| VIIRS VNL v2.1 | 2021 | Done | 31,710/31,819 |
| MERIT Hydro | — | Blocked | NaN (on other PC) |
| LandScan population | — | Not needed | Ratio approach |
| Jambeck 2015 waste | 2015 | Not needed | Ratio approach |

---

## Strategic Decision (2026-06-30)

### The validation angle is data-walled — do not pursue it as the headline

The central "models overestimate top emitters by 1.7×" claim is **fragile**: removing
Japan (58% of the 64 calibration rivers) moves the calibration slope from 0.71 → **0.977**
(R²=0.76) — i.e. the overestimation effect is carried almost entirely by Japanese rivers.

A 2026 literature scan confirmed this is a **field-wide evidence gap**, not just ours:
- **South America**: no field-measured annual mass-flux observations suitable for
  validation. Only microplastic concentrations or modeled estimates (e.g. Amazon ~38,900
  t/yr, modeled).
- **Africa**: at most 1–2 candidates — Odaw, Ghana (macroplastic transport monitoring,
  reported items/h → needs mass conversion); Umgeni, South Africa (Mani et al. 2026,
  surface/daylight-only, not directly comparable).
- **SE Asia** (already represented): Klang, Malaysia (~4,234 t/yr, 2025); Mahiga Creek,
  Philippines (2023). Convertible but don't break Japan's dominance.

### Prior art / competitive landscape (novelty check)

| Work | What it is | Does it scoop us? |
|---|---|---|
| Meijer et al. 2021 (Sci Adv) | The deployed 31,819-outfall ranking; constant 12% plastic fraction | This is what we correct |
| Country-specific riverine contributions (2023, STOTEN) | "R2O" country-level model + HDI, 161 countries | No — coarser, country-resolution, different architecture |
| Rivers of plastic (Ma et al. 2024, Env. Pollution) | New socio-economic + topographic model, seasonal | No — a new model, not a Meijer correction; signals the field is active |

**Verdict:** the specific contribution — substitute WaW 3.0 country-specific plastic
fractions for Meijer's constant 12% and re-rank the operational outfall ranking — appears
**unclaimed**. BUT the *concept* (country waste composition matters) is well-established;
novelty is narrow and applied. Building a new model would lose to better-resourced groups.

### Chosen direction: short paper around the *operational* ranking

Frame: *"An updated and uncertainty-aware correction to the operational global river
plastic ranking: country-specific waste composition reorders priority rivers, but the
evidence base cannot yet confirm the result."*

- Differentiator is **operational, not academic**: Meijer 2021 is the ranking actually
  deployed (TOC 30 Cities). Competing 2024 models aren't used yet.
- Packages all three honest findings: WaW 3.0 substitution (concrete) + reordering
  (decision-relevant) + validation gap (call to action).
- Target venue: Brief Communication / Correspondence — *Marine Pollution Bulletin*,
  *Environmental Research Letters*, or a *Nature* journal Correspondence/Matters Arising.
  NOT a flagship — flagship is off the table without field data that doesn't exist.

### Parallel non-publication move

Contact The Ocean Cleanup directly for their interceptor field data (capture rates on
top-ranked, including non-Japanese, rivers) — the one thing that could revive validation.

### MERIT status (resolved 2026-06-30)

MERIT extraction now works (`merit_extracted.csv`: elv ~29.5%, slp ~18.6%, upa ~43.3%;
slope fixed). BUT MERIT data is **not wired into the model** and, where it overlaps,
correlates only weakly with the calibration ratio (|r| ≤ 0.13). It does not change results
and is not needed for the short paper. Leave as documented groundwork.

---

## Next Steps

1. Draft the short-paper framing (see `docs/paper_outline.md` → "SHORT-PAPER VERSION")
2. Verify/convert candidate non-Japan points (Klang, Mahiga Creek, Odaw) — optional, for spread
3. Build the one essential figure: top-20 reordering (Meijer 12% vs WaW 3.0)
4. Outreach email to The Ocean Cleanup for interceptor capture-rate data

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
- ERA5 runoff in meters/month; conversion to mm/yr gives values 30x lower than expected — likely units issue in .nc file, not used
- Nightlight deviation only applies to rivers with country_iso (93.9% after fixes); missing values filled with 0 (no deviation)
