# River Plastic Emission Ranking — Updated Model (2025)

> An independent recalibration of the Meijer et al. (2021) global river plastic emission model against 64 observed flux measurements, with updated waste statistics (World Bank What a Waste 3.0) and a nightlight-based correction for urban waste management quality.

[License: MIT](LICENSE)
[Python 3.11](https://www.python.org/)
[Preprint](#)
[Status: In Progress](#)

---

## Motivation

Meijer et al. (2021) established the most widely used global ranking of rivers by plastic emission to the ocean — the foundation for The Ocean Cleanup's 30 Cities Program and similar initiatives. That model was calibrated on data from ~2015 and uses a hand-tuned probabilistic formulation.

Five years later:

- Waste management data has been substantially updated (World Bank What a Waste 3.0, published 2024 with data through 2022)
- Post-2021 field observations from additional rivers are now available for validation

This project reproduces the Meijer 2021 baseline, diagnoses a structural overestimation for high-emission rivers (log-log slope ~0.7), and applies a linear calibration against 64 observed flux measurements. The result is an updated ranking of 31,819 river outfalls with bootstrap uncertainty estimates — directly actionable for deployment prioritization.

---

## Key outputs

- **Recalibrated global river plastic emission estimates** (31,819 outfalls, metric tons/year)
- **Bootstrap uncertainty**: 95% CIs on concentration metrics (n=2,000 resamples)
- **Delta map**: rank change vs Meijer 2021 — which rivers are most affected by recalibration
- **Validation report**: calibration R², Spearman ρ, Japan sensitivity analysis

---

## Data sources (all open)


| Dataset                 | Source                                                                                  | Used for                                        |
| ----------------------- | --------------------------------------------------------------------------------------- | ----------------------------------------------- |
| Meijer 2021 outputs     | [figshare 10.6084/m9.figshare.14515590](https://figshare.com/articles/dataset/14515590) | Baseline reproduction + validation flux obs     |
| MERIT Hydro v1.0.1      | [global-hydrodynamics.github.io](https://global-hydrodynamics.github.io/MERIT_Hydro/)   | River network, upstream area, channel width     |
| HydroRIVERS v1.0        | [hydrosheds.org](https://www.hydrosheds.org/products/hydrorivers)                       | River reach topology                            |
| ERA5-Land monthly       | [ECMWF CDS](https://cds.climate.copernicus.eu)                                          | Runoff forcing 2015–2025 (early 2026 available) |
| What a Waste 3.0        | [World Bank](https://datatopics.worldbank.org/what-a-waste/)                            | Waste generation + management rates             |
| WorldClim v2.1          | [worldclim.org](https://worldclim.org)                                                  | Precipitation climatology                       |
| NASA VIIRS nightlights  | [NASA Earthdata](https://earthdata.nasa.gov)                                            | Urbanization proxy                              |
| OSM road network        | [Geofabrik](https://download.geofabrik.de)                                              | Infrastructure access proxy                     |
| Field flux observations | Meijer S4/S5 + van Emmerik et al.                                                       | Model validation                                |


All data is freely available. See `docs/data_access.md` for download instructions.

---

## Repo structure

```
river-plastic-ranking/
│
├── data/
│   ├── raw/                  # Downloaded source files (not committed, see docs/)
│   └── processed/            # Cleaned, merged features per river outfall
│
├── notebooks/
│   ├── 01_baseline_reproduction.ipynb   # Reproduce Meijer 2021 within 10% R²
│   ├── 02_feature_engineering.ipynb     # Build updated feature matrix
│   ├── 03_model_training.ipynb          # XGBoost + conformal prediction
│   ├── 04_validation.ipynb              # Held-out evaluation vs baseline
│   └── 05_results_figures.ipynb         # All publication figures
│
├── src/
│   ├── features/
│   │   ├── hydrology.py      # MERIT Hydro processing, upstream area aggregation
│   │   ├── waste.py          # World Bank waste data merging by country/catchment
│   │   ├── climate.py        # ERA5 runoff extraction and temporal aggregation
│   │   └── socioeconomic.py  # Nightlights, OSM road density, WASH index
│   ├── models/
│   │   ├── baseline.py       # Meijer 2021 probabilistic reimplementation
│   │   ├── xgboost_model.py  # XGBoost training + SHAP explainability
│   │   └── uncertainty.py    # Conformal prediction intervals (MAPIE)
│   └── viz/
│       ├── maps.py           # Geopandas + matplotlib global maps
│       └── validation.py     # Residual plots, rank correlation figures
│
├── results/
│   ├── figures/              # Publication-ready figures (PNG + SVG)
│   └── tables/               # Updated ranking tables (CSV + GeoJSON)
│
├── docs/
│   ├── data_access.md        # Step-by-step download instructions per dataset
│   └── methods.md            # Detailed methods supplement
│
├── environment.yml           # Conda environment (fully reproducible)
├── .gitignore
└── LICENSE
```

---

## Quickstart

```bash
# 1. Clone
git clone https://github.com/pablocs116/river-plastic-ranking.git
cd river-plastic-ranking

# 2. Create environment
conda env create -f environment.yml
conda activate riverplastic

# 3. Download data (see docs/data_access.md for credentials)
# Then run notebooks in order: 01 → 02 → 03 → 04 → 05
```

---

## Methods summary

This model follows Meijer et al.'s conceptual framework (mismanaged plastic waste × mobilization probability × river transport probability) but replaces the expert-elicited parameters with a gradient-boosted regression (XGBoost) trained on observed plastic flux measurements from ~80 rivers globally.

Key improvements over Meijer 2021:

1. **Updated waste data** — World Bank What a Waste 3.0 (data through 2022) vs Jambeck 2015
2. **Higher-resolution river network** — MERIT Hydro 90m vs HydroSHEDS 500m
3. **Temporal forcing** — ERA5 runoff anomalies 2015–2025 vs static climatology
4. **New features** — urbanization trend (VIIRS), infrastructure access (OSM), WASH investment index
5. **Uncertainty quantification** — conformal prediction intervals vs point estimates
6. **Extended validation** — ~80 observed fluxes vs ~50 in original paper

---

## Citation

If you use this work, please cite:

```bibtex
@misc{castillo2026riverplastic,
  author    = {Cabriada, Pablo},
  title     = {Updated Global River Plastic Emission Ranking (2025)},
  year      = {2026},
  publisher = {EarthArXiv},
  note      = {Preprint. github.com/pablocs116/river-plastic-ranking}
}
```

Also cite the original model this work extends:

> Meijer, L.J.J., van Emmerik, T., van der Ent, R., Schmidt, C., Lebreton, L. (2021). More than 1000 rivers account for 80% of global riverine plastic emissions into the ocean. *Science Advances*, 7(18).

---

## Contact & collaboration

Pablo Cabriada · [github.com/pablocs116](https://github.com/pablocs116)

This is independent research. If you work on river plastic monitoring or ocean cleanup operations and are interested in collaborating — particularly on validation data or field observations — please open an issue or get in touch directly.