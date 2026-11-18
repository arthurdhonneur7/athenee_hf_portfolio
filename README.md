# Athénée Investment — Hedge Fund Research, TPM & Portfolio Construction

Institutional repository for **Athénée Investment**, structured around three core pillars:
1. **Third-Party Marketing (TPM) & Capital Introduction** ([`third_party_marketing/`](./third_party_marketing/))
2. **Hedge Fund Research & Due Diligence** ([`hf_research/`](./hf_research/))
3. **Quantitative Portfolio Research & Allocation** ([`portfolio_research/`](./portfolio_research/) and [`allocation/`](./allocation/))

---

## Repository Architecture

```text
athenee_hf_pflio/
├── third_party_marketing/                        # 1. Third-Party Marketing (TPM) Activity
│   ├── pipeline.py                               # Automated tear-sheet PDF & Excel workbook generator
│   ├── tearsheet_pipeline.ipynb                  # Interactive Jupyter dashboard for TPM tear-sheets
│   ├── fund_database.csv                         # Fund commercial terms, vehicle structure & metadata
│   ├── confidential_fund_mapping.csv             # Deterministic anonymized code/name mapping
│   ├── list.md                                   # TPM pipeline notes
│   └── output/                                   # Timestamped TPM batch runs (PDF factsheets & Excel)
│
├── hf_research/                                  # 2. Hedge Fund Due Diligence & Universe Research
│   ├── single_fund_analysis/                     # Single-manager deep dives & regression templates
│   │   ├── general_analysis.ipynb                # Standard monthly quantitative due-diligence suite
│   │   ├── daily_general_analysis.ipynb          # Daily return quantitative due-diligence suite
│   │   ├── cambrian.ipynb                        # Cambrian vs. BTC/ETH factor regression analysis
│   │   ├── gator.ipynb                           # Gator fund isolated performance & factor analysis
│   │   └── sp500_analysis.ipynb                  # S&P 500 benchmark statistical & regime analysis
│   │
│   ├── group_fund_analysis/                      # Thematic & multi-fund group comparisons
│   │   ├── coban_analysis/                       # Coban pods & multi-manager shortlist + pitch decks
│   │   ├── qlumina_analysis/                     # Qlumina multi-pod analysis, fee restructuring & allocation
│   │   ├── wizard_comparison/                    # Wizard Quant Onshore vs. Offshore comparison
│   │   ├── indian_funds/                         # Indian quantitative & market-neutral fund universe
│   │   └── ucits/                                # Alternative UCITS fund universe & ISIN list
│   │
│   └── cap_intro_scraping/                       # Prime Broker Capital Introduction platform databases
│       ├── jpm/                                  # J.P. Morgan Cap Intro scraping & screening
│       ├── bnp/                                  # BNP Paribas Cap Intro scraping & screening
│       ├── ms/                                   # Morgan Stanley Cap Intro scraping & screening
│       ├── sg/                                   # Société Générale Nelson Report & strategy breakdown
│       └── archive/                              # Historical JPM & Fama-French time-series archives
│
├── portfolio_research/                           # 3. Quantitative FoF Research & Benchmarking
│   ├── train_test_analysis/                      # Out-of-sample (IS/OOS) persistence & selection research
│   │   ├── jpm_train_test.ipynb                  # JPM Cap Intro train/test split Monte Carlo
│   │   ├── jpm_train_test_v2.ipynb               # JPM train/test split with correlation cutoffs & surfaces
│   │   ├── bnp_train_test.ipynb                  # BNP Cap Intro train/test split Monte Carlo
│   │   ├── ms_train_test.ipynb                   # Morgan Stanley Cap Intro train/test split Monte Carlo
│   │   └── old_analysis/                         # Legacy bootstrap train/test experiments (JPM & HFR)
│   │
│   ├── portfolio_testing_and_benchmarking/       # Experimental & benchmark portfolio weighting schemes
│   │   ├── ew_portfolio.ipynb                    # Equal-Weight (EW) benchmark portfolio analysis
│   │   ├── custom_ew_portfolio.ipynb             # Custom subset Equal-Weight portfolio tester
│   │   ├── vol_based_pflio.ipynb                 # Inverse-Volatility (1/vol) portfolio benchmark
│   │   ├── vol_analysis.ipynb                    # Cross-fund annualized return vs. volatility screening
│   │   └── correlation_analysis.ipynb            # Unconditional & S&P 500 stress-regime correlations
│   │
│   └── diversification_and_bootstrap/            # Theoretical diversification & bootstrap simulations
│       ├── mc_diversification_sim.ipynb          # Monte Carlo N-asset Gaussian diversification simulation
│       ├── bootstrap_enb.ipynb                   # Expected Number of Bets (ENB/N) effective breadth study
│       ├── portfolio_bootstrap.ipynb             # Random portfolio bootstrap comparison (EW vs. Inv-Vol)
│       └── portfolio_block_bootstrap_b3.ipynb    # Stationary block bootstrap (b=3) tail-risk testing
│
├── allocation/                                   # 4. Live Fund of Funds Allocation & Implementation
│   ├── target_portfolio/                         # Target FoF portfolio construction & rebalancing models
│   │   └── target_pflio.ipynb                    # Lazarus target portfolio model & LaTeX report builder
│   ├── day_1_allocation/                         # Day-1 deployment shortlists & PM status
│   │   └── initial_chioce.md                     # Initial investable universe & tiering notes
│   └── execution_tools/                          # Execution & brokerage helpers
│       └── ibkr_fill.ipynb                       # Interactive Brokers bid/ask spread & mid-price tool
│
├── data/                                         # 5. Central Data Warehouse
│   ├── data_building.ipynb                       # Master ETL notebook ingesting raw fund track records
│   ├── concat.ipynb                              # Monthly return matrix builder -> concat_hf_data.csv
│   ├── concat_daily.ipynb                        # Daily return matrix builder -> concat_hf_data_daily.csv
│   ├── concat_hf_data.csv                        # Consolidated monthly returns across all tracked funds
│   ├── concat_hf_data_daily.csv                  # Consolidated daily returns
│   ├── hf_metadata.csv                           # Synchronized fund metadata & commercial terms
│   ├── hf_returns/                               # Individual fund monthly return CSVs (77+ funds)
│   ├── hf_returns_daily/                         # Individual fund daily return CSVs
│   └── portfolios/                               # Saved benchmark portfolio return series (EW, Inv-Vol)
│
└── report/                                       # 6. Generated Investor Presentations & Whitepapers
    ├── lazarus/                                  # Technical presentation & figures built by target_pflio.ipynb
    ├── lazarus_admin/                            # One-pager summary presentation built by target_pflio.ipynb
    └── educational/                              # Theoretical & empirical diversification whitepapers
        ├── educational_easier/                   # Concise investor FoF report (fof_report.tex)
        └── education_hard/                       # Full quantitative technical whitepaper (report.tex)
```

---

## Core Workflows

### 1. Adding or Updating a Fund Track Record
1. Add or update the fund's cell in [`data/data_building.ipynb`](./data/data_building.ipynb) (saves to `data/hf_returns/<fund>.csv` and syncs metadata with `third_party_marketing/fund_database.csv`).
2. Run [`data/concat.ipynb`](./data/concat.ipynb) to refresh `data/concat_hf_data.csv`.

### 2. Third-Party Marketing (TPM) Tear Sheets & Excel Workbooks
- **Interactive UI**: Open [`third_party_marketing/tearsheet_pipeline.ipynb`](./third_party_marketing/tearsheet_pipeline.ipynb).
- **CLI**:
  ```bash
  python3 third_party_marketing/pipeline.py --funds dcm_systematic smithson 26_miles
  ```

### 3. Running Target Portfolio & Updating Lazarus Presentations
- Open [`allocation/target_portfolio/target_pflio.ipynb`](./allocation/target_portfolio/target_pflio.ipynb) and run all cells to recompute portfolio statistics, export charts, and compile `report/lazarus/presentation.pdf` and `report/lazarus_admin/presentation.pdf`.
