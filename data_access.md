# Data Access Instructions

Step-by-step guide to download all datasets used in this project. Everything is freely available — some require a free account or licence acceptance.

---

## 1. Meijer 2021 baseline outputs
**What:** GIS shapefile of 31,819 river outfalls with plastic emission estimates + observed flux validation table  
**Where:** https://figshare.com/articles/dataset/14515590  
**How:** Direct download, no registration required  
**Save to:** `data/raw/meijer2021/`

---

## 2. MERIT Hydro v1.0.1
**What:** 90m global river network — flow direction, upstream area, channel width, elevation  
**Where:** https://global-hydrodynamics.github.io/MERIT_Hydro/  
**How:**
1. Fill in the Google Form at https://goo.gl/forms/6VwfnasNjkYm0Wqu2
2. Receive password by email (usually same day)
3. Download relevant 30°×30° tiles from the Dropbox link provided
4. You only need tiles covering your study region — for global analysis, download all

**Alternatively:** Access via Google Earth Engine (no download needed):
```python
import ee
ee.Initialize()
merit = ee.Image("MERIT/Hydro/v1_0_1")
```
**Save to:** `data/raw/merit_hydro/`

---

## 3. HydroRIVERS v1.0 (fallback / topology)
**What:** Global river reach vector network with discharge estimates  
**Where:** https://www.hydrosheds.org/products/hydrorivers  
**How:** Free download after registering a free account  
**Save to:** `data/raw/hydrorivers/`

---

## 4. ERA5-Land Monthly Means
**What:** Global monthly runoff at ~9km resolution, 2015–2024  
**Where:** https://cds.climate.copernicus.eu  
**How:**
1. Register at https://cds.climate.copernicus.eu (free)
2. Go to the ERA5-Land Monthly Means dataset page → Download tab → **Accept Terms of Use** (required before API works)
3. Add credentials to `~/.cdsapirc`:
```
url: https://cds.climate.copernicus.eu/api/v2
key: YOUR-UID:YOUR-API-KEY
```
4. Run `notebooks/01_baseline_reproduction.ipynb` — the CDS download is triggered automatically

**Note:** Global monthly runoff 2015–2024 is ~15–20 GB. Queue it first, it takes a few hours.  
**Save to:** `data/raw/era5/`

---

## 5. World Bank What a Waste 3.0
**What:** Country-level waste generation rates, collection rates, mismanagement percentages  
**Where:** https://datatopics.worldbank.org/what-a-waste/  
**How:** Direct CSV download, no registration  
**Save to:** `data/raw/worldbank_waste/`

---

## 6. WorldClim v2.1 — Precipitation
**What:** 1km monthly precipitation climatology  
**Where:** https://worldclim.org/data/worldclim21.html  
**How:** Direct download (select "Precipitation", 2.5 min resolution is sufficient)  
**Save to:** `data/raw/worldclim/`

---

## 7. NASA VIIRS Nighttime Lights
**What:** Annual nightlight composites 2015–2023 (urbanization proxy)  
**Where:** https://earthdata.nasa.gov (search "VNP46A4")  
**How:** Free NASA Earthdata account required. Alternatively via GEE:
```python
viirs = ee.ImageCollection("NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG")
```
**Save to:** `data/raw/viirs/`

---

## 8. OpenStreetMap road network
**What:** Road density per catchment (infrastructure access proxy)  
**Where:** https://download.geofabrik.de (by continent/country)  
**How:** Direct download, no registration. Use `osmnx` for targeted extraction.  
**Save to:** `data/raw/osm/`

---

## Credential template

Copy `.env.example` to `.env` and fill in your credentials (never commit `.env`):

```bash
cp .env.example .env
```

```
CDS_KEY=your-uid:your-api-key
GEE_PROJECT=your-gee-project-id
```
