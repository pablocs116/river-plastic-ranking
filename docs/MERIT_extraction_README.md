MERIT extraction quick guide

1) Filter and unpack MERIT_Hydro.zip (only elv/slp/upa tiles containing outfalls):

Example (from repo root):

```
python scripts/merit_prepare_and_extract.py \
  --zip data/raw/MERIT_Hydro.zip \
  --fm river_outfalls.csv \
  --outdir data/raw/merit_15s_filtered --untar
```

If you prefer to extract all tiles for the variables, add `--all`.

2) If `slp` tiles are missing, derive them from the extracted `elv` tiles:

```
python scripts/derive_merit_slope_from_elv.py \
  --elv-dir data/raw/merit_15s_filtered/15s/elv \
  --out-dir data/raw/merit_15s_filtered/15s/slp
```

3) Sample the .tif files at outfall locations:

```
python scripts/sample_merit_at_outfalls.py \
  --merit-dir data/raw/merit_15s_filtered/15s \
  --outfalls river_outfalls.csv \
  --out data/processed/merit_extracted.csv
```

4) Install dependencies (use the environment you prefer):

```
pip install -r requirements-merit-extraction.txt
```

Notes:
- The prepare script extracts .tar files from the ZIP and, with `--untar`, unpacks .tif files.
- The sampling script expects `lon` and `lat` columns in `river_outfalls.csv`.
- MERIT Hydro is CC-BY-NC 4.0 — ensure compliance for publication.
