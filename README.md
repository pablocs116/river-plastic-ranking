# River Plastic Emission Ranking — Updated Model (2025)

> An independent recalibration of the Meijer et al. (2021) global river plastic emission model against 64 observed flux measurements, with updated waste statistics (World Bank What a Waste 3.0) and a nightlight-based correction for urban waste management quality.

[License: MIT](LICENSE)
[Python 3.10](https://www.python.org/)
[Raw data DOI: 10.5281/zenodo.20793131](https://doi.org/10.5281/zenodo.20793131)
[Status: In Progress](#)

---

## Data availability

Raw input datasets (Meijer 2021 shapefile, HydroRIVERS, WorldClim precipitation,
What a Waste 3.0, VIIRS nightlights, ERA5-Land runoff) are archived on Zenodo:
**[10.5281/zenodo.20793131](https://doi.org/10.5281/zenodo.20793131)** (CC BY 4.0,
`river-plastic-ranking-raw-data.zip`, ~2.86 GB). Download and unpack into `data/raw/`
to reproduce the processed feature matrix via `notebooks/02_feature_engineering.ipynb`.

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


All data is freely available. See `data_access.md` for download instructions, or recover
everything at once from the Zenodo deposit (below).

---

## Repo structure

```
river-plastic-ranking/
│
├── data/
│   ├── raw/                  # Source datasets — not committed; archived on Zenodo (see Data availability)
│   └── processed/            # Feature matrix, recalibrated emissions, reordering outputs
│
├── notebooks/
│   ├── 01_baseline_reproduction.ipynb   # Reproduce the Meijer 2021 baseline
│   ├── 02_feature_engineering.ipynb     # Build the feature matrix (needs raw data; memory-heavy)
│   ├── 03_model_training.ipynb          # Baseline model runs / diagnostics
│   ├── 04_observed_flux_model.ipynb     # Calibration against observed flux
│   ├── 05_updated_ranking.ipynb         # Recalibrated ranking
│   ├── 06_paper_analysis.ipynb          # Calibration + recalibrated estimates
│   ├── 07_updated_ranking.ipynb         # Ranking with data-quality fixes
│   ├── 08_improved_model.ipynb          # Plastic-fraction + nightlight correction
│   └── 09_paper_figures.ipynb           # Manuscript figures
│   (each NN_*.ipynb has a paired NN_*_executed.ipynb with outputs)
│
├── scripts/
│   ├── plastic_fraction_reorder.py      # Lightweight repro of the top-20 reordering (core result)
│   ├── extract_merit.py, merit_*.py     # MERIT Hydro extraction pipeline
│   └── download_*.py                    # Auxiliary dataset download helpers
│
├── src/models/baseline.py               # Meijer 2021 probabilistic reimplementation
│
├── docs/                                # paper_outline.md, literature reviews
├── methods.md, data_access.md           # Methods supplement, data download guide
├── DEV_NOTES.md                         # Full development log, decisions, gotchas
├── environment.yml / requirements.txt   # Reproducible environment (Python 3.10)
├── CITATION.cff
└── LICENSE
```

---

## Quickstart

The headline result (top-20 reordering) reproduces in seconds and does **not** need the
memory-heavy feature-engineering step:

```bash
git clone https://github.com/pablocs116/river-plastic-ranking.git
cd river-plastic-ranking

# Environment (Python 3.10)
python -m venv .river-env && .river-env/bin/pip install -r requirements.txt
#   or:  conda env create -f environment.yml && conda activate riverplastic

# Recover raw inputs from Zenodo, unpack into data/raw/
#   (2.86 GB — see Data availability). Then reproduce the core reordering:
.river-env/bin/python scripts/plastic_fraction_reorder.py
```

Rebuilding the full feature matrix (`notebooks/02_feature_engineering.ipynb`) reads the
1.5 GB HydroRIVERS geodatabase and needs **>8 GB RAM** — run it on a higher-memory machine
or in Google Colab.

---

## Methods summary

This work follows Meijer et al.'s conceptual framework (mismanaged plastic waste ×
mobilization probability × river transport probability) and **recalibrates** it against
observations — it is not a machine-learning model. Two corrections are applied to the
published Meijer emissions:

1. **Country-specific plastic fraction** — replace Meijer's constant 12% with World Bank
   What a Waste 3.0 values (1.6–30% per country), plus data-quality fixes (endorheic
   basins, implausible high-income mismanagement defaults, coastal country assignment).
2. **Observational calibration** — a log–log linear calibration against 64 rivers with
   observed annual flux, with a nightlight-based term for within-country waste-management
   quality, and bootstrap uncertainty.

> Note: an earlier design explored XGBoost / conformal prediction. It was dropped — with
> n = 64 calibration rivers, ML did not outperform linear calibration. The current method
> is calibration + input correction. See `DEV_NOTES.md` for the full history.

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