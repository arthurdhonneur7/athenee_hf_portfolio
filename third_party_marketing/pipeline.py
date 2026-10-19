"""
Athénée Investment — Third-Party Marketing & Capital Introduction Tear Sheet Pipeline
=====================================================================================
Selects one or multiple hedge funds from `data/hf_returns/` using their CSV names,
computes the full `single_fund_analysis` quantitative metrics suite against the S&P 500
(and cross-asset benchmarks WTI & BTC), and compiles a modern 2-page LaTeX PDF:
  - Page 1: Institutional One-Pager Tear Sheet (Logo, Quantitative Indicators, Monthly Return Matrix)
  - Page 2: Quantitative Appendix, Extended Diagnostics & Capital Introduction Risk / Legal Disclaimer
"""

import os
import sys
import csv
import glob
import math
import shutil
import random
import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Union, Tuple, Any

# ---------------------------------------------------------------------------
# Directory & Path Configuration
# ---------------------------------------------------------------------------
THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
HF_RETURNS_DIR = PROJECT_ROOT / "data" / "hf_returns"
CONCAT_DATA_PATH = PROJECT_ROOT / "data" / "concat_hf_data.csv"
DEFAULT_OUTPUT_DIR = THIS_DIR / "output"
LOGO_PATH = THIS_DIR / "athenee_logo.png"

MONTH_ABBR = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Optional human-readable metadata for known funds (automatically falls back to clean title-case)
FUND_DISPLAY_NAMES: Dict[str, str] = {
    "dcm_systematic": "DCM Systematic",
    "quantstream": "Quantstream Volatility Strategy",
    "m1": "M1 Crypto Carry Strategy",
    "vadantia": "Vadantia Quant FX & Metals",
    "arr": "ARR Equity Trading Strategy",
    "r_squared": "R-Squared Futures Arbitrage",
    "shiprock": "Shiprock Distressed Credit",
    "smithson": "Smithson Systematic Multi-Asset",
    "26_miles": "26 Miles Quant Indian Strategy",
    "adar1": "Adar1 Biotech Strategy",
    "grasshoper": "Grasshopper Quant HFT",
    "wizard_quant": "Wizard Quant Market Neutral",
    "wizard_quant_offshore": "Wizard Quant Offshore",
    "h3im": "H3IM FX Swap Arbitrage",
    "sam_capital": "SAM Capital Systematic Global Macro",
    "cinctive": "Cinctive Multi-Manager",
    "schonfeld_equity": "Schonfeld Fundamental Equity",
    "boothbay": "Boothbay Absolute Return",
    "cambrian": "Cambrian Digital Strategy",
    "gator": "Gator Financial Strategy",
    "winton": "Winton Systematic Strategy",
    "graham": "Graham Tactical Trend",
    "brummer": "Brummer Multi-Strategy",
    "cevian": "Cevian Constructive Activist",
    "enko": "Enko Macro Fixed Income",
    "aqua_lake": "Aqua Lake Quantitative Strategy",
    "anvik": "Anvik Quantitative Strategy",
    "edge_capital": "Edge Capital Market Neutral",
    "coban_edge_capital": "Coban Edge Capital",
    "coban_orca": "Coban ORCA Strategy",
    "coban_clarion_multi_asset": "Coban Clarion Multi-Asset",
    "coban_arkis_ls_alpha": "Coban Arkis Long/Short Alpha",
    "coban_amount_abs_ret": "Coban Amont Absolute Return",
    "coban_plettenberg": "Coban Plettenberg Strategy",
    "coban_pod_1": "Coban Multi-Manager Pod 1",
    "coban_pod_2": "Coban Multi-Manager Pod 2",
    "blackrock_sta": "BlackRock Systematic Total Alpha",
    "spear_digital": "Spear Digital Asset Strategy",
    "agt_partners": "AGT Partners Strategy",
}

FUND_STRATEGY_SUBTITLES: Dict[str, str] = {
    "dcm_systematic": "Systematic Multi-Asset & Diversified Quantitative Strategy",
    "quantstream": "Systematic Commodity Volatility Selling Strategy",
    "m1": "Market-Neutral Digital Asset Carry Trade Strategy",
    "vadantia": "Quantitative High-Velocity FX & Precious Metals Trading",
    "arr": "Tactical Equity Trading & Relative Value Strategy",
    "r_squared": "Dividend Futures & Index Futures Quantitative Arbitrage",
    "shiprock": "Event-Driven & Distressed Corporate Debt Strategy",
    "smithson": "Systematic Multi-Asset Absolute Return Strategy",
    "26_miles": "Quantitative Medium-Frequency Multi-Asset Strategy",
    "adar1": "Specialist Healthcare & Biotechnology Long/Short Strategy",
    "grasshoper": "High-Frequency Quantitative Market-Making & Alpha Strategy",
    "wizard_quant": "Quantitative Equity Market-Neutral Strategy",
    "h3im": "Systematic G10 & EM FX Swap Arbitrage Strategy",
    "sam_capital": "Systematic Global Macro Strategy",
}


def format_fund_title(csv_name: str) -> str:
    """Convert a CSV stem (e.g., 'dcm_systematic') into a clean display title."""
    stem = csv_name.replace(".csv", "").strip()
    if stem in FUND_DISPLAY_NAMES:
        return FUND_DISPLAY_NAMES[stem]
    return stem.replace("_", " ").title()


def format_fund_subtitle(csv_name: str) -> str:
    """Return strategy subtitle for a given CSV stem."""
    stem = csv_name.replace(".csv", "").strip()
    return FUND_STRATEGY_SUBTITLES.get(
        stem, "Institutional Alternative Investment Strategy — Quantitative Performance Analysis"
    )


def find_pdflatex() -> Optional[str]:
    """Locate pdflatex binary on macOS / Linux."""
    candidates = [
        shutil.which("pdflatex"),
        "/Users/arthurdhonneur/Library/TinyTeX/bin/universal-darwin/pdflatex",
        "/Library/TeX/texbin/pdflatex",
        "/opt/homebrew/bin/pdflatex",
        "/usr/local/bin/pdflatex",
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None


def list_available_funds(hf_returns_dir: Path = HF_RETURNS_DIR) -> List[str]:
    """List all available fund CSV names (without .csv extension) in data/hf_returns/."""
    excluded = {"sp500", "btc", "wti", "vix"}
    files = sorted(glob.glob(str(hf_returns_dir / "*.csv")))
    return [
        os.path.splitext(os.path.basename(f))[0]
        for f in files
        if os.path.splitext(os.path.basename(f))[0] not in excluded
    ]


# ---------------------------------------------------------------------------
# Step 1: Data Loading & Monthly Alignment
# ---------------------------------------------------------------------------
def _parse_ym(date_str: str) -> Optional[Tuple[int, int]]:
    """Parse 'YYYY-MM' or 'YYYY-MM-DD' into (year, month) tuple."""
    s = date_str.strip()
    if not s:
        return None
    parts = s.split("-")
    if len(parts) >= 2:
        try:
            return (int(parts[0]), int(parts[1]))
        except ValueError:
            pass
    for fmt in ("%Y/%m/%d", "%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d %H:%M:%S"):
        try:
            dt = datetime.strptime(s, fmt)
            return (dt.year, dt.month)
        except ValueError:
            continue
    return None


def _read_monthly_csv(csv_path: Path) -> Dict[Tuple[int, int], float]:
    """Read a 2-column CSV (Date/Period, Return) and normalize to {(year, month): mean_return}."""
    buckets: Dict[Tuple[int, int], List[float]] = {}
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for row in reader:
            if not row or len(row) < 2:
                continue
            ym = _parse_ym(row[0])
            if ym is None:
                continue
            try:
                val = float(row[1])
                if not math.isnan(val):
                    buckets.setdefault(ym, []).append(val)
            except ValueError:
                continue
    return {ym: sum(vals) / len(vals) for ym, vals in sorted(buckets.items())}


def load_fund_and_benchmarks(
    fund_csv_name: str,
    hf_returns_dir: Path = HF_RETURNS_DIR,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    leverage: Optional[float] = None,
    annual_financing_cost: float = 0.0,
) -> List[Dict[str, Any]]:
    """
    Load a selected fund by its CSV name from `data/hf_returns/` along with S&P 500,
    WTI, and BTC benchmark returns, aligned on monthly periods.
    """
    stem = fund_csv_name.replace(".csv", "").strip()
    fund_path = Path(hf_returns_dir) / f"{stem}.csv"
    if not fund_path.exists():
        raise FileNotFoundError(f"Fund CSV '{stem}.csv' not found in {hf_returns_dir}")

    fund_map = _read_monthly_csv(fund_path)
    if leverage is not None and leverage != 1.0:
        fund_map = {ym: r * leverage - (annual_financing_cost / 12.0) for ym, r in fund_map.items()}

    sp500_path = Path(hf_returns_dir) / "sp500.csv"
    if not sp500_path.exists():
        raise FileNotFoundError(f"Benchmark 'sp500.csv' not found in {hf_returns_dir}")
    sp500_map = _read_monthly_csv(sp500_path)

    wti_path = Path(hf_returns_dir) / "wti.csv"
    wti_map = _read_monthly_csv(wti_path) if wti_path.exists() else {}

    btc_path = Path(hf_returns_dir) / "btc.csv"
    btc_map = _read_monthly_csv(btc_path) if btc_path.exists() else {}

    start_ym = _parse_ym(start_date) if start_date else None
    end_ym = _parse_ym(end_date) if end_date else None

    common_yms = sorted(set(fund_map.keys()).intersection(sp500_map.keys()))
    if start_ym:
        common_yms = [ym for ym in common_yms if ym >= start_ym]
    if end_ym:
        common_yms = [ym for ym in common_yms if ym <= end_ym]

    if not common_yms:
        raise ValueError(f"No overlapping monthly observations between '{stem}' and 'sp500'.")

    records = []
    for ym in common_yms:
        records.append(
            {
                "ym": ym,
                "year": ym[0],
                "month": ym[1],
                "fund": fund_map[ym],
                "sp500": sp500_map[ym],
                "wti": wti_map.get(ym, math.nan),
                "btc": btc_map.get(ym, math.nan),
            }
        )
    return records


# ---------------------------------------------------------------------------
# Step 2: Quantitative Metrics Engine (`single_fund_analysis` Framework)
# ---------------------------------------------------------------------------
def _mean(xs: List[float]) -> float:
    return sum(xs) / len(xs) if xs else math.nan


def _std_sample(xs: List[float]) -> float:
    n = len(xs)
    if n < 2:
        return math.nan
    m = sum(xs) / n
    var = sum((x - m) ** 2 for x in xs) / (n - 1)
    return math.sqrt(var)


def _quantile_linear(xs: List[float], q: float) -> float:
    """Exact match to pandas/numpy linear quantile interpolation."""
    if not xs:
        return math.nan
    s = sorted(xs)
    n = len(s)
    if n == 1:
        return s[0]
    pos = q * (n - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return s[lo]
    weight = pos - lo
    return s[lo] * (1.0 - weight) + s[hi] * weight


def _ranks_avg_ties(xs: List[float]) -> List[float]:
    """Compute average-tie ranks (1-based) for Spearman correlation."""
    n = len(xs)
    indexed = sorted(enumerate(xs), key=lambda t: t[1])
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and indexed[j + 1][1] == indexed[i][1]:
            j += 1
        avg_rank = (i + j + 2) / 2.0
        for k in range(i, j + 1):
            ranks[indexed[k][0]] = avg_rank
        i = j + 1
    return ranks


def _pearson(xs: List[float], ys: List[float]) -> float:
    n = len(xs)
    if n < 2 or len(ys) != n:
        return math.nan
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx <= 0 or syy <= 0:
        return math.nan
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    return max(-1.0, min(1.0, sxy / math.sqrt(sxx * syy)))


def _spearman(xs: List[float], ys: List[float]) -> float:
    if len(xs) < 2 or len(ys) != len(xs):
        return math.nan
    return _pearson(_ranks_avg_ties(xs), _ranks_avg_ties(ys))


def _ols_simple(ys: List[float], xs: List[float]) -> Tuple[float, float, float, float, float]:
    """
    OLS regression y = const + beta * x.
    Returns (annualized_alpha, alpha_tstat, beta, beta_tstat, r_squared).
    Matches statsmodels `sm.OLS(y, sm.add_constant(x)).fit()` exactly.
    """
    n = len(ys)
    if n < 3 or len(xs) != n:
        return (math.nan, math.nan, math.nan, math.nan, math.nan)
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx <= 0:
        return (math.nan, math.nan, math.nan, math.nan, math.nan)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    beta = sxy / sxx
    alpha_m = my - beta * mx
    alpha_ann = alpha_m * 12.0

    ssr = sum((y - (alpha_m + beta * x)) ** 2 for x, y in zip(xs, ys))
    r2 = 1.0 - (ssr / syy) if syy > 0 else math.nan

    s2 = ssr / (n - 2)
    if s2 > 0:
        se_beta = math.sqrt(s2 / sxx)
        se_alpha = math.sqrt(s2 * (1.0 / n + (mx ** 2) / sxx))
        t_beta = beta / se_beta if se_beta > 0 else math.nan
        t_alpha = alpha_m / se_alpha if se_alpha > 0 else math.nan
    else:
        t_beta = math.nan
        t_alpha = math.nan

    return (alpha_ann, t_alpha, beta, t_beta, r2)


def _bootstrap_corr_ci(
    xs: List[float],
    ys: List[float],
    method: str = "pearson",
    block_size: int = 1,
    iters: int = 1000,
    seed: int = 42,
) -> Tuple[float, float]:
    """Compute 95% confidence interval for correlation via IID or Moving-Block Bootstrap."""
    n = len(xs)
    if n < 6 or (block_size > 1 and n <= block_size):
        return (math.nan, math.nan)
    rng = random.Random(seed)
    corrs: List[float] = []
    num_blocks = int(math.ceil(n / block_size)) if block_size > 1 else n

    for _ in range(iters):
        if block_size <= 1:
            idx = [rng.randrange(n) for _ in range(n)]
        else:
            starts = [rng.randrange(n - block_size + 1) for _ in range(num_blocks)]
            idx = [s + offset for s in starts for offset in range(block_size)][:n]
        xb = [xs[i] for i in idx]
        yb = [ys[i] for i in idx]
        c = _spearman(xb, yb) if method == "spearman" else _pearson(xb, yb)
        if not math.isnan(c):
            corrs.append(c)

    if not corrs:
        return (math.nan, math.nan)
    return (_quantile_linear(corrs, 0.025), _quantile_linear(corrs, 0.975))


def _ljung_box_1_3(xs: List[float]) -> Tuple[float, float, float, float]:
    """
    Compute Ljung-Box Q-statistics and exact chi-square p-values at Lags 1 and 3.
    Returns (lb_stat_1, lb_pval_1, lb_stat_3, lb_pval_3).
    """
    n = len(xs)
    if n < 6:
        return (math.nan, math.nan, math.nan, math.nan)
    m = sum(xs) / n
    denom = sum((x - m) ** 2 for x in xs)
    if denom <= 0:
        return (math.nan, math.nan, math.nan, math.nan)

    def acf(k: int) -> float:
        return sum((xs[t] - m) * (xs[t - k] - m) for t in range(k, n)) / denom

    r1 = acf(1)
    q1 = n * (n + 2) * ((r1 ** 2) / (n - 1))
    # Chi-square df=1 survival function: erfc(sqrt(q1 / 2))
    p1 = math.erfc(math.sqrt(max(0.0, q1) / 2.0))

    r2 = acf(2)
    r3 = acf(3)
    q3 = n * (n + 2) * (
        (r1 ** 2) / (n - 1) + (r2 ** 2) / (n - 2) + (r3 ** 2) / (n - 3)
    )
    # Chi-square df=3 survival function: erfc(sqrt(x/2)) + sqrt(2x/pi) * exp(-x/2)
    q3_pos = max(0.0, q3)
    p3 = math.erfc(math.sqrt(q3_pos / 2.0)) + math.sqrt(2.0 * q3_pos / math.pi) * math.exp(-q3_pos / 2.0)
    p3 = min(1.0, max(0.0, p3))

    return (q1, p1, q3, p3)


def _core_series_stats(rets: List[float]) -> Dict[str, float]:
    """Compute CAGR, Mean, Vol, Sharpe, Sortino, MDD, Calmar, Best/Worst month for a return series."""
    n = len(rets)
    if n == 0:
        return {}
    n_years = n / 12.0
    mean_ann = _mean(rets) * 12.0
    vol_ann = _std_sample(rets) * math.sqrt(12.0) if n > 1 else math.nan
    sharpe = mean_ann / vol_ann if (not math.isnan(vol_ann) and vol_ann > 0) else math.nan

    downside_sq = [min(0.0, r) ** 2 for r in rets]
    downside_dev = math.sqrt(sum(downside_sq) / n) * math.sqrt(12.0)
    sortino = mean_ann / downside_dev if downside_dev > 0 else math.nan

    wealth = 1.0
    peak = -math.inf
    mdd = 0.0
    for r in rets:
        wealth *= (1.0 + r)
        if wealth > peak:
            peak = wealth
        dd = (wealth - peak) / peak if peak > 0 else 0.0
        if dd < mdd:
            mdd = dd

    cum_ret = wealth - 1.0
    cagr = (wealth ** (1.0 / n_years) - 1.0) if (n_years > 0 and wealth > 0) else math.nan
    calmar = (cagr / abs(mdd)) if (not math.isnan(cagr) and mdd < 0) else math.nan

    return {
        "cagr": cagr,
        "ann_mean": mean_ann,
        "ann_vol": vol_ann,
        "sharpe": sharpe,
        "sortino": sortino,
        "mdd": mdd,
        "calmar": calmar,
        "cum_ret": cum_ret,
        "best_month": max(rets),
        "worst_month": min(rets),
    }


def compute_single_fund_metrics(records: List[Dict[str, Any]], fund_col: str) -> Dict[str, Any]:
    """
    Compute the complete `single_fund_analysis` indicator suite for `fund_col` vs `sp500`
    (plus WTI and BTC cross-asset regressions and Ljung-Box serial correlation diagnostics).
    """
    fund = [r["fund"] for r in records]
    sp500 = [r["sp500"] for r in records]
    n_months = len(records)

    start_ym = records[0]["ym"]
    end_ym = records[-1]["ym"]
    start_date_str = f"{MONTH_ABBR[start_ym[1] - 1]} {start_ym[0]}"
    end_date_str = f"{MONTH_ABBR[end_ym[1] - 1]} {end_ym[0]}"
    n_years = n_months / 12.0

    f_core = _core_series_stats(fund)
    s_core = _core_series_stats(sp500)

    # Hit Rates & Conditional Hit Rates
    fund_pos_count = sum(1 for r in fund if r > 0)
    sp500_pos_count = sum(1 for s in sp500 if s > 0)
    fund_pos_rate = fund_pos_count / n_months if n_months > 0 else math.nan
    sp500_pos_rate = sp500_pos_count / n_months if n_months > 0 else math.nan

    up_pairs = [(f, s) for f, s in zip(fund, sp500) if s > 0]
    down_pairs = [(f, s) for f, s in zip(fund, sp500) if s < 0]
    n_sp500_pos = len(up_pairs)
    n_sp500_neg = len(down_pairs)

    fund_pos_when_sp500_neg = sum(1 for f, _ in down_pairs if f > 0)
    fund_neg_when_sp500_pos = sum(1 for f, _ in up_pairs if f < 0)

    crisis_hit_rate = fund_pos_when_sp500_neg / n_sp500_neg if n_sp500_neg > 0 else math.nan
    up_loss_rate = fund_neg_when_sp500_pos / n_sp500_pos if n_sp500_pos > 0 else math.nan

    # Capture Ratios
    up_capture = (
        _mean([f for f, _ in up_pairs]) / _mean([s for _, s in up_pairs])
        if n_sp500_pos > 0 and _mean([s for _, s in up_pairs]) != 0
        else math.nan
    )
    down_capture = (
        _mean([f for f, _ in down_pairs]) / _mean([s for _, s in down_pairs])
        if n_sp500_neg > 0 and _mean([s for _, s in down_pairs]) != 0
        else math.nan
    )

    # Correlations, Bootstrap CIs & OLS Regression
    pearson_corr = _pearson(fund, sp500)
    spearman_corr = _spearman(fund, sp500)

    pearson_std_ci = _bootstrap_corr_ci(fund, sp500, method="pearson", block_size=1)
    pearson_blk_ci = _bootstrap_corr_ci(fund, sp500, method="pearson", block_size=3)
    spearman_std_ci = _bootstrap_corr_ci(fund, sp500, method="spearman", block_size=1)
    spearman_blk_ci = _bootstrap_corr_ci(fund, sp500, method="spearman", block_size=3)
    worst_case_corr = max(-1.0, min(1.0, pearson_blk_ci[1])) if not math.isnan(pearson_blk_ci[1]) else math.nan

    alpha, alpha_tstat, beta, beta_tstat, r_squared = _ols_simple(fund, sp500)

    # Conditional Up/Down Market Regressions
    up_alpha, up_alpha_t, up_beta, up_beta_t, _ = _ols_simple(
        [f for f, _ in up_pairs], [s for _, s in up_pairs]
    )
    down_alpha, down_alpha_t, down_beta, down_beta_t, _ = _ols_simple(
        [f for f, _ in down_pairs], [s for _, s in down_pairs]
    )

    # Tail Correlations (SP500 < 1st Decile & 1st Quartile)
    decile_1 = _quantile_linear(sp500, 0.10)
    d1_pairs = [(f, s) for f, s in zip(fund, sp500) if s < decile_1]
    n_d1 = len(d1_pairs)
    d1_pearson = _pearson([f for f, _ in d1_pairs], [s for _, s in d1_pairs]) if n_d1 > 2 else math.nan
    d1_spearman = _spearman([f for f, _ in d1_pairs], [s for _, s in d1_pairs]) if n_d1 > 2 else math.nan

    quartile_1 = _quantile_linear(sp500, 0.25)
    q1_pairs = [(f, s) for f, s in zip(fund, sp500) if s < quartile_1]
    n_q1 = len(q1_pairs)
    q1_pearson = _pearson([f for f, _ in q1_pairs], [s for _, s in q1_pairs]) if n_q1 > 2 else math.nan
    q1_spearman = _spearman([f for f, _ in q1_pairs], [s for _, s in q1_pairs]) if n_q1 > 2 else math.nan

    # Worst 20% SP500 Months Average Return
    q20_sp500 = _quantile_linear(sp500, 0.20)
    w20_pairs = [(f, s) for f, s in zip(fund, sp500) if s <= q20_sp500]
    worst20_fund_mean = _mean([f for f, _ in w20_pairs]) if w20_pairs else math.nan
    worst20_sp500_mean = _mean([s for _, s in w20_pairs]) if w20_pairs else math.nan

    # Cross-Asset Factor Regressions (WTI & BTC)
    wti_pairs = [(r["fund"], r["wti"]) for r in records if not math.isnan(r["wti"])]
    if len(wti_pairs) > 10:
        wti_alpha, wti_alpha_t, wti_beta, wti_beta_t, _ = _ols_simple(
            [f for f, _ in wti_pairs], [w for _, w in wti_pairs]
        )
        wti_corr = _pearson([f for f, _ in wti_pairs], [w for _, w in wti_pairs])
    else:
        wti_alpha = wti_alpha_t = wti_beta = wti_beta_t = wti_corr = math.nan

    btc_pairs = [(r["fund"], r["btc"]) for r in records if not math.isnan(r["btc"])]
    if len(btc_pairs) > 10:
        btc_alpha, btc_alpha_t, btc_beta, btc_beta_t, _ = _ols_simple(
            [f for f, _ in btc_pairs], [b for _, b in btc_pairs]
        )
        btc_corr = _pearson([f for f, _ in btc_pairs], [b for _, b in btc_pairs])
    else:
        btc_alpha = btc_alpha_t = btc_beta = btc_beta_t = btc_corr = math.nan

    # Ljung-Box Autocorrelation
    lb_lag1_stat, lb_lag1_pval, lb_lag3_stat, lb_lag3_pval = _ljung_box_1_3(fund)

    return {
        "fund_col": fund_col,
        "start_date": start_date_str,
        "end_date": end_date_str,
        "start_ym": f"{start_ym[0]:04d}-{start_ym[1]:02d}",
        "end_ym": f"{end_ym[0]:04d}-{end_ym[1]:02d}",
        "n_months": n_months,
        "years_elapsed": n_years,
        # Core performance & risk
        "cagr": f_core["cagr"],
        "ann_mean": f_core["ann_mean"],
        "ann_vol": f_core["ann_vol"],
        "sharpe": f_core["sharpe"],
        "sortino": f_core["sortino"],
        "mdd": f_core["mdd"],
        "calmar": f_core["calmar"],
        "cum_ret": f_core["cum_ret"],
        "best_month": f_core["best_month"],
        "worst_month": f_core["worst_month"],
        # SP500 Benchmark
        "sp_cagr": s_core["cagr"],
        "sp_ann_mean": s_core["ann_mean"],
        "sp_ann_vol": s_core["ann_vol"],
        "sp_sharpe": s_core["sharpe"],
        "sp_sortino": s_core["sortino"],
        "sp_mdd": s_core["mdd"],
        "sp_calmar": s_core["calmar"],
        "sp_cum_ret": s_core["cum_ret"],
        "sp_best_month": s_core["best_month"],
        "sp_worst_month": s_core["worst_month"],
        # Hit rates
        "fund_pos_count": fund_pos_count,
        "fund_pos_rate": fund_pos_rate,
        "sp500_pos_count": sp500_pos_count,
        "sp500_pos_rate": sp500_pos_rate,
        "n_sp500_neg": n_sp500_neg,
        "n_sp500_pos": n_sp500_pos,
        "fund_pos_when_sp500_neg": fund_pos_when_sp500_neg,
        "crisis_hit_rate": crisis_hit_rate,
        "fund_neg_when_sp500_pos": fund_neg_when_sp500_pos,
        "up_loss_rate": up_loss_rate,
        # Capture ratios
        "up_capture": up_capture,
        "down_capture": down_capture,
        # Regressions & correlations
        "alpha": alpha,
        "alpha_tstat": alpha_tstat,
        "beta": beta,
        "beta_tstat": beta_tstat,
        "r_squared": r_squared,
        "pearson_corr": pearson_corr,
        "spearman_corr": spearman_corr,
        "pearson_std_ci_low": pearson_std_ci[0],
        "pearson_std_ci_high": pearson_std_ci[1],
        "pearson_blk_ci_low": pearson_blk_ci[0],
        "pearson_blk_ci_high": pearson_blk_ci[1],
        "spearman_std_ci_low": spearman_std_ci[0],
        "spearman_std_ci_high": spearman_std_ci[1],
        "spearman_blk_ci_low": spearman_blk_ci[0],
        "spearman_blk_ci_high": spearman_blk_ci[1],
        "worst_case_corr": worst_case_corr,
        # Conditional Up/Down Regressions
        "up_alpha": up_alpha,
        "up_alpha_t": up_alpha_t,
        "up_beta": up_beta,
        "up_beta_t": up_beta_t,
        "down_alpha": down_alpha,
        "down_alpha_t": down_alpha_t,
        "down_beta": down_beta,
        "down_beta_t": down_beta_t,
        # Tail Correlations & Worst 20% SP500
        "n_d1": n_d1,
        "d1_pearson": d1_pearson,
        "d1_spearman": d1_spearman,
        "n_q1": n_q1,
        "q1_pearson": q1_pearson,
        "q1_spearman": q1_spearman,
        "worst20_fund_mean": worst20_fund_mean,
        "worst20_sp500_mean": worst20_sp500_mean,
        # Cross-asset WTI & BTC
        "wti_alpha": wti_alpha,
        "wti_alpha_t": wti_alpha_t,
        "wti_beta": wti_beta,
        "wti_beta_t": wti_beta_t,
        "wti_corr": wti_corr,
        "btc_alpha": btc_alpha,
        "btc_alpha_t": btc_alpha_t,
        "btc_beta": btc_beta,
        "btc_beta_t": btc_beta_t,
        "btc_corr": btc_corr,
        # Serial correlation
        "lb_lag1_stat": lb_lag1_stat,
        "lb_lag1_pval": lb_lag1_pval,
        "lb_lag3_stat": lb_lag3_stat,
        "lb_lag3_pval": lb_lag3_pval,
    }


# ---------------------------------------------------------------------------
# Step 3: Monthly Return Matrix Builder
# ---------------------------------------------------------------------------
def build_monthly_return_matrix(records: List[Dict[str, Any]]) -> Dict[int, Dict[Union[int, str], float]]:
    """
    Create a Year -> {1..12, 'Yearly'} return matrix dictionary.
    'Yearly' is the compounded annual return across available months in that year.
    """
    years = sorted({r["year"] for r in records})
    matrix: Dict[int, Dict[Union[int, str], float]] = {
        y: {m: math.nan for m in range(1, 13)} for y in years
    }
    for r in records:
        matrix[r["year"]][r["month"]] = r["fund"]

    for y in years:
        prod = 1.0
        has_data = False
        for m in range(1, 13):
            v = matrix[y][m]
            if not math.isnan(v):
                prod *= (1.0 + v)
                has_data = True
        matrix[y]["Yearly"] = (prod - 1.0) if has_data else math.nan

    return matrix


# ---------------------------------------------------------------------------
# Step 4: LaTeX Formatting & Modern Tear Sheet + Appendix/Risk Generator
# ---------------------------------------------------------------------------
def _isna(val: Any) -> bool:
    if val is None:
        return True
    if isinstance(val, float) and math.isnan(val):
        return True
    return False


def escape_latex(text: str) -> str:
    """Escape LaTeX special characters in text strings."""
    if not isinstance(text, str):
        text = str(text)
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def fmt_pct(val: float, decimals: int = 2, signed: bool = False) -> str:
    if _isna(val):
        return "-"
    fmt = f"{val * 100:+0.{decimals}f}%" if signed else f"{val * 100:0.{decimals}f}%"
    return escape_latex(fmt)


def fmt_num(val: float, decimals: int = 2, signed: bool = False) -> str:
    if _isna(val):
        return "-"
    fmt = f"{val:+0.{decimals}f}" if signed else f"{val:0.{decimals}f}"
    return escape_latex(fmt)


def _format_matrix_cell_latex(val: float, is_yearly: bool = False) -> str:
    """Format a monthly or yearly return cell with heatmap shading."""
    if _isna(val):
        return r"\textcolor{gray!60}{-}"
    str_val = escape_latex(f"{val * 100:.1f}%")
    if is_yearly:
        str_val = f"\\textbf{{{str_val}}}"
    scale = 320 if is_yearly else 750
    intensity = min(max(int(abs(val) * scale), 4), 75) if val != 0 else 0
    if val > 0:
        return f"\\cellcolor{{posgreen!{intensity}!white}}{str_val}"
    elif val < 0:
        return f"\\cellcolor{{negred!{intensity}!white}}{str_val}"
    return str_val


def generate_latex_tearsheet(
    fund_csv_name: str,
    metrics: Dict[str, Any],
    monthly_matrix: Dict[int, Dict[Union[int, str], float]],
    logo_rel_path: str = "athenee_logo.png",
    custom_title: Optional[str] = None,
    custom_subtitle: Optional[str] = None,
) -> str:
    """
    Generate the complete 2-page modern LaTeX document:
      - Page 1: Logo + Header + Hero KPI Cards + Full Single-Fund Quantitative Indicators + Return Matrix
      - Page 2: Quantitative Appendix, Extended Diagnostics & Capital Introduction Legal / Risk Disclaimer
    """
    stem = fund_csv_name.replace(".csv", "").strip()
    display_title = escape_latex(custom_title if custom_title else format_fund_title(stem))
    display_subtitle = escape_latex(custom_subtitle if custom_subtitle else format_fund_subtitle(stem))

    n_years_rows = len(monthly_matrix)
    # Adapt table compactness if a fund has a very long track record (e.g., > 10 years) so Page 1 stays 1 page
    if n_years_rows <= 7:
        matrix_arraystretch = "1.28"
        matrix_fontsize = r"\footnotesize"
        section_vspace = "0.60em"
        stats_arraystretch = "1.22"
    elif n_years_rows <= 12:
        matrix_arraystretch = "1.10"
        matrix_fontsize = r"\scriptsize"
        section_vspace = "0.42em"
        stats_arraystretch = "1.14"
    else:
        matrix_arraystretch = "0.94"
        matrix_fontsize = r"\tiny"
        section_vspace = "0.25em"
        stats_arraystretch = "1.06"

    # Build Monthly Return Matrix LaTeX rows
    matrix_rows_latex = ""
    for year in sorted(monthly_matrix.keys()):
        row = monthly_matrix[year]
        cells = [_format_matrix_cell_latex(row[m], is_yearly=False) for m in range(1, 13)]
        cells.append(_format_matrix_cell_latex(row["Yearly"], is_yearly=True))
        matrix_rows_latex += f"\\textbf{{{year}}} & " + " & ".join(cells) + r" \\" + "\n"

    # Format strings for Indicators
    cagr_str = fmt_pct(metrics["cagr"])
    sp_cagr_str = fmt_pct(metrics["sp_cagr"])
    ann_mean_str = fmt_pct(metrics["ann_mean"])
    sp_ann_mean_str = fmt_pct(metrics["sp_ann_mean"])
    vol_str = fmt_pct(metrics["ann_vol"])
    sp_vol_str = fmt_pct(metrics["sp_ann_vol"])
    sharpe_str = fmt_num(metrics["sharpe"])
    sp_sharpe_str = fmt_num(metrics["sp_sharpe"])
    sortino_str = fmt_num(metrics["sortino"])
    sp_sortino_str = fmt_num(metrics["sp_sortino"])
    mdd_str = fmt_pct(metrics["mdd"])
    sp_mdd_str = fmt_pct(metrics["sp_mdd"])
    calmar_str = fmt_num(metrics["calmar"])
    sp_calmar_str = fmt_num(metrics["sp_calmar"])
    cum_ret_str = fmt_pct(metrics["cum_ret"])
    sp_cum_ret_str = fmt_pct(metrics["sp_cum_ret"])
    best_m_str = fmt_pct(metrics["best_month"], signed=True)
    worst_m_str = fmt_pct(metrics["worst_month"], signed=True)
    sp_best_m_str = fmt_pct(metrics["sp_best_month"], signed=True)
    sp_worst_m_str = fmt_pct(metrics["sp_worst_month"], signed=True)

    pos_months_str = (
        f"{fmt_pct(metrics['fund_pos_rate'], 1)} ({metrics['fund_pos_count']}/{metrics['n_months']})"
    )
    sp_pos_months_str = (
        f"{fmt_pct(metrics['sp500_pos_rate'], 1)} ({metrics['sp500_pos_count']}/{metrics['n_months']})"
    )
    crisis_hit_str = (
        f"{fmt_pct(metrics['crisis_hit_rate'], 1)} ({metrics['fund_pos_when_sp500_neg']}/{metrics['n_sp500_neg']})"
        if metrics["n_sp500_neg"] > 0
        else "-"
    )
    up_loss_str = (
        f"{fmt_pct(metrics['up_loss_rate'], 1)} ({metrics['fund_neg_when_sp500_pos']}/{metrics['n_sp500_pos']})"
        if metrics["n_sp500_pos"] > 0
        else "-"
    )

    up_cap_str = fmt_num(metrics["up_capture"])
    down_cap_str = fmt_num(metrics["down_capture"])

    alpha_str = (
        f"{fmt_pct(metrics['alpha'])} (t={fmt_num(metrics['alpha_tstat'])})"
        if not _isna(metrics["alpha"])
        else "-"
    )
    beta_str = (
        f"{fmt_num(metrics['beta'])} (t={fmt_num(metrics['beta_tstat'])})"
        if not _isna(metrics["beta"])
        else "-"
    )
    r2_str = fmt_pct(metrics["r_squared"], 1) if not _isna(metrics["r_squared"]) else "-"

    pearson_str = fmt_num(metrics["pearson_corr"])
    spearman_str = fmt_num(metrics["spearman_corr"])
    pearson_blk_ci_str = (
        f"[{fmt_num(metrics['pearson_blk_ci_low'])}, {fmt_num(metrics['pearson_blk_ci_high'])}]"
        if not _isna(metrics["pearson_blk_ci_low"])
        else "-"
    )
    pearson_std_ci_str = (
        f"[{fmt_num(metrics['pearson_std_ci_low'])}, {fmt_num(metrics['pearson_std_ci_high'])}]"
        if not _isna(metrics["pearson_std_ci_low"])
        else "-"
    )
    spearman_blk_ci_str = (
        f"[{fmt_num(metrics['spearman_blk_ci_low'])}, {fmt_num(metrics['spearman_blk_ci_high'])}]"
        if not _isna(metrics["spearman_blk_ci_low"])
        else "-"
    )
    spearman_std_ci_str = (
        f"[{fmt_num(metrics['spearman_std_ci_low'])}, {fmt_num(metrics['spearman_std_ci_high'])}]"
        if not _isna(metrics["spearman_std_ci_low"])
        else "-"
    )
    worst_case_corr_str = fmt_num(metrics["worst_case_corr"])

    up_reg_str = (
        f"\\alpha={fmt_pct(metrics['up_alpha'], 1)}, \\beta={fmt_num(metrics['up_beta'])}"
        if not _isna(metrics["up_alpha"])
        else "-"
    )
    down_reg_str = (
        f"\\alpha={fmt_pct(metrics['down_alpha'], 1)}, \\beta={fmt_num(metrics['down_beta'])}"
        if not _isna(metrics["down_alpha"])
        else "-"
    )

    q1_corr_str = (
        f"r={fmt_num(metrics['q1_pearson'])}, \\rho={fmt_num(metrics['q1_spearman'])}\\ (n={metrics['n_q1']})"
        if not _isna(metrics["q1_pearson"])
        else "-"
    )
    d1_corr_str = (
        f"r={fmt_num(metrics['d1_pearson'])}, \\rho={fmt_num(metrics['d1_spearman'])}\\ (n={metrics['n_d1']})"
        if not _isna(metrics["d1_pearson"])
        else "-"
    )
    worst20_str = (
        f"Fund: {fmt_pct(metrics['worst20_fund_mean'], 2, signed=True)} vs SPX: {fmt_pct(metrics['worst20_sp500_mean'], 2, signed=True)}"
        if not _isna(metrics["worst20_fund_mean"])
        else "-"
    )

    wti_str = (
        f"\\beta={fmt_num(metrics['wti_beta'])}\\ (t={fmt_num(metrics['wti_beta_t'])}),\\ \\alpha={fmt_pct(metrics['wti_alpha'], 1)}"
        if not _isna(metrics["wti_beta"])
        else "\\text{N/A}"
    )
    btc_str = (
        f"\\beta={fmt_num(metrics['btc_beta'])}\\ (t={fmt_num(metrics['btc_beta_t'])}),\\ \\alpha={fmt_pct(metrics['btc_alpha'], 1)}"
        if not _isna(metrics["btc_beta"])
        else "\\text{N/A}"
    )
    wti_btc_compact = (
        f"WTI $\\beta$: {fmt_num(metrics['wti_beta'])} $\\vert$ BTC $\\beta$: {fmt_num(metrics['btc_beta'])}"
    )

    lb1_pval = metrics["lb_lag1_pval"]
    lb3_pval = metrics["lb_lag3_pval"]
    if not _isna(lb1_pval) and not _isna(lb3_pval):
        lb_status = "Pass (No Serial Corr.)" if (lb1_pval >= 0.05 and lb3_pval >= 0.05) else "Serial Corr. Detected"
        lb_str = f"p_1={fmt_num(lb1_pval, 2)},\\ p_3={fmt_num(lb3_pval, 2)}\\ (\\text{{{lb_status}}})"
    else:
        lb_str = "-"

    period_str = escape_latex(
        f"{metrics['start_date']} - {metrics['end_date']} ({metrics['n_months']} Months / {metrics['years_elapsed']:.1f} Years)"
    )

    latex_doc = rf"""\documentclass[10pt,a4paper]{{article}}
\usepackage[utf8]{{inputenc}}
\usepackage[T1]{{fontenc}}
\usepackage[left=0.32in, right=0.32in, top=0.28in, bottom=0.28in]{{geometry}}
\usepackage{{graphicx}}
\usepackage{{booktabs}}
\usepackage{{xcolor}}
\usepackage{{colortbl}}
\usepackage{{tabularx}}
\usepackage{{tcolorbox}}
\usepackage{{titlesec}}
\usepackage{{microtype}}
\usepackage{{helvet}}
\usepackage{{amsmath,amssymb}}
\usepackage{{enumitem}}
\usepackage{{hyperref}}

\renewcommand{{\familydefault}}{{\sfdefault}}
\pagestyle{{empty}}

% Institutional Color Palette (Athénée Investment)
\definecolor{{primary}}{{RGB}}{{15, 23, 42}}       % Deep Institutional Navy
\definecolor{{accent}}{{RGB}}{{26, 54, 93}}        % Royal Slate Navy
\definecolor{{goldaccent}}{{RGB}}{{176, 138, 87}}  % Athénée Warm Bronze/Gold
\definecolor{{cardbg}}{{RGB}}{{248, 250, 252}}     % Crisp Light Slate Background
\definecolor{{cardborder}}{{RGB}}{{218, 226, 236}} % Subtle Card Border
\definecolor{{posgreen}}{{RGB}}{{34, 197, 94}}     % Positive Return Green
\definecolor{{negred}}{{RGB}}{{239, 68, 68}}       % Negative Return Red
\definecolor{{mutedtext}}{{RGB}}{{100, 116, 139}}  % Secondary Slate Text

\hypersetup{{
    colorlinks=true,
    linkcolor=accent,
    urlcolor=accent
}}

\tcbuselibrary{{skins}}

\begin{{document}}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% PAGE 1: INSTITUTIONAL ONE-PAGER TEAR SHEET
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% --- HEADER BAR WITH LOGO ---
\noindent
\begin{{minipage}}[c]{{0.68\textwidth}}
    {{\fontsize{{20}}{{24}}\selectfont \bfseries \textcolor{{primary}}{{{display_title}}}}}\\[3pt]
    {{\normalsize \bfseries \textcolor{{accent}}{{{display_subtitle}}}}}\\[3pt]
    {{\footnotesize \textcolor{{mutedtext}}{{\textbf{{Track Record:}} {period_str} \quad $\vert$ \quad \textbf{{Benchmark:}} S\&P 500 Total Return}}}}
\end{{minipage}}%
\hfill
\begin{{minipage}}[c]{{0.30\textwidth}}
    \raggedleft
    \includegraphics[height=1.15cm, keepaspectratio]{{{logo_rel_path}}}\\[2pt]
    {{\tiny \bfseries \textcolor{{goldaccent}}{{CAPITAL INTRODUCTION \& THIRD-PARTY MARKETING}}}}
\end{{minipage}}

\vspace{{0.30em}}
\noindent{{\color{{goldaccent}}\rule{{\textwidth}}{{1.5pt}}}}
\vspace{{{section_vspace}}}

% --- SECTION 1: TOP-LINE KPI HIGHLIGHT CARDS ---
\noindent
\begin{{minipage}}[t]{{0.192\textwidth}}\vspace{{0pt}}
\begin{{tcolorbox}}[equal height group=kpicards, colback=white, colframe=primary, title=\textbf{{\footnotesize\strut CAGR (Net)}}, fonttitle=\sffamily\bfseries\footnotesize, arc=4pt, boxrule=0.8pt, toptitle=3.5pt, bottomtitle=3.5pt, left=2pt, right=2pt, top=4pt, bottom=4pt, colbacktitle=primary, halign title=center]
    \centering
    {{\Large \bfseries \textcolor{{primary}}{{\strut {cagr_str}}}}}\\[2pt]
    {{\tiny \textcolor{{mutedtext}}{{\strut S\&P 500: {sp_cagr_str}}}}}
\end{{tcolorbox}}
\end{{minipage}}\hfill
\begin{{minipage}}[t]{{0.192\textwidth}}\vspace{{0pt}}
\begin{{tcolorbox}}[equal height group=kpicards, colback=white, colframe=primary, title=\textbf{{\footnotesize\strut Ann. Volatility}}, fonttitle=\sffamily\bfseries\footnotesize, arc=4pt, boxrule=0.8pt, toptitle=3.5pt, bottomtitle=3.5pt, left=2pt, right=2pt, top=4pt, bottom=4pt, colbacktitle=primary, halign title=center]
    \centering
    {{\Large \bfseries \textcolor{{primary}}{{\strut {vol_str}}}}}\\[2pt]
    {{\tiny \textcolor{{mutedtext}}{{\strut S\&P 500: {sp_vol_str}}}}}
\end{{tcolorbox}}
\end{{minipage}}\hfill
\begin{{minipage}}[t]{{0.192\textwidth}}\vspace{{0pt}}
\begin{{tcolorbox}}[equal height group=kpicards, colback=white, colframe=primary, title=\textbf{{\footnotesize\strut Sharpe Ratio}}, fonttitle=\sffamily\bfseries\footnotesize, arc=4pt, boxrule=0.8pt, toptitle=3.5pt, bottomtitle=3.5pt, left=2pt, right=2pt, top=4pt, bottom=4pt, colbacktitle=primary, halign title=center]
    \centering
    {{\Large \bfseries \textcolor{{primary}}{{\strut {sharpe_str}}}}}\\[2pt]
    {{\tiny \textcolor{{mutedtext}}{{\strut S\&P 500: {sp_sharpe_str} $\vert$ Sortino: {sortino_str}}}}}
\end{{tcolorbox}}
\end{{minipage}}\hfill
\begin{{minipage}}[t]{{0.192\textwidth}}\vspace{{0pt}}
\begin{{tcolorbox}}[equal height group=kpicards, colback=white, colframe=primary, title=\textbf{{\footnotesize\strut Max Drawdown}}, fonttitle=\sffamily\bfseries\footnotesize, arc=4pt, boxrule=0.8pt, toptitle=3.5pt, bottomtitle=3.5pt, left=2pt, right=2pt, top=4pt, bottom=4pt, colbacktitle=primary, halign title=center]
    \centering
    {{\Large \bfseries \textcolor{{primary}}{{\strut {mdd_str}}}}}\\[2pt]
    {{\tiny \textcolor{{mutedtext}}{{\strut S\&P 500: {sp_mdd_str} $\vert$ Calmar: {calmar_str}}}}}
\end{{tcolorbox}}
\end{{minipage}}\hfill
\begin{{minipage}}[t]{{0.192\textwidth}}\vspace{{0pt}}
\begin{{tcolorbox}}[equal height group=kpicards, colback=white, colframe=primary, title=\textbf{{\footnotesize\strut Ann. Alpha ($\alpha$)}}, fonttitle=\sffamily\bfseries\footnotesize, arc=4pt, boxrule=0.8pt, toptitle=3.5pt, bottomtitle=3.5pt, left=2pt, right=2pt, top=4pt, bottom=4pt, colbacktitle=primary, halign title=center]
    \centering
    {{\Large \bfseries \textcolor{{primary}}{{\strut {fmt_pct(metrics['alpha'])}}}}}\\[2pt]
    {{\tiny \textcolor{{mutedtext}}{{\strut Beta: {fmt_num(metrics['beta'])} $\vert$ Corr: {pearson_str}}}}}
\end{{tcolorbox}}
\end{{minipage}}

\vspace{{{section_vspace}}}

% --- SECTION 2: COMPREHENSIVE SINGLE-FUND ANALYSIS INDICATORS ---
\noindent
\begin{{minipage}}[t]{{0.492\textwidth}}\vspace{{0pt}}
\begin{{tcolorbox}}[equal height group=statspanels, colback=white, colframe=primary, title=\textbf{{\small\strut Performance, Risk \& Hit Rate Indicators}}, fonttitle=\sffamily\bfseries\small, arc=5pt, boxrule=0.9pt, toptitle=4pt, bottomtitle=4pt, left=2pt, right=2pt, top=1pt, bottom=1pt, colbacktitle=primary]
\renewcommand{{\arraystretch}}{{{stats_arraystretch}}}
\scriptsize
\begin{{tabularx}}{{\textwidth}}{{>{{\columncolor{{white}}}}X >{{\columncolor{{white}}}}r >{{\columncolor{{white}}}}r}}
\rowcolor{{primary!10!white}} \textbf{{\textcolor{{primary}}{{Indicator}}}} & \textbf{{\textcolor{{primary}}{{Fund}}}} & \textbf{{\textcolor{{mutedtext}}{{S\&P 500}}}} \\
\textbf{{\textcolor{{primary}}{{CAGR (Compound Annual Growth)}}}} & \textbf{{\textcolor{{primary}}{{{cagr_str}}}}} & \textcolor{{mutedtext}}{{{sp_cagr_str}}} \\
\rowcolor{{cardbg}} \textbf{{\textcolor{{primary}}{{Annualized Mean Return}}}} & \textcolor{{primary}}{{{ann_mean_str}}} & \textcolor{{mutedtext}}{{{sp_ann_mean_str}}} \\
\textbf{{\textcolor{{primary}}{{Annualized Volatility (Std. Dev.)}}}} & \textcolor{{primary}}{{{vol_str}}} & \textcolor{{mutedtext}}{{{sp_vol_str}}} \\
\rowcolor{{cardbg}} \textbf{{\textcolor{{primary}}{{Proxy Sharpe Ratio ($r_f = 0\%$)}}}} & \textbf{{\textcolor{{primary}}{{{sharpe_str}}}}} & \textcolor{{mutedtext}}{{{sp_sharpe_str}}} \\
\textbf{{\textcolor{{primary}}{{Annualized Sortino Ratio}}}} & \textcolor{{primary}}{{{sortino_str}}} & \textcolor{{mutedtext}}{{{sp_sortino_str}}} \\
\rowcolor{{cardbg}} \textbf{{\textcolor{{primary}}{{Maximum Drawdown (MDD)}}}} & \textbf{{\textcolor{{primary}}{{{mdd_str}}}}} & \textcolor{{mutedtext}}{{{sp_mdd_str}}} \\
\textbf{{\textcolor{{primary}}{{Calmar Ratio (CAGR / $|$MDD$|$)}}}} & \textcolor{{primary}}{{{calmar_str}}} & \textcolor{{mutedtext}}{{{sp_calmar_str}}} \\
\rowcolor{{cardbg}} \textbf{{\textcolor{{primary}}{{Cumulative Total Return}}}} & \textcolor{{primary}}{{{cum_ret_str}}} & \textcolor{{mutedtext}}{{{sp_cum_ret_str}}} \\
\textbf{{\textcolor{{primary}}{{Best / Worst Monthly Return}}}} & \textcolor{{primary}}{{{best_m_str} / {worst_m_str}}} & \textcolor{{mutedtext}}{{{sp_best_m_str} / {sp_worst_m_str}}} \\
\rowcolor{{cardbg}} \textbf{{\textcolor{{primary}}{{Positive Months (Hit Rate)}}}} & \textcolor{{primary}}{{{pos_months_str}}} & \textcolor{{mutedtext}}{{{sp_pos_months_str}}} \\
\textbf{{\textcolor{{primary}}{{Crisis Hit Rate ($\text{{Fund}}>0 \mid \text{{SPX}}<0$)}}}} & \textbf{{\textcolor{{primary}}{{{crisis_hit_str}}}}} & \textcolor{{mutedtext}}{{--}} \\
\rowcolor{{cardbg}} \textbf{{\textcolor{{primary}}{{Up-Mkt Loss ($\text{{Fund}}<0 \mid \text{{SPX}}>0$)}}}} & \textcolor{{primary}}{{{up_loss_str}}} & \textcolor{{mutedtext}}{{--}} \\
\end{{tabularx}}
\end{{tcolorbox}}
\end{{minipage}}\hfill
\begin{{minipage}}[t]{{0.492\textwidth}}\vspace{{0pt}}
\begin{{tcolorbox}}[equal height group=statspanels, colback=white, colframe=primary, title=\textbf{{\small\strut Alpha, Beta, Correlation \& Tail Analysis (vs. S\&P 500)}}, fonttitle=\sffamily\bfseries\small, arc=5pt, boxrule=0.9pt, toptitle=4pt, bottomtitle=4pt, left=2pt, right=2pt, top=1pt, bottom=1pt, colbacktitle=primary]
\renewcommand{{\arraystretch}}{{{stats_arraystretch}}}
\scriptsize
\begin{{tabularx}}{{\textwidth}}{{>{{\columncolor{{white}}}}X >{{\columncolor{{white}}}}r}}
\rowcolor{{primary!10!white}} \textbf{{\textcolor{{primary}}{{Quantitative Metric}}}} & \textbf{{\textcolor{{primary}}{{Estimate / Diagnostic}}}} \\
\textbf{{\textcolor{{primary}}{{Annualized Alpha ($\alpha$) \& $t$-stat}}}} & \textbf{{\textcolor{{primary}}{{{alpha_str}}}}} \\
\rowcolor{{cardbg}} \textbf{{\textcolor{{primary}}{{Market Beta ($\beta_{{\text{{SPX}}}}$) \& $t$-stat}}}} & \textcolor{{primary}}{{{beta_str} ($R^2={r2_str}$)}} \\
\textbf{{\textcolor{{primary}}{{Pearson Corr. ($r$) to S\&P 500}}}} & \textbf{{\textcolor{{primary}}{{{pearson_str}}}}} \textcolor{{mutedtext}}{{(95\% Blk CI: {pearson_blk_ci_str})}} \\
\rowcolor{{cardbg}} \textbf{{\textcolor{{primary}}{{Spearman Rank Corr. ($\rho$)}}}} & \textcolor{{primary}}{{{spearman_str}}} \textcolor{{mutedtext}}{{(95\% Blk CI: {spearman_blk_ci_str})}} \\
\textbf{{\textcolor{{primary}}{{Upside / Downside Capture}}}} & \textcolor{{primary}}{{Up: \textbf{{{up_cap_str}}} $\vert$ Down: \textbf{{{down_cap_str}}}}} \\
\rowcolor{{cardbg}} \textbf{{\textcolor{{primary}}{{Cond. Up-Market ($\text{{SPX}}>0$)}}}} & \textcolor{{primary}}{{${up_reg_str}$}} \\
\textbf{{\textcolor{{primary}}{{Cond. Down-Market ($\text{{SPX}}<0$)}}}} & \textcolor{{primary}}{{${down_reg_str}$}} \\
\rowcolor{{cardbg}} \textbf{{\textcolor{{primary}}{{Tail Corr. ($\text{{SPX}} < \text{{Q}}_1$, 25\%)}}}} & \textcolor{{primary}}{{${q1_corr_str}$}} \\
\textbf{{\textcolor{{primary}}{{Tail Corr. ($\text{{SPX}} < \text{{D}}_1$, 10\%)}}}} & \textcolor{{primary}}{{${d1_corr_str}$}} \\
\rowcolor{{cardbg}} \textbf{{\textcolor{{primary}}{{Worst 20\% SPX Months Mean}}}} & \textcolor{{primary}}{{{worst20_str}}} \\
\textbf{{\textcolor{{primary}}{{Cross-Asset Beta (WTI / BTC)}}}} & \textcolor{{primary}}{{{wti_btc_compact}}} \\
\rowcolor{{cardbg}} \textbf{{\textcolor{{primary}}{{Ljung-Box Serial Corr.}}}} & \textcolor{{primary}}{{${lb_str}$}} \\
\end{{tabularx}}
\end{{tcolorbox}}
\end{{minipage}}

\vspace{{{section_vspace}}}

% --- SECTION 3: MONTHLY RETURN MATRIX ---
\begin{{tcolorbox}}[colback=white, colframe=primary, title=\textbf{{\small\strut Historical Monthly \& Yearly Net Return Matrix (\%)}}, fonttitle=\sffamily\bfseries\small, arc=5pt, boxrule=0.9pt, toptitle=4pt, bottomtitle=4pt, left=3pt, right=3pt, top=1pt, bottom=1pt, colbacktitle=primary, halign title=center]
\renewcommand{{\arraystretch}}{{{matrix_arraystretch}}}
{matrix_fontsize}
\begin{{tabularx}}{{\textwidth}}{{l *{{12}}{{>{{\centering\arraybackslash}}X}} >{{\centering\arraybackslash}}p{{1.15cm}}}}
\rowcolor{{primary!8!white}}
\textbf{{\textcolor{{primary}}{{Year}}}} & \textbf{{\textcolor{{primary}}{{Jan}}}} & \textbf{{\textcolor{{primary}}{{Feb}}}} & \textbf{{\textcolor{{primary}}{{Mar}}}} & \textbf{{\textcolor{{primary}}{{Apr}}}} & \textbf{{\textcolor{{primary}}{{May}}}} & \textbf{{\textcolor{{primary}}{{Jun}}}} & \textbf{{\textcolor{{primary}}{{Jul}}}} & \textbf{{\textcolor{{primary}}{{Aug}}}} & \textbf{{\textcolor{{primary}}{{Sep}}}} & \textbf{{\textcolor{{primary}}{{Oct}}}} & \textbf{{\textcolor{{primary}}{{Nov}}}} & \textbf{{\textcolor{{primary}}{{Dec}}}} & \textbf{{\textcolor{{primary}}{{Yearly}}}} \\
\midrule
{matrix_rows_latex}\bottomrule
\end{{tabularx}}
\end{{tcolorbox}}

\vfill

% --- PAGE 1 FOOTER ---
\noindent{{\color{{cardborder}}\rule{{\textwidth}}{{0.6pt}}}}\\[2pt]
\noindent
\begin{{minipage}}[c]{{0.74\textwidth}}
    {{\tiny \textcolor{{mutedtext}}{{\textbf{{Ath\'en\'ee Investment}} $\vert$ Quai des Bergues 23, 1201 Geneva, Switzerland $\vert$ \href{{mailto:arthur.dhonneur@athenee-investment.com}}{{arthur.dhonneur@athenee-investment.com}}}}\\[1pt]
    \tiny \textcolor{{mutedtext}}{{\textit{{Capital Introduction \& Third-Party Marketing Memorandum. Strictly for Institutional \& Qualified Investors. Please see Page 2 for Risk \& Legal Disclosures.}}}}}}
\end{{minipage}}%
\hfill
\begin{{minipage}}[c]{{0.24\textwidth}}
    \raggedleft
    {{\tiny \bfseries \textcolor{{primary}}{{Page 1 of 2}}}}
\end{{minipage}}

\clearpage

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% PAGE 2: APPENDIX, QUANTITATIVE METHODOLOGY & RISK / LEGAL DISCLAIMER
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% --- PAGE 2 HEADER ---
\noindent
\begin{{minipage}}[c]{{0.68\textwidth}}
    {{\Large \bfseries \textcolor{{primary}}{{Appendix, Quantitative Methodology \& Risk Disclosures}}}}\\[2pt]
    {{\footnotesize \bfseries \textcolor{{accent}}{{Fund Reference: {display_title} ({period_str})}}}}
\end{{minipage}}%
\hfill
\begin{{minipage}}[c]{{0.30\textwidth}}
    \raggedleft
    \includegraphics[height=1.0cm, keepaspectratio]{{{logo_rel_path}}}\\[2pt]
    {{\tiny \bfseries \textcolor{{goldaccent}}{{CAPITAL INTRODUCTION \& THIRD-PARTY MARKETING}}}}
\end{{minipage}}

\vspace{{0.3em}}
\noindent{{\color{{goldaccent}}\rule{{\textwidth}}{{1.2pt}}}}
\vspace{{0.5em}}

% --- PART I: EXTENDED SINGLE-FUND QUANTITATIVE DIAGNOSTICS ---
\begin{{tcolorbox}}[colback=white, colframe=primary, title=\textbf{{\small\strut Appendix A: Extended Statistical, Bootstrap \& Factor Diagnostics}}, fonttitle=\sffamily\bfseries\small, arc=5pt, boxrule=0.8pt, toptitle=4pt, bottomtitle=4pt, left=6pt, right=6pt, top=4pt, bottom=4pt, colbacktitle=primary]
\renewcommand{{\arraystretch}}{{1.25}}
\scriptsize
\begin{{tabularx}}{{\textwidth}}{{l X r}}
\toprule
\textbf{{\textcolor{{primary}}{{Diagnostic Family}}}} & \textbf{{\textcolor{{primary}}{{Methodology / Statistical Specification}}}} & \textbf{{\textcolor{{primary}}{{Empirical Value}}}} \\
\midrule
\textbf{{Pearson Correlation CI}} & 95\% Confidence Interval (IID Bootstrap vs. Moving Block $B=3$, 1,000 iters) & Std: {pearson_std_ci_str} $\vert$ Blk: {pearson_blk_ci_str} \\
\rowcolor{{cardbg}} \textbf{{Spearman Rank Corr. CI}} & 95\% Confidence Interval (Rank Monotonic Co-Movement, IID vs. Block $B=3$) & Std: {spearman_std_ci_str} $\vert$ Blk: {spearman_blk_ci_str} \\
\textbf{{Worst-Case Co-Dependence}} & 97.5th Percentile Upper-Bound Block Bootstrap Correlation (PSD Projection) & $\rho_{{\text{{wc}}}} = {worst_case_corr_str}$ \\
\rowcolor{{cardbg}} \textbf{{Serial Correlation (Lag 1 \& 3)}} & Ljung-Box $Q$-Statistic $p$-values testing for return smoothing / illiquidity bias & ${lb_str}$ \\
\textbf{{Conditional Up-Market OLS}} & Annualized Alpha \& Beta estimated during positive S\&P 500 months ($n={metrics['n_sp500_pos']}$) & ${up_reg_str}$ ($t_\alpha={fmt_num(metrics['up_alpha_t'])}$) \\
\rowcolor{{cardbg}} \textbf{{Conditional Down-Market OLS}} & Annualized Alpha \& Beta estimated during negative S\&P 500 months ($n={metrics['n_sp500_neg']}$) & ${down_reg_str}$ ($t_\alpha={fmt_num(metrics['down_alpha_t'])}$) \\
\textbf{{Commodity Factor (WTI)}} & OLS Regression against Front-Month WTI Crude Oil Monthly Returns & ${wti_str}$ \\
\rowcolor{{cardbg}} \textbf{{Digital Asset Factor (BTC)}} & OLS Regression against Bitcoin (BTC-USD) Monthly Returns & ${btc_str}$ \\
\bottomrule
\end{{tabularx}}
\end{{tcolorbox}}

\vspace{{0.35em}}

% --- PART II: METHODOLOGY DEFINITIONS ---
\begin{{tcolorbox}}[colback=cardbg, colframe=cardborder, title=\textbf{{\small Appendix B: Quantitative Framework \& Indicator Definitions}}, fonttitle=\sffamily\bfseries\small\color{{primary}}, arc=5pt, boxrule=0.8pt, toptitle=4pt, bottomtitle=4pt, left=6pt, right=6pt, top=4pt, bottom=4pt, colbacktitle=cardborder]
\scriptsize
\begin{{itemize}}[leftmargin=1.2em, itemsep=1.5pt, topsep=1pt]
    \item \textbf{{CAGR \& Annualized Volatility:}} Compound Annual Growth Rate is computed geometrically as $\text{{CAGR}} = \left(\prod_{{t=1}}^T (1 + r_t)\right)^{{12/T}} - 1$. Annualized Volatility is sample standard deviation scaled by $\sqrt{{12}}$: $\sigma_{{\text{{ann}}}} = \hat{{\sigma}}_m \sqrt{{12}}$. Proxy Sharpe Ratio assumes $r_f = 0\%$ ($\bar{{r}}_{{\text{{ann}}}} / \sigma_{{\text{{ann}}}}$).
    \item \textbf{{Maximum Drawdown (MDD) \& Calmar Ratio:}} Maximum peak-to-trough decline of cumulative compounded wealth $W_t = \prod_{{s \le t}}(1+r_s)$, defined as $\text{{MDD}} = \min_t \left((W_t - \max_{{s \le t}} W_s) / \max_{{s \le t}} W_s\right)$. Calmar Ratio is $\text{{CAGR}} / |\text{{MDD}}|$.
    \item \textbf{{OLS Alpha ($\alpha$), Beta ($\beta$) \& Capture Ratios:}} Estimated via Ordinary Least Squares $r_{{\text{{fund}},t}} = \alpha_m + \beta r_{{\text{{SPX}},t}} + \varepsilon_t$, where $\alpha_{{\text{{ann}}}} = 12 \times \alpha_m$. Upside (Downside) Capture measures the ratio of the fund's mean return to the S\&P 500's mean return during positive (negative) S\&P 500 months.
    \item \textbf{{Tail Correlations \& Moving Block Bootstrap:}} Tail correlations evaluate linear ($r$) and rank ($\rho$) co-movement during S\&P 500 drawdowns below the 25th percentile ($Q_1$) and 10th percentile ($D_1$). Moving Block Bootstrap ($B=3$ months) preserves local serial dependencies when constructing 95\% confidence intervals.
\end{{itemize}}
\end{{tcolorbox}}

\vspace{{0.35em}}

% --- PART III: CAPITAL INTRODUCTION & RISK DISCLAIMER ---
\begin{{tcolorbox}}[colback=white, colframe=accent, title=\textbf{{\small Important Legal Disclaimer, Risk Disclosures \& Capital Introduction Notice}}, fonttitle=\sffamily\bfseries\small, arc=5pt, boxrule=0.9pt, toptitle=5pt, bottomtitle=5pt, left=8pt, right=8pt, top=5pt, bottom=5pt, colbacktitle=accent]
\scriptsize
\textcolor{{primary}}{{
\textbf{{1. Role of Ath\'en\'ee Investment — Capital Introduction Services Only (No Investment Advice):}}\\[1.5pt]
This document has been prepared by \textbf{{Ath\'en\'ee Investment}} solely for informational and discussion purposes as part of its institutional \textbf{{Capital Introduction and Third-Party Marketing}} activities. \textbf{{This document does not constitute investment advice, financial advisory services, a personal recommendation, or an offer to sell or a solicitation of an offer to buy}} any shares, units, or interests in any investment fund or financial instrument. Prospective investors must conduct their own independent due diligence and consult their own professional legal, regulatory, tax, and financial advisors before making any investment decision.\\[5pt]
\textbf{{2. No Warranty of Data Accuracy or Completeness (Third-Party Manager Data):}}\\[1.5pt]
All historical performance figures, return series, and strategy descriptions presented herein are derived from information provided directly by the respective third-party hedge fund managers or external data providers. While Ath\'en\'ee Investment has compiled and analyzed these quantitative metrics in good faith, \textbf{{Ath\'en\'ee Investment has not independently audited or verified the underlying data and cannot guarantee—and makes no representation or warranty, express or implied, regarding—the accuracy, completeness, reliability, or timeliness}} of any information contained in this document. Any errors, omissions, or subsequent restatements by the underlying fund manager are the sole responsibility of such manager.\\[5pt]
\textbf{{3. Key Risk Factors of Alternative \& Hedge Fund Strategies:}}\\[1.5pt]
Investing in alternative investment funds and hedge funds involves a \textbf{{high degree of risk}} and is suitable only for sophisticated investors capable of bearing the loss of their entire investment. Material risks include, without limitation:
\begin{{itemize}}[leftmargin=1.3em, itemsep=1pt, topsep=1pt]
    \item \textbf{{Market, Leverage \& Derivative Risk:}} Underlying funds may employ substantial leverage, short-selling, options, futures, swaps, and other derivative instruments, which can amplify both gains and losses and cause rapid capital erosion during extreme market dislocations.
    \item \textbf{{Illiquidity \& Lock-Up Risk:}} Hedge fund interests are typically not listed on any regulated exchange and are subject to redemption gates, notice periods, lock-ups, and side-pocket arrangements.
    \item \textbf{{Model, Regime Shift \& Tail-Correlation Risk:}} Quantitative and systematic strategies rely on mathematical models and historical statistical relationships (such as low equity beta or negative downside capture) that may break down or experience sudden correlation spikes during systemic liquidity crises.
    \item \textbf{{Operational, Counterparty \& Valuation Risk:}} Strategies trading in over-the-counter (OTC) derivatives, digital assets, distressed debt, or emerging markets face heightened counterparty default, custody, regulatory, and mark-to-model valuation risks.
\end{{itemize}}
\vspace{{3pt}}
\textbf{{4. Past Performance \& Quantitative Limitations:}}\\[1.5pt]
\textbf{{Past performance is not indicative of, nor a guarantee of, future results.}} The value of investments and the income derived from them may go down as well as up. Simulated, bootstrap, or regression-based indicators (including Alpha, Beta, Sharpe Ratio, Sortino Ratio, and Capture Ratios) are backward-looking statistical estimates and do not represent a promise or forecast of future risk-adjusted returns.\\[5pt]
\textbf{{5. Qualified Investors Only \& Confidentiality:}}\\[1.5pt]
This document is strictly confidential and is directed exclusively at \textbf{{Institutional, Professional, and Qualified Investors}} (including Qualified Investors within the meaning of the Swiss Collective Investment Schemes Act (CISA) and Financial Services Act (FinSA)). It may not be copied, reproduced, distributed, or disclosed to any third party, nor distributed in any jurisdiction where such distribution would be unlawful.
}}
\end{{tcolorbox}}

\vfill

% --- PAGE 2 FOOTER ---
\noindent{{\color{{cardborder}}\rule{{\textwidth}}{{0.6pt}}}}\\[2pt]
\noindent
\begin{{minipage}}[c]{{0.74\textwidth}}
    {{\tiny \textcolor{{mutedtext}}{{\textbf{{Ath\'en\'ee Investment}} $\vert$ Quai des Bergues 23, 1201 Geneva, Switzerland $\vert$ \href{{mailto:arthur.dhonneur@athenee-investment.com}}{{arthur.dhonneur@athenee-investment.com}}}}\\[1pt]
    \tiny \textcolor{{mutedtext}}{{\textit{{\textcopyright\ 2026 Ath\'en\'ee Investment. All rights reserved. For Institutional \& Qualified Investors Only.}}}}}}
\end{{minipage}}%
\hfill
\begin{{minipage}}[c]{{0.24\textwidth}}
    \raggedleft
    {{\tiny \bfseries \textcolor{{primary}}{{Page 2 of 2}}}}
\end{{minipage}}

\end{{document}}
"""
    return latex_doc


# ---------------------------------------------------------------------------
# Step 5: CSV Writers & Pipeline Runners (Single & Batch)
# ---------------------------------------------------------------------------
def _write_dict_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _write_return_matrix_csv(path: Path, matrix: Dict[int, Dict[Union[int, str], float]]) -> None:
    headers = ["Year"] + MONTH_ABBR + ["Yearly"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for year in sorted(matrix.keys()):
            row = [year]
            for m in range(1, 13):
                v = matrix[year][m]
                row.append("" if _isna(v) else f"{v:.6f}")
            vy = matrix[year]["Yearly"]
            row.append("" if _isna(vy) else f"{vy:.6f}")
            writer.writerow(row)


def compile_tex_to_pdf(tex_path: Union[str, Path]) -> Optional[Path]:
    """Compile a generated .tex file to .pdf using pdflatex and clean auxiliary files."""
    tex_file = Path(tex_path).resolve()
    out_dir = tex_file.parent
    stem = tex_file.stem
    pdflatex_bin = find_pdflatex()
    if pdflatex_bin is None:
        raise RuntimeError("Could not find `pdflatex` binary on system.")

    cmd = [pdflatex_bin, "-interaction=nonstopmode", tex_file.name]
    res = subprocess.run(cmd, cwd=str(out_dir), capture_output=True, text=True)
    pdf_path = out_dir / f"{stem}.pdf"
    if res.returncode != 0 and not pdf_path.exists():
        print(f"[WARNING] pdflatex failed for {tex_file.name}:\n{res.stdout[-1500:]}")
        return None

    for ext in [".aux", ".log", ".out"]:
        aux_file = out_dir / f"{stem}{ext}"
        if aux_file.exists():
            aux_file.unlink()
    return pdf_path if pdf_path.exists() else None


def run_fund_pipeline(
    fund_csv_name: str,
    output_dir: Union[str, Path] = DEFAULT_OUTPUT_DIR,
    hf_returns_dir: Union[str, Path] = HF_RETURNS_DIR,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    leverage: Optional[float] = None,
    annual_financing_cost: float = 0.0,
    custom_title: Optional[str] = None,
    custom_subtitle: Optional[str] = None,
    compile_pdf: bool = True,
) -> Dict[str, Any]:
    """
    Run the complete pipeline for a single fund CSV:
      1. Load returns from `data/hf_returns/<fund_csv_name>.csv` and align with S&P 500, WTI, BTC
      2. Compute all `single_fund_analysis` metrics
      3. Build the Year x Month + Yearly Return Matrix
      4. Generate the modern LaTeX document (Page 1 Tear Sheet + Page 2 Appendix & Risk Disclaimer)
      5. Compile to PDF using `pdflatex` (if compile_pdf=True)
    """
    stem = fund_csv_name.replace(".csv", "").strip()
    out_dir = Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Ensure logo is present in output directory so pdflatex finds it cleanly
    target_logo = out_dir / "athenee_logo.png"
    if not target_logo.exists():
        if LOGO_PATH.exists():
            shutil.copy(LOGO_PATH, target_logo)
        else:
            fallback_logo = PROJECT_ROOT / "report" / "educational" / "educational_easier" / "athenee_logo.png"
            if fallback_logo.exists():
                shutil.copy(fallback_logo, LOGO_PATH)
                shutil.copy(LOGO_PATH, target_logo)

    # 1. Load data
    records = load_fund_and_benchmarks(
        fund_csv_name=stem,
        hf_returns_dir=Path(hf_returns_dir),
        start_date=start_date,
        end_date=end_date,
        leverage=leverage,
        annual_financing_cost=annual_financing_cost,
    )

    # 2. Compute metrics
    metrics = compute_single_fund_metrics(records, stem)

    # 3. Build Monthly Return Matrix
    monthly_matrix = build_monthly_return_matrix(records)

    # Save CSV exports of metrics and monthly return matrix
    metrics_csv_path = out_dir / f"{stem}_metrics.csv"
    _write_dict_csv(metrics_csv_path, [metrics])

    matrix_csv_path = out_dir / f"{stem}_return_matrix.csv"
    _write_return_matrix_csv(matrix_csv_path, monthly_matrix)

    # 4. Generate LaTeX file
    latex_code = generate_latex_tearsheet(
        fund_csv_name=stem,
        metrics=metrics,
        monthly_matrix=monthly_matrix,
        logo_rel_path="athenee_logo.png",
        custom_title=custom_title,
        custom_subtitle=custom_subtitle,
    )
    tex_path = out_dir / f"{stem}_tearsheet.tex"
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(latex_code)

    pdf_path = None
    if compile_pdf:
        pdf_path = compile_tex_to_pdf(tex_path)

    return {
        "fund": stem,
        "metrics": metrics,
        "return_matrix": monthly_matrix,
        "tex_path": str(tex_path),
        "pdf_path": str(pdf_path) if pdf_path else None,
        "metrics_csv_path": str(metrics_csv_path),
        "matrix_csv_path": str(matrix_csv_path),
    }


def run_batch_pipeline(
    selected_funds: Union[List[str], str],
    output_dir: Union[str, Path] = DEFAULT_OUTPUT_DIR,
    hf_returns_dir: Union[str, Path] = HF_RETURNS_DIR,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    fund_configs: Optional[Dict[str, Dict]] = None,
    compile_pdf: bool = True,
) -> List[Dict[str, Any]]:
    """
    Run the tear sheet generation pipeline for multiple funds in one shot using the exact same model.
    Saves individual PDFs (`<fund>_tearsheet.pdf`) as well as a combined `summary_selected_funds_metrics.csv`.
    """
    if isinstance(selected_funds, str):
        if selected_funds.lower() == "all":
            fund_list = list_available_funds(Path(hf_returns_dir))
        else:
            fund_list = [f.strip() for f in selected_funds.split(",") if f.strip()]
    else:
        fund_list = list(selected_funds)

    out_dir = Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    fund_configs = fund_configs or {}

    all_metrics: List[Dict[str, Any]] = []
    print(f"=== Running Athénée Third-Party Marketing Pipeline for {len(fund_list)} fund(s) ===")

    for idx, fund_name in enumerate(fund_list, 1):
        stem = fund_name.replace(".csv", "").strip()
        cfg = fund_configs.get(stem, {})
        try:
            res = run_fund_pipeline(
                fund_csv_name=stem,
                output_dir=out_dir,
                hf_returns_dir=hf_returns_dir,
                start_date=cfg.get("start_date", start_date),
                end_date=cfg.get("end_date", end_date),
                leverage=cfg.get("leverage", None),
                annual_financing_cost=cfg.get("annual_financing_cost", 0.0),
                custom_title=cfg.get("title", None),
                custom_subtitle=cfg.get("subtitle", None),
                compile_pdf=compile_pdf,
            )
            m = res["metrics"]
            all_metrics.append(m)
            status_label = os.path.basename(res["pdf_path"]) if res["pdf_path"] else os.path.basename(res["tex_path"])
            print(
                f"  [{idx}/{len(fund_list)}] {stem:<26} | "
                f"CAGR: {m['cagr']*100:6.2f}% | Vol: {m['ann_vol']*100:5.2f}% | "
                f"Sharpe: {m['sharpe']:5.2f} | MDD: {m['mdd']*100:6.2f}% | "
                f"Corr SPX: {m['pearson_corr']:+5.2f} | Out: {status_label}"
            )
        except Exception as e:
            print(f"  [{idx}/{len(fund_list)}] ERROR processing '{stem}': {e}")

    if all_metrics:
        summary_csv = out_dir / "summary_selected_funds_metrics.csv"
        _write_dict_csv(summary_csv, all_metrics)
        print(f"=== Batch Complete! Summary CSV & Tear Sheets saved to: {out_dir} ===")
    return all_metrics


# ---------------------------------------------------------------------------
# CLI Entrypoint
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Athénée Investment — Third-Party Marketing & Capital Introduction Tear Sheet Pipeline"
    )
    parser.add_argument(
        "--funds",
        nargs="+",
        default=["dcm_systematic"],
        help="List of fund CSV names from data/hf_returns (e.g. dcm_systematic smithson 26_miles) or 'all'.",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(DEFAULT_OUTPUT_DIR),
        help="Output directory for generated .tex, .pdf, and .csv files.",
    )
    parser.add_argument(
        "--start-date",
        type=str,
        default=None,
        help="Optional start date filter (YYYY-MM-DD or YYYY-MM).",
    )
    parser.add_argument(
        "--end-date",
        type=str,
        default=None,
        help="Optional end date filter (YYYY-MM-DD or YYYY-MM).",
    )
    parser.add_argument(
        "--no-pdf",
        action="store_true",
        help="Generate CSVs and .tex files without running pdflatex.",
    )
    parser.add_argument(
        "--list-funds",
        action="store_true",
        help="List all available fund CSV names in data/hf_returns and exit.",
    )

    args = parser.parse_args()
    if args.list_funds:
        funds = list_available_funds()
        print(f"Available funds in {HF_RETURNS_DIR} ({len(funds)}):")
        for f in funds:
            print(f"  - {f}")
        return

    compile_pdf_flag = not args.no_pdf
    if len(args.funds) == 1 and args.funds[0].lower() == "all":
        run_batch_pipeline(
            "all",
            output_dir=args.output_dir,
            start_date=args.start_date,
            end_date=args.end_date,
            compile_pdf=compile_pdf_flag,
        )
    else:
        run_batch_pipeline(
            args.funds,
            output_dir=args.output_dir,
            start_date=args.start_date,
            end_date=args.end_date,
            compile_pdf=compile_pdf_flag,
        )


if __name__ == "__main__":
    main()

