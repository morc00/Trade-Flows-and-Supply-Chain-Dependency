# Trade Flows and Supply Chain Dependency

This repository contains the project notebook for **DSC3132 theme CNT-12**. It studies India's trade in electronic integrated circuits (HS 8542) using annual bilateral records from the United Nations Comtrade Database.

## First analytics stage

- **Type:** Descriptive analytics
- **Question:** How did India's imports and exports of electronic integrated circuits change between 2019 and 2025, and how concentrated were India's imports among supplier countries or areas in the latest year?
- **Source:** [UN Comtrade](https://comtrade.un.org/)
- **Measures:** Annual import and export value, trade balance, supplier shares, HHI, effective supplier count, and top-supplier concentration ratios

The source choice, data requirements, access plan, quality checks, analysis, interpretation, and limitations are recorded in `notebooks/Project_Notebook.Rmd`.

## Repository structure

```text
.
├── data/
│   ├── raw/                    # API download and query metadata
│   └── processed/              # Cleaned analysis dataset
├── notebooks/
│   └── Project_Notebook.Rmd    # R Markdown notebook with Python analysis
├── reports/
│   ├── figures/                # Reproducible charts
│   └── tables/                 # Reproducible summary tables
├── scripts/
│   └── data_acquisition.py     # UN Comtrade public API client
├── requirements.txt
└── README.md
```

## Reproduce the project

Create a local environment and install the Python packages:

```bash
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

Download the real trade data:

```bash
.venv\Scripts\python scripts/data_acquisition.py
```

Open `notebooks/Project_Notebook.Rmd` in RStudio and knit it to HTML. The notebook requires the R packages `rmarkdown`, `knitr`, and `reticulate`. All data acquisition, preparation, calculations, and visualisation are written in Python.

## Data source and scope

The acquisition script calls the official public preview endpoint documented in the [UN Comtrade API guide](https://uncomtrade.org/docs/un-comtrade-api/). It makes one query per year, rejects a response that reaches the 500-record preview limit, joins official partner names, and saves exact query URLs in `data/raw/un_comtrade_metadata.json`.

The raw dataset contains India-reported annual import and export values for HS 8542 from 2019 through 2025. Partner code `0` is the World aggregate; it is used for national totals but excluded from supplier concentration calculations.

## Limitations

Trade values are in current US dollars and do not isolate price or exchange-rate effects. HS 8542 is an aggregate product group, bilateral trade does not reveal every upstream production dependency, and Comtrade records can be revised after retrieval. The `Other Asia, nes` partner label is retained exactly as published. The present notebook therefore provides a descriptive baseline rather than a causal model or a firm-level sourcing recommendation.
