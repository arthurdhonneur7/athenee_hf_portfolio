# Athénée Investment — Third-Party Marketing & Capital Introduction Pipeline

This folder contains the automated quantitative analysis and LaTeX PDF tear-sheet generation pipeline for single or multiple hedge funds from `../data/hf_returns/`.

## Folder Structure
- [`pipeline.py`](./pipeline.py): Core Python module and CLI script that loads selected fund CSVs from `../data/hf_returns/`, computes the full `single_fund_analysis` indicator suite, builds the Year $\times$ Month + Yearly return matrix, and compiles the 2-page modern LaTeX PDF tear sheet.
- [`tearsheet_pipeline.ipynb`](./tearsheet_pipeline.ipynb): Interactive Jupyter Notebook to select funds by CSV name and generate single or batch tear sheets in one click.
- [`athenee_logo.png`](./athenee_logo.png): Official Athénée Investment logo embedded in the PDF header.
- [`output/`](./output/): Generated `.pdf` tear sheets, `.tex` source files, `<fund>_return_matrix.csv`, `<fund>_metrics.csv`, and `summary_selected_funds_metrics.csv`.

---

## Quick Usage

### 1. Via Jupyter Notebook
Open [`tearsheet_pipeline.ipynb`](./tearsheet_pipeline.ipynb), edit the `SELECTED_FUNDS` list with the CSV names of the funds from `../data/hf_returns/` (with or without `.csv`), and run all cells:
```python
SELECTED_FUNDS = [
    'dcm_systematic',
    'smithson',
    '26_miles',
    'adar1',
    'h3im',
    'sam_capital',
]
```

### 2. Via Command Line (Single Fund, Multiple Funds, or All Funds)
```bash
# Single fund
python3 third_party_marketing/pipeline.py --funds dcm_systematic

# Multiple funds in one shot
python3 third_party_marketing/pipeline.py --funds dcm_systematic smithson 26_miles adar1 h3im sam_capital

# All funds in data/hf_returns/ in one shot
python3 third_party_marketing/pipeline.py --funds all

# List all available fund CSV names
python3 third_party_marketing/pipeline.py --list-funds
```

### 3. Via Python Import
```python
from third_party_marketing.pipeline import run_fund_pipeline, run_batch_pipeline

# Generate for a single fund
res = run_fund_pipeline("dcm_systematic")

# Generate for multiple funds in one shot using the exact same model
summary = run_batch_pipeline(["dcm_systematic", "smithson", "26_miles"])
```

