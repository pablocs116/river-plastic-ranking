# Future Research Ideas

Achievable with data/methods that don't exist yet but are expected within 1-3 years.

---

## 1. Converting Surface Daylight Observations to Total 24h Flux

**Status**: Not feasible now. Achievable in 1-2 years.

**Idea**: Mani et al. (2026) and other camera-based studies measure surface daylight-only plastic flux. If we could convert these to total 24h water-column flux, we'd unlock dozens of new calibration points in data-scarce regions.

**Two-step conversion**:
1. **Day → Night**: Scale daylight observations to 24h using a day:night ratio
2. **Surface → Total water column**: Apply extrapolation factor (Roebroek et al. 2025)

**What's blocking us**:
- Only one dataset has nighttime river plastic data: Schreyers et al. (2024), 74.5h on the Saigon River — but they don't report a day:night ratio
- Surface→total correction factors exist (Roebroek 2025) but are site-specific and vary with discharge

**What would unlock it**:
- Schreyers/van Emmerik group publishing the Saigon day:night ratio from their raw data
- More 24h monitoring campaigns (The Ocean Cleanup interceptors collect 24h data but haven't published day/night separation)
- Standardized extrapolation factors per river type (Roebroek 2025 methodology applied more broadly)

**If achieved**: Could add 50-100+ calibration points from camera studies worldwide, especially in tropical developing countries where we have zero data. This alone could make regional calibration viable.

**Key references**:
- Schreyers et al. (2024) "River plastic transport affected by tidal dynamics" — HESS, only nighttime dataset
- Roebroek et al. (2025) "Plastic Transport in Rivers: Bridging the Gap Between Surface and Water Column" — Water Research, extrapolation factor methodology
- Kooi et al. (2017) — modeled surface:total ratios (1-30x depending on wind/turbulence)
- Lenaker et al. (2019) — empirical surface:total in Milwaukee River system
- Gnann et al. (2026) — 16-month 24h monitoring on the Rhine (passive trap, no day/night separation published yet)

---

## 2. Regional Calibration with Enough Observed Flux Data

**Status**: Blocked by data. Achievable in 2-3 years.

**Idea**: Instead of one global slope (0.72), fit separate calibrations per region/continent. Our data hints this matters: Japan slope=0.201 vs non-Japan slope=0.852.

**What's blocking us**: 64 rivers, 0 African, 0 South American. Need ~30 per major region.

**What would unlock it**: Systematic compilation of observed flux data (see literature search list in DEV_NOTES.md). Field campaigns by van Emmerik group, The Ocean Cleanup, and UNEP are actively collecting this.

**If achieved**: Could reveal that overestimation is region-specific (e.g., models may be more accurate in SE Asia but overestimate in Africa). This would be the main finding of a second paper.

---

## 3. Grid-Level Model Reimplementation with Updated Inputs

**Status**: Blocked by MERIT Hydro + compute. Achievable in 1-2 years.

**Idea**: Reimplement Meijer's P(M)×P(R)×P(O) at 30arcsec with updated inputs (WaW3.0, ERA5-Land, VIIRS, MERIT Hydro). Produce genuinely new emission estimates rather than a linear correction.

**What's blocking us**:
- MERIT Hydro tiles (~200GB) on another PC
- Per-cell flow path accumulation requires GEE or local raster processing
- Catchment-level approximation already failed (R²=-0.03)

**What would unlock it**: MERIT Hydro transfer + either GEE account or local compute pipeline

**If achieved**: New independent emission estimates, not just a recalibration. Could validate whether updated inputs change the ranking beyond what calibration alone does.

---

## 4. ML Model with Sufficient Calibration Data

**Status**: Blocked by data. Achievable in 2-3 years.

**Idea**: XGBoost failed with n=64 (R²=-0.03). With 200+ observed rivers, nonlinear models could capture interactions (e.g., waste × discharge, slope × urbanization) that a single slope cannot.

**What's blocking us**: Need ~200+ observed rivers for XGBoost to be viable (rule of thumb: ~10 samples per feature, we have 43 features).

**What would unlock it**: Same as #2 — systematic literature compilation + new field campaigns.

**If achieved**: A predictive model that could outperform Meijer in regions with different characteristics than the calibration set. SHAP explainability would reveal what actually drives emissions vs Meijer's expert-chosen weights.

---

## 5. Tidal Retention as a Model Correction Term

**Status**: Partially feasible now. Achievable in 1-2 years.

**Idea**: Add a tidal retention correction to Meijer's P(O) term. Mani showed 26-43% of days have zero/reverse flow in tidal estuaries. This could be parameterized as a function of tidal range and distance from mouth.

**What's blocking us**: Only 3 rivers studied (Mani et al. 2026). Our own tidal analysis is underpowered (p=0.21). Need tidal range data for all 31,819 outfalls.

**What would unlock it**:
- More tidal river studies (van Emmerik group working on this)
- Global tidal range dataset (e.g., TPXO model) applied at outfall locations
- At least 10-20 tidal vs non-tidal calibration rivers to validate the correction

**If achieved**: Structural improvement to the model rather than an empirical correction. Would specifically address why estuarine rivers are overpredicted.

**Key references**:
- Mani et al. (2026) — 26-43% zero/reverse flow days
- Schreyers et al. (2024) — tidal dynamics in Saigon River
