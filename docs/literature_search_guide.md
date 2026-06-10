# Observed River Plastic Flux — Search Guide

## Data Repositories

### General scientific data
| Platform | URL | What to search | Notes |
|---|---|---|---|
| **Zenodo** | https://zenodo.org | "river plastic flux", "macroplastic monitoring", "riverine plastic" | EU open repository. van Emmerik, Ocean Cleanup often deposit here |
| **Figshare** | https://figshare.com | Same terms | Meijer 2021 data is here. Many supplementary datasets |
| **PANGAEA** | https://www.pangaea.de | "plastic river", "macroplastic", "floating debris" | Earth & environmental science focus. European groups deposit here |
| **Dryad** | https://datadryad.org | "river plastic" | Less common for this field |
| **Kaggle** | https://www.kaggle.com/datasets | "plastic pollution", "river waste" | Unlikely to have academic flux data, but worth a check |
| **Mendeley Data** | https://data.mendeley.com | "river plastic flux" | Elsevier's repository. Some environmental datasets |
| **Harvard Dataverse** | https://dataverse.harvard.edu | "plastic river" | Less common but some environmental justice datasets |

### Institutional / project-specific
| Platform | URL | What to look for |
|---|---|---|
| **The Ocean Cleanup** | https://theoceancleanup.com/research/ | River interceptor data, monitoring reports |
| **The Ocean Cleanup — Figshare** | https://figshare.com/authors/The_Ocean_Cleanup/ | Their published datasets |
| **JRC Data Catalogue** | https://data.jrc.ec.europa.eu/ | European river plastic monitoring (EU MSFD) |
| **EMODnet** | https://www.emodnet.eu/ | European marine litter data, some river inputs |
| **UNEP GPA** | https://www.unep.org/explore-topics/oceans-seas/ | Global Programme of Action reports with river data |
| **World Bank Open Data** | https://data.worldbank.org | Waste data, not flux, but may link to studies |
| **GEOSS** | https://www.geoportal.org | "plastic river" — Global Earth Observation system |

### Literature databases
| Platform | URL | Search terms |
|---|---|---|
| **Google Scholar** | https://scholar.google.com | "river plastic flux" measurement tons/year, "macroplastic monitoring river" quantification |
| **Web of Science** | https://www.webofscience.com | Same + filter 2019-2026 |
| **Scopus** | https://www.scopus.com | Same + filter by Environmental Science |
| **Semantic Scholar** | https://www.semanticscholar.org | "river plastic emission observation" — good for finding citing papers |
| **OpenAlex** | https://openalex.org | Free, comprehensive. API available for bulk searches |
| **Dimensions** | https://app.dimensions.ai | Free academic search |

### Author-specific (most prolific groups)
| Group | Affiliation | Where they publish data |
|---|---|---|
| **van Emmerik** | Wageningen University | Zenodo, Figshare, PANGAEA |
| **The Ocean Cleanup** | TOC, Rotterdam | Figshare, own website |
| **Lebreton** | The Ocean Cleanup / independent | Figshare |
| **González-Fernández** | CIDCO, Spain | Zenodo, PANGAEA |
| **Roebroek** | Deltares, Netherlands | Zenodo |
| **Blettler** | CONICET, Argentina | Figshare, supplementary |
| **Schmidt** | TU Wien, Austria | Figshare |

## Search Strategy

### Phase 1: Repository search (1-2 days)
1. Search Zenodo, Figshare, PANGAEA for "river plastic flux" datasets
2. Download any CSV/XLSX with per-river flux measurements
3. Log in `observed_flux_literature_search.csv`

### Phase 2: Paper search (2-3 days)
1. Google Scholar: `"river plastic flux" OR "macroplastic transport river" tons OR kg measurement`
2. Filter 2019-2026
3. For each hit, check supplementary materials for flux tables
4. Check if data is deposited in a repository (often linked in the paper)

### Phase 3: Citation chaining (1-2 days)
1. Start from Meijer 2021 — who has cited it? (Google Scholar "Cited by")
2. Start from Mani 2026 — who has cited it?
3. Start from van Emmerik most-cited papers — follow citation chains
4. Use Semantic Scholar / OpenAlex for citation graph traversal

### Phase 4: Direct outreach (if needed)
1. Email van Emmerik group — they likely have unpublished monitoring data
2. Email The Ocean Cleanup research team
3. Check if UNEP has unpublished river assessment data

## What to extract for each river

| Field | Description | Example |
|---|---|---|
| `name` | River or site name | "Saigon River" |
| `country` | ISO 3166-1 alpha-3 | "VNM" |
| `lat`, `lon` | Measurement point coordinates | 10.78, 106.70 |
| `river_basin` | Broader basin if applicable | "Mekong" |
| `flux_ton_yr` | Annualized flux in tons/year | 43.2 |
| `flux_unit` | Original unit before conversion | "kg/day" |
| `measurement_period` | When measured | "2020-2022" |
| `n_observations` | How many sampling events | 12 |
| `method` | How measured | "net trawl", "visual counting", "camera", "boom" |
| `plastic_type` | Size fraction | "macroplastic >5mm", "microplastic" |
| `depth_coverage` | What part of water column | "surface only", "full water column" |
| `time_coverage` | Temporal coverage | "daylight only", "24h" |
| `source_paper` | First author + year | "van Emmerik 2022" |
| `source_doi` | DOI | "10.1016/..." |
| `source_url` | Direct URL to data | "https://zenodo.org/record/..." |
| `notes` | Anything unusual | "tidal estuary", "flood event during measurement" |
| `already_in_s3` | "yes" if already in Meijer Table S3 | "no" |

## Target: 100+ rivers, minimum 50 non-Japanese
