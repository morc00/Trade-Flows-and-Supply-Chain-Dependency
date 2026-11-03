# Trade Flows and Supply Chain Dependency

This repository contains the project notebook and knitted report for **DSC3132 theme CNT-12**. It studies India's trade in electronic integrated circuits (HS 8542) using annual bilateral records from the United Nations Comtrade Database. The notebook contains descriptive analysis followed by a diagnostic decomposition at the HS six-digit level. The finished report is available in both HTML and PDF under `reports/`.

## First analytics stage

- **Type:** Descriptive analytics
- **Question:** How did India's imports and exports of electronic integrated circuits change between 2019 and 2025, and how concentrated were India's imports among supplier countries or areas in the latest year?
- **Source:** [UN Comtrade](https://comtrade.un.org/)
- **Measures:** Annual import and export value, trade balance, supplier shares, HHI, effective supplier count, and top-supplier concentration ratios

## Diagnostic stage

- **Question:** Which changes in supplier economies and HS six-digit product categories account for the growth and changing concentration of India's integrated-circuit imports between 2019 and 2025?
- **Additional data:** Five HS six-digit product categories within HS 8542
- **Methods:** Product growth contribution, supplier-share change, annual HHI, HHI contribution change, and partner-product decomposition

The source choice, data requirements, access plan, quality checks, analysis, interpretation, and limitations are recorded in `notebooks/Project_Notebook.Rmd`.

## Key findings

- Imports rose from **USD 10.17 billion in 2019 to USD 28.62 billion in 2025** (18.8% CAGR), while exports stayed close to **USD 242 million** and the trade deficit widened to **USD 28.37 billion**.
- In 2025, **China (40.9%)**, **Other Asia, nes (28.1%)**, and **Rep. of Korea (16.0%)** supplied 85.0% of import value. The HHI was **2,752.8**, equivalent to about **3.6 equally sized suppliers**.
- **Processors and controllers** accounted for **61.1%** of the import increase, followed by memories (24.7%), other integrated circuits (16.0%), and amplifiers (3.0%). Imports of parts fell and offset 4.8% of growth elsewhere.
- The headline HHI was almost unchanged between 2019 and 2025, but the annual path was not: it fell to **1,949.5 in 2022** and rose to **3,334.0 in 2023**. Over the period, `Other Asia, nes` gained **27.2 percentage points** and China gained **5.6**, while China, Hong Kong SAR lost **34.2** and Singapore lost **6.4**.
- The shift between Hong Kong and `Other Asia, nes` may reflect trade routing or partner attribution, so the report treats it as a change in declared sourcing rather than proof of physical relocation.

## Repository structure

```text
.
├── data/
│   ├── raw/                    # HS4 and HS6 API downloads and query metadata
│   └── processed/              # Validated analysis datasets
├── notebooks/
│   └── Project_Notebook.Rmd    # R Markdown notebook with Python analysis
├── reports/
│   ├── Project_Notebook.html   # Knitted HTML report
│   ├── Project_Notebook.pdf    # Knitted PDF report
│   ├── figures/                # Reproducible charts
│   └── tables/                 # Reproducible summary tables
├── scripts/
│   └── data_acquisition.py     # UN Comtrade public API client
├── requirements.txt
└── README.md
```

## Reproduce the project

Create a local environment and install the Python packages. Python 3.13 is the tested interpreter:

```bash
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

Download the real trade data:

```bash
.venv\Scripts\python scripts/data_acquisition.py
```

Open `notebooks/Project_Notebook.Rmd` in RStudio and knit it to HTML. The notebook requires the R packages `rmarkdown`, `knitr`, and `reticulate`. All data acquisition, preparation, calculations, and visualisation are written in Python.

To build the PDF version, run this from the repository root:

```r
rmarkdown::render(
  "notebooks/Project_Notebook.Rmd",
  output_format = rmarkdown::pdf_document(toc = TRUE),
  output_file = "Project_Notebook.pdf"
)
```

Then move `notebooks/Project_Notebook.pdf` into `reports/`. The PDF build also needs a LaTeX installation such as MiKTeX or TinyTeX; the HTML build does not.

## Report outputs

Knitting the notebook produces the report plus the following reproducible outputs:

- `reports/figures/` — six charts covering trade trends, supplier shares, the trade balance, product contributions, the HHI trend, and supplier-share shifts.
- `reports/tables/` — seven CSV tables covering the yearly summary, 2025 supplier shares and concentration metrics, product and partner-product growth drivers, HHI by year, and supplier concentration drivers.
- `data/processed/` — cleaned heading-level and HS6 analysis datasets.

## Data source and scope

The acquisition script calls the official public preview endpoint documented in the [UN Comtrade API guide](https://uncomtrade.org/docs/un-comtrade-api/). It makes one query per year and product, rejects a response that reaches the 500-record preview limit, joins official partner names, and saves exact query URLs in the raw-data metadata files.

The raw datasets contain India-reported annual import and export values for HS 8542 and six-digit import detail from 2019 through 2025. Partner code `0` is the World aggregate; it is used for national totals but excluded from supplier concentration calculations. The five detailed categories reconcile to the published HS 8542 total in every year.

The notebook checks the data before analysis: complete 2019-2025 coverage, one World total per year and flow, no duplicate country-flow-year records, non-negative values, and two reconciliation tests. Non-group bilateral partners must sum to the World total within 0.1%, and the five HS6 categories must sum to the HS 8542 total within 0.001%.

## Limitations

Trade values are in current US dollars and do not isolate price or exchange-rate effects. HS 8542 is an aggregate product group, bilateral trade does not reveal every upstream production dependency, and Comtrade records can be revised after retrieval. The `Other Asia, nes` partner label is retained exactly as published. The present notebook therefore provides a descriptive baseline rather than a causal model or a firm-level sourcing recommendation.
