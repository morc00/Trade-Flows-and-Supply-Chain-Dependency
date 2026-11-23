# Trade Flows and Supply Chain Dependency

This repository contains the project notebook and knitted report for **DSC3132 theme CNT-12**. It studies India's trade in electronic integrated circuits (HS 8542) using annual bilateral records from the United Nations Comtrade Database. The notebook contains descriptive analysis, a diagnostic decomposition at the HS six-digit level, a predictive forecast for 2026-2028, and a prescriptive supplier-diversification scenario analysis. The finished report is available in both HTML and PDF under `reports/`.

## First analytics stage

- **Type:** Descriptive analytics
- **Question:** How did India's imports and exports of electronic integrated circuits change between 2019 and 2025, and how concentrated were India's imports among supplier countries or areas in the latest year?
- **Source:** [UN Comtrade](https://comtrade.un.org/)
- **Measures:** Annual import and export value, trade balance, supplier shares, HHI, effective supplier count, and top-supplier concentration ratios

## Diagnostic stage

- **Question:** Which changes in supplier economies and HS six-digit product categories account for the growth and changing concentration of India's integrated-circuit imports between 2019 and 2025?
- **Additional data:** Five HS six-digit product categories within HS 8542
- **Methods:** Product growth contribution, supplier-share change, annual HHI, HHI contribution change, and partner-product decomposition

## Predictive stage

- **Question:** What is a reasonable range for India's HS 8542 imports in 2026-2028, and how does it split across HS six-digit categories?
- **Methods:** Log-linear trend fitted to 2022-2025, 80% prediction intervals, holdout validation against 2024-2025, and a full-period sensitivity check
- **Outputs:** 2028 central forecast, category forecast table, backtest errors, and a fan chart

## Prescriptive stage

- **Question:** If India wants to reduce single-supplier concentration in 2028, what supplier mix would meet a given cap, and how large is the required reallocation?
- **Methods:** Supplier-share caps, pro-rata reallocation, HHI and effective-supplier metrics, and required-growth feasibility checks
- **Scenarios:** Baseline 2025 mix, China capped at 30%, every supplier capped at 35%, and every supplier capped at 25%

The source choice, data requirements, access plan, quality checks, analysis, interpretation, and limitations are recorded in `notebooks/Project_Notebook.Rmd`.

## Key findings

- Imports rose from **USD 10.17 billion in 2019 to USD 28.62 billion in 2025** (18.8% CAGR), while exports stayed close to **USD 242 million** and the trade deficit widened to **USD 28.37 billion**.
- In 2025, **China (40.9%)**, **Other Asia, nes (28.1%)**, and **Rep. of Korea (16.0%)** supplied 85.0% of import value. The HHI was **2,752.8**, equivalent to about **3.6 equally sized suppliers**.
- **Processors and controllers** accounted for **61.1%** of the import increase, followed by memories (24.7%), other integrated circuits (16.0%), and amplifiers (3.0%). Imports of parts fell and offset 4.8% of growth elsewhere.
- The headline HHI was almost unchanged between 2019 and 2025, but the annual path was not: it fell to **1,949.5 in 2022** and rose to **3,334.0 in 2023**. Over the period, `Other Asia, nes` gained **27.2 percentage points** and China gained **5.6**, while China, Hong Kong SAR lost **34.2** and Singapore lost **6.4**.
- The shift between Hong Kong and `Other Asia, nes` may reflect trade routing or partner attribution, so the report treats it as a change in declared sourcing rather than proof of physical relocation.
- A log-linear trend fitted to 2022-2025 puts **2028 imports at USD 50.67 billion** (21.0% CAGR), with a wider full-period planning range of **USD 38.61-68.81 billion**. Processors and controllers account for **56.5%** of the 2028 central forecast.
- A universal **35% supplier cap** would require **USD 3.00 billion (5.9%)** of 2028 imports to shift and would lower the HHI to **2,530.2**. A universal **25% cap** would require **USD 9.65 billion (19.0%)** and lower the HHI to **1,962.8**, but alternative suppliers would need about **43.6% annual growth**.
- A targeted **30% cap on China** lowers the HHI to **2,413.7**, but it raises `Other Asia, nes` to **33.3%**, so it swaps one concentration risk for another rather than diversifying the supplier base.

## Repository structure

```text
.
├── data/
│   ├── raw/                    # HS4 and HS6 API downloads and query metadata
│   └── processed/              # Validated analysis datasets
├── notebooks/
│   ├── Project_Notebook.Rmd    # R Markdown notebook with Python analysis
│   └── Project_Notebook.ipynb  # Jupyter version for running cell by cell
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

## Live walkthrough notebook

`notebooks/Project_Notebook.ipynb` is a Jupyter version of the analysis, organized so each step can be run and explained separately. It reads the saved data in `data/raw` and does not download anything.

Register the project environment as a Jupyter kernel:

```bash
.venv\Scripts\python -m ipykernel install --user --name trade-project --display-name "Python 3 (Trade Project)"
```

Then open the notebook in VS Code or Jupyter, select **Python 3 (Trade Project)**, and run the cells from top to bottom. The notebook includes a setup cell, the four analysis stages, a key-results summary, and a troubleshooting note.

## Report outputs

Knitting the notebook produces the report plus the following reproducible outputs:

- `reports/figures/` — eight charts covering trade trends, supplier shares, the trade balance, product contributions, the HHI trend, supplier-share shifts, the 2026-2028 forecast, and the diversification scenarios.
- `reports/tables/` — twelve CSV tables covering the yearly summary, 2025 supplier shares and concentration metrics, product and partner-product growth drivers, HHI by year, supplier concentration drivers, forecast validation and sensitivity, and the prescriptive scenario and supplier-allocation results.
- `data/processed/` — cleaned heading-level and HS6 analysis datasets.

## Data source and scope

The acquisition script calls the official public preview endpoint documented in the [UN Comtrade API guide](https://uncomtrade.org/docs/un-comtrade-api/). It makes one query per year and product, rejects a response that reaches the 500-record preview limit, joins official partner names, and saves exact query URLs in the raw-data metadata files.

The raw datasets contain India-reported annual import and export values for HS 8542 and six-digit import detail from 2019 through 2025. Partner code `0` is the World aggregate; it is used for national totals but excluded from supplier concentration calculations. The five detailed categories reconcile to the published HS 8542 total in every year.

The notebook checks the data before analysis: complete 2019-2025 coverage, one World total per year and flow, no duplicate country-flow-year records, non-negative values, and two reconciliation tests. Non-group bilateral partners must sum to the World total within 0.1%, and the five HS6 categories must sum to the HS 8542 total within 0.001%.

## Limitations

Trade values are in current US dollars and do not isolate price or exchange-rate effects. HS 8542 is an aggregate product group, bilateral trade does not reveal every upstream production dependency, and Comtrade records can be revised after retrieval. The `Other Asia, nes` partner label is retained exactly as published. The predictive model uses a short annual series, so its intervals describe model fit rather than structural breaks or policy changes. The prescriptive scenarios hold the 2028 forecast and the 2025 supplier mix fixed and redistribute capped shares pro rata; they do not model tariffs, logistics, supplier capacity, lead times, or firm-level contracts. The notebook therefore provides a descriptive baseline, a conditional forecast, and accounting-based diversification scenarios rather than a causal model or a firm-level sourcing recommendation.
