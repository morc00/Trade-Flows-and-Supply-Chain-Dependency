# Trade Flows and Supply Chain Dependency

This repository contains an analytical pipeline to map a country's import and export flows for a chosen sector, identify concentration risks, and quantify exposure to tariff or disruption shocks.

## 🎯 Framed Business Question

"What is the concentration risk of supplier countries for a chosen sector's import/export flows, and how does exposure to tariff or supply chain disruption shocks impact a firm's operational stability? What diversification strategies can mitigate these risks?"

## 📂 Repository Structure

```
Trade-Flows-and-Supply-Chain-Dependency/
├── notebooks/                   # Source RMarkdown notebooks (Python engines)
│   ├── 01_data_prep.Rmd         # Modular data preparation & cleaning
│   ├── 02_eda.Rmd               # Exploratory data analysis & visualization
│   └── Analysis.Rmd             # Concentration risk & shock exposure modeling
├── data/
│   ├── raw/                     # Raw dataset (acquired by script)
│   └── processed/               # Cleaned & feature-engineered dataset
├── scripts/
│   └── data_acquisition.py      # Connects to database to extract trade flows
├── reports/                     # Output directory for rendered HTML/PDF reports
├── requirements.txt             # Python dependencies
└── README.md                    # Project overview
```

## ⚡ Quickstart & Reproducibility Guide

### 1. Set Up Environment
Ensure you have R, RStudio, and Python installed. Install the Python dependencies:
```bash
pip install -r requirements.txt
```
*Note: The RMarkdown files use the `reticulate` library to run Python code blocks natively.*

### 2. Acquire Data
```bash
python scripts/data_acquisition.py
```

### 3. Run Analysis
Open `notebooks/01_data_prep.Rmd`, `notebooks/02_eda.Rmd`, and `notebooks/Analysis.Rmd` in RStudio or any compatible IDE, and Knit the files to generate HTML/PDF reports into the `reports/` directory.

## 📊 Summary of Key Components
1. **Data Acquisition**: The Python script extracts and processes global semiconductor trade records, embedding tariff rates and disruption risk scores.
2. **Data Cleaning (Python/Pandas)**: Data structures are validated and processed.
3. **Exploratory Data Analysis**: Visualizes global trade volumes and pinpoints major industry players.
4. **Concentration Risk (HHI)**: Calculates the Herfindahl-Hirschman Index to warn against monopolistic supply dependencies.
5. **Shock Exposure**: Models hypothetical risk exposure by weighting market share against disruption risk scores, feeding directly into actionable firm-level recommendations.
