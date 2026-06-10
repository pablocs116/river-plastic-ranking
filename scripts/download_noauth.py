"""
Download datasets that require no authentication.
  1. Meijer 2021 baseline outputs (figshare)
  2. World Bank What a Waste 3.0
  3. WorldClim v2.1 precipitation (2.5 min)
"""

import json
import zipfile
from pathlib import Path

import requests
from tqdm import tqdm

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"


def download_file(url: str, dest: Path, desc: str | None = None):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        print(f"  [skip] {dest.name} already exists")
        return
    print(f"  Downloading {desc or dest.name}...")
    resp = requests.get(url, stream=True, timeout=60)
    resp.raise_for_status()
    total = int(resp.headers.get("content-length", 0))
    with open(dest, "wb") as f, tqdm(total=total, unit="B", unit_scale=True, desc=dest.name) as bar:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
            bar.update(len(chunk))


def extract_zip(zip_path: Path, dest_dir: Path):
    if not zip_path.exists():
        return
    print(f"  Extracting {zip_path.name}...")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(dest_dir)
    zip_path.unlink()
    print(f"  Cleaned up {zip_path.name}")


def download_meijer2021():
    print("\n[1/3] Meijer 2021 baseline outputs")
    out_dir = DATA_RAW / "meijer2021"
    shp_file = out_dir / "Meijer2021_midpoint_emissions.shp"
    if shp_file.exists():
        print(f"  [skip] Meijer 2021 already extracted")
        return
    zip_url = "https://ndownloader.figshare.com/files/27807774"
    zip_path = out_dir / "Meijer2021_midpoint_emissions.zip"
    download_file(zip_url, zip_path, "Meijer 2021 shapefile + tables")
    extract_zip(zip_path, out_dir)
    print("  Done.")


def download_worldbank_waste():
    print("\n[2/3] World Bank What a Waste 3.0 (via Data360 API)")
    out_dir = DATA_RAW / "worldbank_waste"
    out_file = out_dir / "what_a_waste_3.0.csv"
    out_dir.mkdir(parents=True, exist_ok=True)
    if out_file.exists():
        print(f"  [skip] {out_file.name} already exists")
        return

    WAW_INDICATORS = [
        "WM_MSW_GEN",
        "WM_MSW_COMP",
        "WM_MSW_TREAT",
        "WM_MSW_UNC",
        "WM_COL_COV",
        "WM_DRS_SYS",
        "WM_EPR_SYS",
        "WM_LEG_PLS",
        "WM_NMSW_COMP",
        "WM_SWM_INS",
        "WM_WKRS_REF",
    ]

    all_rows = []
    for indicator in WAW_INDICATORS:
        print(f"  Fetching {indicator}...")
        resp = requests.post(
            "https://data360api.worldbank.org/data360/portal/v1/data",
            json={
                "Site": "data360",
                "Database_ID": "WB_WAW",
                "indicator": indicator,
                "ref_area": "all",
            },
            timeout=60,
        )
        resp.raise_for_status()
        data = json.loads(resp.content.decode("utf-8-sig"))
        for item in data:
            row = {
                "REF_AREA": item.get("REF_AREA"),
                "INDICATOR": item.get("INDICATOR"),
                "UNIT_MEASURE": item.get("UNIT_MEASURE"),
                "FREQ": item.get("FREQ"),
            }
            time_series = item.get("data", {}).get("yAxis", [])
            years = item.get("data", {}).get("xAxis", [])
            for yr, val in zip(years, time_series):
                row[f"YR_{yr}"] = val
            all_rows.append(row)

    if all_rows:
        import pandas as pd
        df = pd.DataFrame(all_rows)
        df.to_csv(out_file, index=False)
        print(f"  Saved {len(df)} rows to {out_file.name}")
    else:
        print("  WARNING: No data retrieved from Data360 API")
    print("  Done.")


def download_worldclim():
    print("\n[3/3] WorldClim v2.1 precipitation (2.5 min)")
    out_dir = DATA_RAW / "worldclim"
    zip_url = "https://geodata.ucdavis.edu/climate/worldclim/2_1/base/wc2.1_2.5m_prec.zip"
    zip_path = out_dir / "wc2.1_2.5m_prec.zip"
    download_file(zip_url, zip_path, "WorldClim precip 2.5min")
    extract_zip(zip_path, out_dir)
    print("  Done.")


if __name__ == "__main__":
    print("=== Downloading open-access datasets ===")
    download_meijer2021()
    download_worldbank_waste()
    download_worldclim()
    print("\nAll open-access downloads complete.")
