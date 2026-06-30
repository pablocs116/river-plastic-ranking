# CLAUDE.md

Guidance for working in this repo. Read `DEV_NOTES.md` for the scientific state of the project — especially its "Technical Gotchas" section, which complements this file.

## What this project is

An independent **recalibration** of the Meijer et al. (2021) global river-plastic-emission model against 64 observed-flux rivers, with updated waste data (World Bank What a Waste 3.0) and a nightlight-based correction. The headline result: the model overestimates top emitters (log-log calibration slope ≈ 0.7).

**The real method is log-log linear calibration + data-quality fixes, NOT machine learning.** ML was tried and failed (XGBoost R²=−0.03 with n=64). The README/`docs/paper_outline.md` still contain aspirational ML/XGBoost framing and reference `src/` modules and notebooks that **do not exist** (`src/features/*.py`, `src/models/xgboost_model.py`, `uncertainty.py`, `04_validation.ipynb`, `05_results_figures.ipynb`). Only `src/models/baseline.py` is real. Don't trust the repo-structure section of the README as ground truth — verify files exist.

## Environment — IMPORTANT

**Always use the project venv: `.river-env/bin/python`** (Python 3.10, has `numpy`, `pandas`, `rasterio`, `scipy`).

The system `python3` has **none** of the geo/data packages. Running scripts with bare `python3` is why `data/processed/merit_extracted.csv` was once silently written as 100% NaN — the scripts catch import/read errors and fall back to NaN. If a script produces all-NaN output, suspect the wrong interpreter first.

```bash
.river-env/bin/python scripts/sample_merit_at_outfalls.py --help
```

`environment.yml` describes a separate conda env (`riverplastic`, Python 3.11) that may not be the one actually in use. The venv is the source of truth for running code.

## Big files — do not scan blindly

- `data/raw/` is **~218 GB**, including `data/raw/MERIT_Hydro.zip` at **196 GB**. Never `find`/glob/`cat` across `data/raw` without scoping to a subdirectory. It is gitignored.
- `.river-env/` is a 391 MB virtualenv (gitignored).
- `data/processed/*.csv` are gitignored too. The committed analysis lives in the notebooks.

## Line endings

Files are stored **LF** in git. A `.gitattributes` (`* text=auto eol=lf`) normalizes on commit, so editing on Windows/WSL no longer shows every file as "modified." If you ever see dozens of files as modified with no content change, run `git add --renormalize .`.

## MERIT Hydro extraction pipeline

Scripts in `scripts/` (run with the venv):

- `merit_prepare_and_extract.py` — filter `MERIT_Hydro.zip` to tiles containing outfalls, extract `.tar`/`.tif`.
- `sample_merit_at_outfalls.py` — sample elv/slp/upa `.tif` tiles at `river_outfalls.csv` coords → `data/processed/merit_extracted.csv`. Globs `*.tif` per `{var}/` subdir (filename suffix is ignored).
- `derive_merit_slope_from_elv.py` — compute slope-% tiles from elevation tiles (there are no real `_slp.tif` tiles).
- `extract_merit.py` — older standalone extractor (nearest-valid-pixel; skips empty/corrupt tiles).

### Known issues (as of 2026-06-30)

1. **Partial tile coverage.** `data/raw/merit_15s_filtered/15s/{elv,upa}` holds only ~255 tiles, so the latest `merit_extracted.csv` is only ~30% (elevation) / ~43% (upstream area) filled. Full coverage requires extracting more tiles from the zip.
2. **Slope is broken.** `slope_pct` comes out absurd (median ~195,000%). Cause: `derive_merit_slope_from_elv.py` does not mask `-9999` nodata robustly before differencing, so nodata leaks into the elevation gradient. Fix: mask nodata (and implausible values) before `np.gradient`, and clip slope to a sane max. Elevation and upstream area are fine.
3. The `slp/` tile dir was historically polluted with copies of `_elv.tif` tiles (no real slope tiles exist) — slope must be derived.

## Conventions

- Commits go directly to `main` (solo research project; linear history).
- End commit messages with the `Co-Authored-By: Claude` trailer.
- Notebooks come in `NN_name.ipynb` (source) and `NN_name_executed.ipynb` (run-with-outputs) pairs.
