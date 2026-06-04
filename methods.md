# Methods

Detailed description of the modeling approach, complementing the manuscript methods section.

---

## 1. Baseline reproduction (Meijer 2021)

The Meijer 2021 model estimates plastic flux at river outfalls as:

```
E_i = W_i × P_mobilization × P_transport
```

Where:
- `W_i` = mismanaged plastic waste generated in catchment i (kg/year)
- `P_mobilization` = probability that mismanaged waste reaches a waterway (function of runoff, population density, distance to waterway)
- `P_transport` = probability that plastic in the waterway reaches the ocean (function of river length, discharge, slope)

We reimplement this pipeline using the same input sources (Jambeck 2015 waste data, HydroSHEDS v1, GRUN runoff) and verify that our R² on the validation flux observations is within 10% of the published value. This is the baseline all improvements are measured against.

---

## 2. Updated feature matrix

We extend the Meijer feature set with:

### Waste inputs (updated)
- World Bank What a Waste 3.0 (2026): waste generation rate kg/capita/day, collection rate %, open dumping %, by country
- Applied to catchment population using HydroSHEDS catchment boundaries + LandScan population grid

### Hydrology (improved resolution)
- MERIT Hydro v1.0.1 at 90m: upstream drainage area, channel width, slope, HAND
- Flow accumulation computed with `pysheds` on MERIT DEM
- ERA5-Land monthly runoff 2015–2024: mean annual runoff + interannual variability (coefficient of variation) per catchment

### Socioeconomic proxies (new)
- VIIRS nightlight intensity trend 2015–2023: urbanization rate proxy
- OSM road density within 5km buffer of river: infrastructure access
- World Bank WASH investment index: sanitation infrastructure proxy

### Temporal features (new)
- ERA5 runoff anomaly 2020–2024 vs 2015–2019 baseline: captures climate-driven mobilization shifts
- Waste generation trend: linear slope of per-capita waste 2015–2024 from World Bank

---

## 3. Model architecture

### XGBoost regression
- Target: log10(plastic flux in kg/year) at river outfall
- Features: ~25 engineered features per outfall (see above)
- Training: 5-fold cross-validation on ~60 rivers with observed fluxes
- Hyperparameter tuning: Optuna (50 trials)
- Evaluation: R², RMSE, Spearman rank correlation on 30-river held-out set

### Uncertainty quantification
- Conformal prediction intervals via MAPIE (CQR method)
- Produces per-river 90% credible intervals on emission estimates
- Calibrated on held-out validation set

### SHAP explainability
- SHAP TreeExplainer for global feature importance
- Per-river SHAP waterfall plots for top-50 emitters
- Enables comparison of what drives emissions now vs Meijer's expert weights

---

## 4. Validation

Validation flux dataset assembled from:
- Meijer 2021 supplementary tables S4 and S5 (~50 rivers)
- van Emmerik et al. post-2021 observations (~15 European rivers)
- Additional published field campaigns identified in literature review

Split: 60 training / 30 held-out (stratified by continent and river size)

Metrics reported:
- R² (coefficient of determination)
- RMSE in log10(kg/year)
- Spearman ρ (rank correlation — most relevant for prioritization use case)
- Coverage of 90% prediction intervals

---

## 5. Updated ranking

Final ranking produced by applying the trained model to all ~31,819 river outfalls in the Meijer dataset, using updated 2024 feature values. Outputs:
- Point estimate (median) in kg/year
- 90% CI lower and upper bounds
- Rank in updated model
- Rank in Meijer 2021
- Delta rank (positive = risen, negative = fallen)
- Temporal trend flag (increasing / stable / decreasing 2015–2024)
