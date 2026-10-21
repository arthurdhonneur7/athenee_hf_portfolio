"""
Athénée Investment — Third-Party Marketing & Capital Introduction Tear Sheet Pipeline
=====================================================================================
Selects one or multiple hedge funds from `data/hf_returns/` using their CSV names,
computes the full `single_fund_analysis` quantitative metrics suite against the S&P 500
(and cross-asset benchmarks WTI & BTC), and compiles a modern 2-page LaTeX PDF:
  - Page 1: Institutional One-Pager Tear Sheet (Logo, 5 KPI Cards incl. Corr/Alpha/Beta,
            Aligned Quantitative Indicator Panels, Growth & Worst-20% SPX Charts,
            and Proportionally-Scaled Monthly Return Matrix)
  - Page 2: Quantitative Appendix, Extended Diagnostics & Capital Introduction Risk / Legal Disclaimer
"""

import os
import sys
import csv
import glob
import math
import shutil
import random
import hashlib
import argparse
import subprocess
import zipfile
from xml.sax.saxutils import escape as xml_escape
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
DOWNLOADS_DIR = Path.home() / "Downloads"
DEFAULT_DOWNLOADS_EXCEL_PATH = DOWNLOADS_DIR / "Athenee_TPM_Fund_Analysis.xlsx"
CONFIDENTIAL_MAPPING_PATH = THIS_DIR / "confidential_fund_mapping.csv"
LOGO_PATH = THIS_DIR / "athenee_logo.png"
FUND_DATABASE_PATH = THIS_DIR / "fund_database.csv"
DATA_METADATA_PATH = PROJECT_ROOT / "data" / "hf_metadata.csv"

MONTH_ABBR = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

FUND_DB_COLUMNS = [
    "fund_csv",
    "anonymized_code",     # Deterministic Athénée code (e.g. "ATH-514")
    "anonymized_name",     # Deterministic readable anonymized name (e.g. "Schedar Bastion")
    "display_name",
    "strategy_subtitle",
    "return_basis",        # Discretionary: "" (unspecified), "Net", or "Gross"
    "investment_vehicle",  # e.g. "Commingled Fund" or "SMA"
    "management_fee",      # e.g. "2%" or "1.5%"
    "performance_fee",     # e.g. "20%" or "20% (HWM)"
    "liquidity_terms",     # e.g. "Quarter Liquidity" or "Monthly (30d Notice)"
    "lockup",              # e.g. "No Lockup" or "12m Soft Lock"
    "minimum_investment",  # e.g. "1M USD" or "$1,000,000"
    "current_aum",         # e.g. "250M USD" or "$250M"
    "domicile_structure",  # e.g. "Cayman Islands"
    "notes",               # Optional notes
]

# Default human-readable names & subtitles used when initializing fund_database.csv
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
    "anvik": "Anvik Capital Strategy",
    "edge_capital": "Edge Capital Market Neutral",
    "coban_edge_capital": "Coban Edge Capital",
    "coban_orca": "Coban ORCA Strategy",
    "coban_clarion_multi_asset": "Clarion Multi-Asset Strategy",
    "coban_arkis_ls_alpha": "Coban Arkis Long/Short Alpha",
    "coban_amount_abs_ret": "Coban Amont Absolute Return",
    "coban_plettenberg": "Coban Plettenberg Strategy",
    "coban_pod_1": "Coban Multi-Manager Pod 1",
    "coban_pod_2": "Coban Multi-Manager Pod 2",
    "blackrock_sta": "BlackRock Systematic Total Alpha",
    "spear_digital": "Spear Digital Asset Strategy",
    "agt_partners": "AGT Partners Strategy",
    "qlumina_dubai": "Qlumina Dubai Strategy",
    "qlumina_kiruna": "Qlumina Kiruna Strategy",
    "qlumina_miami": "Qlumina Miami Strategy",
    "qlumina_new_york": "Qlumina New York Strategy",
    "qlumina_zermatt": "Qlumina Zermatt Strategy",
    "qlumina_zurich": "Qlumina Zurich Strategy",
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
    "anvik": "Quantitative Multi-Strategy Alternative Investment Fund",
    "coban_clarion_multi_asset": "Systematic & Discretionary Multi-Asset Strategy",
}


_ANON_PRIMARY_WORDS: List[str] = [
    "Solaris", "Meridian", "Borealis", "Hyperion", "Vespera", "Polaris", "Arcturus", "Altair",
    "Sirius", "Vega", "Lyra", "Orion", "Cassiopeia", "Andromeda", "Perseus", "Cygnus",
    "Aquila", "Pegasus", "Centauri", "Rigel", "Antares", "Aldebaran", "Capella", "Procyon",
    "Regulus", "Spica", "Deneb", "Fomalhaut", "Canopus", "Bellatrix", "Alnilam", "Mintaka",
    "Castor", "Pollux", "Alcor", "Mizar", "Alioth", "Dubhe", "Merak", "Alkaid",
    "Thuban", "Eltanin", "Albireo", "Sadr", "Alpheratz", "Mirach", "Almach", "Schedar",
    "Mirfak", "Alcyone", "Electra", "Maia", "Merope", "Taygeta", "Atlas", "Helios",
    "Selene", "Astraea", "Callisto", "Europa", "Ganymede", "Oberon", "Titania", "Triton",
    "Valais", "Engadin", "Oberland", "Leman", "Ticino", "Arosa", "Bernina", "Albula",
    "Julier", "Gotthard", "Simplon", "Furka", "Grimsel", "Susten", "Kander", "Limmat",
    "Rhone", "Maggia", "Verzasca", "Bregaglia", "Lavaux", "Chablais", "Gruyere", "Concordia",
]

_ANON_SECONDARY_WORDS: List[str] = [
    "Alpha", "Prime", "Apex", "Vector", "Vertex", "Horizon", "Vanguard", "Summit",
    "Crest", "Ridge", "Nova", "Zenith", "Nexus", "Prism", "Quantum", "Aegis",
    "Citadel", "Pinnacle", "Ascent", "Equinox", "Solstice", "Catalyst", "Bastion", "Axis",
]


def get_anonymized_fund_identity(csv_name: str) -> Dict[str, str]:
    """
    Generate a 100% deterministic, readable institutional anonymized identity from `csv_name`
    so that client-facing PDFs, chart legends, filenames, and Excel workbooks never leak IP.
    """
    stem = csv_name.replace(".csv", "").strip().lower()
    digest = hashlib.sha256(f"athenee-141:{stem}".encode("utf-8")).digest()
    w1 = _ANON_PRIMARY_WORDS[int.from_bytes(digest[:4], "big") % len(_ANON_PRIMARY_WORDS)]
    w2 = _ANON_SECONDARY_WORDS[int.from_bytes(digest[4:8], "big") % len(_ANON_SECONDARY_WORDS)]
    code_num = 100 + (int.from_bytes(digest[8:12], "big") % 900)

    anon_name = f"{w1} {w2}"
    anon_code = f"ATH-{code_num}"
    anon_slug = f"{w1.lower()}_{w2.lower()}_{anon_code.lower().replace('-', '_')}"
    return {
        "anon_name": anon_name,
        "anon_code": anon_code,
        "anon_display": f"{anon_name} ({anon_code})",
        "anon_short": anon_name,
        "anon_slug": anon_slug,
    }


def scrub_fund_name_from_text(text: str, csv_name: str, real_display_name: str = "") -> str:
    """Ensure no accidental mention of the real fund name or CSV stem remains in a subtitle or note."""
    if not text:
        return ""
    out = text
    stem = csv_name.replace(".csv", "").strip()
    candidates = [stem, stem.replace("_", " ")]
    if real_display_name:
        candidates.append(real_display_name)
        first_token = real_display_name.split()[0] if real_display_name.split() else ""
        if len(first_token) >= 4 and first_token.lower() not in {"quant", "multi", "global", "systematic", "digital", "equity", "macro", "alpha"}:
            candidates.append(first_token)
    for cand in sorted(set(c for c in candidates if len(c) >= 3), key=len, reverse=True):
        # Case-insensitive replacement if present
        low_out = out.lower()
        low_c = cand.lower()
        idx = low_out.find(low_c)
        while idx != -1:
            out = out[:idx] + "Mandate" + out[idx + len(cand) :]
            low_out = out.lower()
            idx = low_out.find(low_c)
    return out


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
# Step 0: Fund Terms & Metadata Database (`fund_database.csv` & `data/hf_metadata.csv`)
# ---------------------------------------------------------------------------
def init_or_load_fund_database(
    db_path: Path = FUND_DATABASE_PATH,
    hf_returns_dir: Path = HF_RETURNS_DIR,
) -> Dict[str, Dict[str, str]]:
    """
    Load `third_party_marketing/fund_database.csv` (and merge any updates from
    `data/hf_metadata.csv` saved via `data/data_building.ipynb`) and ensure all
    funds in `data/hf_returns/` have a row in the database, including their
    deterministic `anonymized_code` and `anonymized_name`.
    """
    db: Dict[str, Dict[str, str]] = {}
    needs_write = (not db_path.exists()) or (not DATA_METADATA_PATH.exists()) or (not CONFIDENTIAL_MAPPING_PATH.exists())

    # Read primary and mirror paths (merging non-empty values from whichever was modified most recently)
    candidate_paths = [p for p in [db_path, DATA_METADATA_PATH] if p.exists()]
    candidate_paths.sort(key=lambda p: p.stat().st_mtime)  # older first, newer overwrites non-empty

    for p in candidate_paths:
        with open(p, "r", newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                stem = (row.get("fund_csv") or "").replace(".csv", "").strip()
                if not stem:
                    continue
                if stem not in db:
                    db[stem] = {col: "" for col in FUND_DB_COLUMNS}
                    db[stem]["fund_csv"] = stem
                for col in FUND_DB_COLUMNS:
                    val = (row.get(col) or "").strip()
                    if val != "" or not db[stem].get(col):
                        db[stem][col] = val
                anon_id = get_anonymized_fund_identity(stem)
                if db[stem].get("anonymized_code") != anon_id["anon_code"] or db[stem].get("anonymized_name") != anon_id["anon_name"]:
                    db[stem]["anonymized_code"] = anon_id["anon_code"]
                    db[stem]["anonymized_name"] = anon_id["anon_name"]
                    needs_write = True
                if not db[stem]["display_name"]:
                    db[stem]["display_name"] = format_fund_title(stem)
                if not db[stem]["strategy_subtitle"]:
                    db[stem]["strategy_subtitle"] = format_fund_subtitle(stem)

    # Sync any funds from data/hf_returns/ not yet in fund_database.csv
    for stem in list_available_funds(hf_returns_dir):
        anon_id = get_anonymized_fund_identity(stem)
        if stem not in db:
            db[stem] = {
                "fund_csv": stem,
                "anonymized_code": anon_id["anon_code"],
                "anonymized_name": anon_id["anon_name"],
                "display_name": format_fund_title(stem),
                "strategy_subtitle": format_fund_subtitle(stem),
                "return_basis": "Net",
                "investment_vehicle": "Commingled Fund",
                "management_fee": "2%",
                "performance_fee": "20%",
                "liquidity_terms": "Quarter Liquidity",
                "lockup": "No Lockup",
                "minimum_investment": "1M USD",
                "current_aum": "250M",
                "domicile_structure": "Cayman Islands",
                "notes": "",
            }
            needs_write = True

    if needs_write:
        save_fund_database(db, db_path)

    return db


def save_fund_database(
    db: Dict[str, Dict[str, str]],
    db_path: Path = FUND_DATABASE_PATH,
) -> None:
    """Save the fund metadata dictionary to `third_party_marketing/fund_database.csv`, `data/hf_metadata.csv`, and `confidential_fund_mapping.csv`."""
    for target_path in {db_path, DATA_METADATA_PATH}:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FUND_DB_COLUMNS)
            writer.writeheader()
            for stem in sorted(db.keys()):
                anon_id = get_anonymized_fund_identity(stem)
                row = {col: db[stem].get(col, "") for col in FUND_DB_COLUMNS}
                row["fund_csv"] = stem
                row["anonymized_code"] = anon_id["anon_code"]
                row["anonymized_name"] = anon_id["anon_name"]
                writer.writerow(row)

    # Also write the confidential internal mapping table for quick IP lookup
    CONFIDENTIAL_MAPPING_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIDENTIAL_MAPPING_PATH, "w", newline="", encoding="utf-8") as f:
        map_cols = ["anonymized_code", "anonymized_name", "anonymized_pdf_slug", "fund_csv", "real_display_name", "strategy_subtitle"]
        writer = csv.DictWriter(f, fieldnames=map_cols)
        writer.writeheader()
        for stem in sorted(db.keys()):
            anon_id = get_anonymized_fund_identity(stem)
            writer.writerow({
                "anonymized_code": anon_id["anon_code"],
                "anonymized_name": anon_id["anon_name"],
                "anonymized_pdf_slug": f"{anon_id['anon_slug']}_tearsheet.pdf",
                "fund_csv": stem,
                "real_display_name": db[stem].get("display_name") or format_fund_title(stem),
                "strategy_subtitle": db[stem].get("strategy_subtitle") or format_fund_subtitle(stem),
            })


def get_fund_metadata(
    fund_csv_name: str,
    db_path: Path = FUND_DATABASE_PATH,
    hf_returns_dir: Path = HF_RETURNS_DIR,
) -> Dict[str, str]:
    """Retrieve metadata & commercial terms for a single fund from `fund_database.csv`."""
    stem = fund_csv_name.replace(".csv", "").strip()
    db = init_or_load_fund_database(db_path=db_path, hf_returns_dir=hf_returns_dir)
    if stem in db:
        return dict(db[stem])
    anon_id = get_anonymized_fund_identity(stem)
    return {
        "fund_csv": stem,
        "anonymized_code": anon_id["anon_code"],
        "anonymized_name": anon_id["anon_name"],
        "display_name": format_fund_title(stem),
        "strategy_subtitle": format_fund_subtitle(stem),
        "return_basis": "Net",
        "investment_vehicle": "Commingled Fund",
        "management_fee": "2%",
        "performance_fee": "20%",
        "liquidity_terms": "Quarter Liquidity",
        "lockup": "No Lockup",
        "minimum_investment": "1M USD",
        "current_aum": "250M",
        "domicile_structure": "Cayman Islands",
        "notes": "",
    }


def update_fund_database_entry(
    fund_csv_name: str,
    db_path: Path = FUND_DATABASE_PATH,
    hf_returns_dir: Path = HF_RETURNS_DIR,
    **updates: str,
) -> Dict[str, str]:
    """
    Update one or more fields for `fund_csv_name` in `third_party_marketing/fund_database.csv`
    (e.g. return_basis='Net', management_fee='2.0%', performance_fee='20.0%',
     liquidity_terms='Monthly (30d Notice)', minimum_investment='$1,000,000', current_aum='$150M').
    """
    stem = fund_csv_name.replace(".csv", "").strip()
    db = init_or_load_fund_database(db_path=db_path, hf_returns_dir=hf_returns_dir)
    if stem not in db:
        db[stem] = get_fund_metadata(stem, db_path=db_path, hf_returns_dir=hf_returns_dir)
    for k, v in updates.items():
        if k in FUND_DB_COLUMNS and k != "fund_csv" and v is not None:
            db[stem][k] = str(v).strip()
    save_fund_database(db, db_path=db_path)
    return dict(db[stem])



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
    p1 = math.erfc(math.sqrt(max(0.0, q1) / 2.0))

    r2 = acf(2)
    r3 = acf(3)
    q3 = n * (n + 2) * (
        (r1 ** 2) / (n - 1) + (r2 ** 2) / (n - 2) + (r3 ** 2) / (n - 3)
    )
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
# Step 4: Native Vector TikZ Charts Generator (Growth vs SP500 & Worst 20% SP500)
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


def _build_tikz_charts_section(
    records: List[Dict[str, Any]],
    short_title: str,
    chart_height_cm: float,
) -> str:
    """
    Build two side-by-side vector TikZ charts inside matching tcolorbox panels:
      - Left: Cumulative Growth of $1M USD (Fund vs. S&P 500)
      - Right: Worst 20% S&P 500 Months (Hard Cap at 20 Months, Navy Blue Fund Bars)
    """
    n = len(records)
    W = 7.45  # plot area width in cm
    H = chart_height_cm  # plot area height in cm

    # --- 1. Left Chart Data: Growth of $1M USD (in $ Millions, starting at $1.00M) ---
    w_fund = [1.0]
    w_spx = [1.0]
    for r in records:
        w_fund.append(w_fund[-1] * (1.0 + r["fund"]))
        w_spx.append(w_spx[-1] * (1.0 + r["sp500"]))

    all_w = w_fund + w_spx
    min_w = min(min(all_w), 0.95)
    max_w = max(max(all_w), 1.10)
    span_w = max(max_w - min_w, 0.10)
    y_lo = max(0.0, min_w - 0.06 * span_w)
    y_hi = max_w + 0.12 * span_w

    def map_gx(idx: int) -> float:
        return (idx / n) * W if n > 0 else 0.0

    def map_gy(val: float) -> float:
        return ((val - y_lo) / (y_hi - y_lo)) * H if y_hi > y_lo else H / 2.0

    # Downsample if very many points (>120) to keep TikZ ultra fast
    step = 1 if n <= 120 else 2
    idxs = list(range(0, n + 1, step))
    if idxs[-1] != n:
        idxs.append(n)

    fund_coords = " ".join(f"({map_gx(i):.3f},{map_gy(w_fund[i]):.3f})" for i in idxs)
    spx_coords = " ".join(f"({map_gx(i):.3f},{map_gy(w_spx[i]):.3f})" for i in idxs)
    fill_coords = f"(0.000,0.000) {fund_coords} ({W:.3f},0.000)"

    # 5 horizontal grid lines & y-tick labels for Growth of $1M USD Chart
    g_grid_lines = ""
    for k in range(5):
        yv = y_lo + (k / 4.0) * (y_hi - y_lo)
        yp = map_gy(yv)
        if (y_hi - y_lo) < 2.5:
            lbl = f"\\${yv:,.2f}M"
        else:
            lbl = f"\\${yv:,.1f}M"
        g_grid_lines += (
            f"\\draw[cardborder, densely dashed, line width=0.4pt] (0,{yp:.3f}) -- ({W:.3f},{yp:.3f});\n"
            f"\\node[anchor=east, font=\\sffamily\\tiny, text=mutedtext, inner sep=1.5pt] at (-0.06,{yp:.3f}) {{{lbl}}};\n"
        )

    # $1.00M baseline if inside range
    if y_lo <= 1.0 <= y_hi:
        y1m = map_gy(1.0)
        g_grid_lines += f"\\draw[mutedtext!60, dotted, line width=0.5pt] (0,{y1m:.3f}) -- ({W:.3f},{y1m:.3f});\n"

    # 5 x-axis date labels for Growth Chart
    g_x_ticks = ""
    num_xticks = min(5, n)
    for k in range(num_xticks):
        rec_idx = int(round(k * (n - 1) / max(1, num_xticks - 1)))
        xp = map_gx(rec_idx + 1) if k > 0 else 0.0
        ym = records[rec_idx]["ym"]
        ym_lbl = f"{ym[0]}-{ym[1]:02d}"
        g_x_ticks += (
            f"\\draw[cardborder, line width=0.4pt] ({xp:.3f},0) -- ({xp:.3f},-0.08);\n"
            f"\\node[anchor=north, font=\\sffamily\\tiny, text=mutedtext, inner sep=1.5pt] at ({xp:.3f},-0.10) {{{ym_lbl}}};\n"
        )

    # --- 2. Right Chart Data: Worst 20% S&P 500 Months (Hard Cap at 20 Months) ---
    sp_vals = [r["sp500"] for r in records]
    q20 = _quantile_linear(sp_vals, 0.20)
    worst_recs = [r for r in records if r["sp500"] <= q20]
    worst_recs.sort(key=lambda r: r["sp500"])  # Most negative SPX month first
    worst_recs = worst_recs[:20]  # Hard cap at maximum of 20 months
    if not worst_recs:
        worst_recs = sorted(records, key=lambda r: r["sp500"])[: min(5, n)]

    k_bars = len(worst_recs)
    bar_vals = [r["sp500"] * 100.0 for r in worst_recs] + [r["fund"] * 100.0 for r in worst_recs]
    b_min = min(min(bar_vals), -2.0) * 1.15
    b_max = max(max(bar_vals), 2.0) * 1.18
    if b_max - b_min < 4.0:
        b_max += 2.0
        b_min -= 2.0

    def map_by(pct_val: float) -> float:
        return ((pct_val - b_min) / (b_max - b_min)) * H

    y_zero = map_by(0.0)

    # 5 horizontal grid lines & y-tick labels for Bar Chart
    b_grid_lines = ""
    for k in range(5):
        bv = b_min + (k / 4.0) * (b_max - b_min)
        bp = map_by(bv)
        b_grid_lines += (
            f"\\draw[cardborder, densely dashed, line width=0.4pt] (0,{bp:.3f}) -- ({W:.3f},{bp:.3f});\n"
            f"\\node[anchor=east, font=\\sffamily\\tiny, text=mutedtext, inner sep=1.5pt] at (-0.06,{bp:.3f}) {{{bv:+.0f}\\%}};\n"
        )

    # Bars & x-axis labels for Worst 20% SPX Months (Hard Cap 20, same navy blue color for Fund)
    slot_w = W / max(1, k_bars)
    gap_half = 0.012 if k_bars <= 12 else 0.006
    bar_w = min(0.28, slot_w * 0.36)
    bars_tikz = ""
    for idx, r in enumerate(worst_recs):
        cx = (idx + 0.5) * slot_w
        spx_pct = r["sp500"] * 100.0
        fnd_pct = r["fund"] * 100.0
        ys = map_by(spx_pct)
        yf = map_by(fnd_pct)

        # SPX bar (left of pair, slate grey)
        x1_s, x2_s = cx - bar_w - gap_half, cx - gap_half
        y1_s, y2_s = min(y_zero, ys), max(y_zero, ys)
        bars_tikz += f"\\fill[primary!40] ({x1_s:.3f},{y1_s:.3f}) rectangle ({x2_s:.3f},{y2_s:.3f});\n"

        # Fund bar (right of pair, always same navy blue 'accent' color for both up and down months)
        x1_f, x2_f = cx + gap_half, cx + bar_w + gap_half
        y1_f, y2_f = min(y_zero, yf), max(y_zero, yf)
        bars_tikz += f"\\fill[accent] ({x1_f:.3f},{y1_f:.3f}) rectangle ({x2_f:.3f},{y2_f:.3f});\n"

        ym_short = f"{str(r['year'])[2:]}-{r['month']:02d}"
        if k_bars <= 10:
            bars_tikz += (
                f"\\node[anchor=north, font=\\sffamily\\tiny, text=mutedtext, inner sep=1.5pt] at ({cx:.3f},-0.10) {{{ym_short}}};\n"
            )
        else:
            bars_tikz += (
                f"\\node[rotate=45, anchor=north east, font=\\sffamily\\fontsize{{4.6}}{{5.6}}\\selectfont, text=mutedtext, inner sep=0.8pt] at ({cx+0.04:.3f},-0.06) {{{ym_short}}};\n"
            )

    bars_tikz += f"\\draw[primary!80, line width=0.55pt] (0,{y_zero:.3f}) -- ({W:.3f},{y_zero:.3f});\n"

    words = short_title.split()
    short_words: List[str] = []
    for w in words:
        if sum(len(x) for x in short_words) + len(short_words) + len(w) <= 20:
            short_words.append(w)
        else:
            break
    short_lbl = escape_latex(" ".join(short_words) if short_words else short_title[:18])
    fund_end_lbl = f"\\${w_fund[-1]:,.2f}M" if w_fund[-1] < 10.0 else f"\\${w_fund[-1]:,.1f}M"
    spx_end_lbl = f"\\${w_spx[-1]:,.2f}M" if w_spx[-1] < 10.0 else f"\\${w_spx[-1]:,.1f}M"

    charts_latex = rf"""% --- SECTION 3: GROWTH OF $1M USD VS SP500 & WORST 20% SP500 MONTHS CHARTS ---
\noindent
\begin{{tcolorbox}}[nobeforeafter, box align=top, width=0.492\textwidth, colback=white, colframe=primary, title=\textbf{{\small\strut Cumulative Growth of \$1M USD (Fund vs. S\&P 500)}}, fonttitle=\sffamily\bfseries\small, arc=5pt, boxrule=0.9pt, toptitle=3.5pt, bottomtitle=3.5pt, left=4pt, right=4pt, top=3pt, bottom=2pt, colbacktitle=primary, halign title=center]
\centering
\begin{{tikzpicture}}[x=1cm, y=1cm]
    \useasboundingbox (-0.95,-0.46) rectangle ({W+0.15:.2f},{H+0.42:.2f});
    {g_grid_lines}
    \fill[accent!10!white] {fill_coords} -- cycle;
    \draw[primary!45, line width=1.1pt] plot coordinates {{{spx_coords}}};
    \draw[accent, line width=1.5pt] plot coordinates {{{fund_coords}}};
    \draw[cardborder, line width=0.6pt] (0,0) rectangle ({W:.3f},{H:.3f});
    {g_x_ticks}
    % Legend
    \draw[accent, line width=1.6pt] (0.15,{H+0.20:.3f}) -- (0.55,{H+0.20:.3f});
    \node[anchor=west, font=\sffamily\tiny\bfseries, text=primary] at (0.60,{H+0.20:.3f}) {{{short_lbl} ({fund_end_lbl})}};
    \draw[primary!45, line width=1.2pt] (3.95,{H+0.20:.3f}) -- (4.35,{H+0.20:.3f});
    \node[anchor=west, font=\sffamily\tiny, text=mutedtext] at (4.40,{H+0.20:.3f}) {{S\&P 500 ({spx_end_lbl})}};
\end{{tikzpicture}}
\end{{tcolorbox}}\hfill
\begin{{tcolorbox}}[nobeforeafter, box align=top, width=0.492\textwidth, colback=white, colframe=primary, title=\textbf{{\small\strut Worst 20\% S\&P 500 Months}}, fonttitle=\sffamily\bfseries\small, arc=5pt, boxrule=0.9pt, toptitle=3.5pt, bottomtitle=3.5pt, left=4pt, right=4pt, top=3pt, bottom=2pt, colbacktitle=primary, halign title=center]
\centering
\begin{{tikzpicture}}[x=1cm, y=1cm]
    \useasboundingbox (-0.95,-0.46) rectangle ({W+0.15:.2f},{H+0.42:.2f});
    {b_grid_lines}
    {bars_tikz}
    \draw[cardborder, line width=0.6pt] (0,0) rectangle ({W:.3f},{H:.3f});
    % Legend
    \fill[accent] (0.85,{H+0.13:.3f}) rectangle (1.15,{H+0.27:.3f});
    \node[anchor=west, font=\sffamily\tiny\bfseries, text=primary] at (1.22,{H+0.20:.3f}) {{{short_lbl}}};
    \fill[primary!40] (4.35,{H+0.13:.3f}) rectangle (4.65,{H+0.27:.3f});
    \node[anchor=west, font=\sffamily\tiny, text=mutedtext] at (4.72,{H+0.20:.3f}) {{S\&P 500}};
\end{{tikzpicture}}
\end{{tcolorbox}}
"""
    return charts_latex


# ---------------------------------------------------------------------------
# Step 5: Modern 2-Page LaTeX Document Generator
# ---------------------------------------------------------------------------
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
    records: List[Dict[str, Any]],
    metrics: Dict[str, Any],
    monthly_matrix: Dict[int, Dict[Union[int, str], float]],
    logo_rel_path: str = "athenee_logo.png",
    custom_title: Optional[str] = None,
    custom_subtitle: Optional[str] = None,
    fund_meta: Optional[Dict[str, str]] = None,
    anonymize: bool = True,
) -> str:
    """
    Generate the complete 2-page modern LaTeX document:
      - Page 1: Logo + Header (with anonymized mandate name by default) +
                6 KPI Cards (CAGR, Vol, Sharpe, MDD, Alpha w/ t-stat, Beta & Corr w/ Beta t-stat) +
                2 Strictly-Aligned Quantitative Indicator Boxes +
                Side-by-Side Growth ($1M USD) & Worst-20% SPX Charts +
                Dynamically Proportioned Monthly Return Matrix (without black horizontal rules) +
                Structured Fund Terms & Commercial Overview Box at the bottom of Page 1
      - Page 2: Capital Introduction Legal / Risk Disclaimer on TOP, followed by Quantitative Appendix A & B
    """
    stem = fund_csv_name.replace(".csv", "").strip()
    db_meta = get_fund_metadata(stem)
    if fund_meta:
        for k, v in fund_meta.items():
            if v is not None and str(v).strip() != "":
                db_meta[k] = str(v).strip()

    real_disp_name = db_meta.get("display_name") or format_fund_title(stem)
    raw_subtitle_base = custom_subtitle if custom_subtitle else (db_meta.get("strategy_subtitle") or format_fund_subtitle(stem))

    if anonymize:
        anon_id = get_anonymized_fund_identity(stem)
        raw_title = f"{anon_id['anon_name']} ({anon_id['anon_code']})"
        chart_short_title = anon_id["anon_name"]
        raw_subtitle = scrub_fund_name_from_text(raw_subtitle_base, stem, real_disp_name)
    else:
        raw_title = custom_title if custom_title else real_disp_name
        chart_short_title = raw_title
        raw_subtitle = raw_subtitle_base

    display_title = escape_latex(raw_title)
    display_subtitle = escape_latex(raw_subtitle)

    # Discretionary Net / Gross Return Basis
    raw_basis = (db_meta.get("return_basis") or "").strip()
    if raw_basis.lower() in ("net", "net of fees"):
        cagr_card_title = "CAGR (Net)"
        matrix_box_title = r"Historical Monthly \& Yearly Net Return Matrix (\%)"
        basis_display = "Net of Fees"
    elif raw_basis.lower() in ("gross", "gross of fees"):
        cagr_card_title = "CAGR (Gross)"
        matrix_box_title = r"Historical Monthly \& Yearly Gross Return Matrix (\%)"
        basis_display = "Gross of Fees"
    elif raw_basis:
        cagr_card_title = f"CAGR ({escape_latex(raw_basis)})"
        matrix_box_title = rf"Historical Monthly \& Yearly {escape_latex(raw_basis)} Return Matrix (\%)"
        basis_display = escape_latex(raw_basis)
    else:
        # Unspecified / discretionary default: do not state Net or Gross
        cagr_card_title = "CAGR"
        matrix_box_title = r"Historical Monthly \& Yearly Return Matrix (\%)"
        basis_display = ""

    # Commercial Terms from `fund_database.csv` (discretionary: only shown when populated)
    vehicle = (db_meta.get("investment_vehicle") or "").strip()
    mgmt_fee = (db_meta.get("management_fee") or "").strip()
    perf_fee = (db_meta.get("performance_fee") or "").strip()
    liquidity = (db_meta.get("liquidity_terms") or "").strip()
    lockup = (db_meta.get("lockup") or "").strip()
    min_inv = (db_meta.get("minimum_investment") or "").strip()
    curr_aum = (db_meta.get("current_aum") or "").strip()
    domicile = (db_meta.get("domicile_structure") or "").strip()
    notes = (db_meta.get("notes") or "").strip()

    # Optional Page 1 Bottom Box: Structured Fund Terms & Commercial Overview
    has_any_db_terms = any([vehicle, basis_display, mgmt_fee, perf_fee, liquidity, lockup, min_inv, curr_aum, domicile, notes])
    if has_any_db_terms:
        fee_val = " / ".join(
            x for x in [
                f"{escape_latex(mgmt_fee)} Mgmt" if mgmt_fee else "",
                f"{escape_latex(perf_fee)} Perf" if perf_fee else "",
            ] if x
        )
        # Collect (Label, Value) pairs for the structured grid
        term_pairs: List[Tuple[str, str]] = []
        if vehicle:
            term_pairs.append(("Vehicle", escape_latex(vehicle)))
        if basis_display:
            term_pairs.append(("Return Basis", basis_display))
        if fee_val:
            term_pairs.append(("Fee Structure", fee_val))
        if liquidity:
            term_pairs.append(("Liquidity", escape_latex(liquidity)))
        if lockup:
            term_pairs.append(("Lock-Up Period", escape_latex(lockup)))
        if min_inv:
            term_pairs.append(("Min. Investment", escape_latex(min_inv)))
        if curr_aum:
            term_pairs.append(("Current AUM", escape_latex(curr_aum)))
        if domicile:
            term_pairs.append(("Domicile", escape_latex(domicile)))
        if notes:
            term_pairs.append(("Share Class / Notes", escape_latex(notes)))

        # Pad to a multiple of 4 cells per row so the 4-column grid is always balanced
        ncols_grid = 4
        while len(term_pairs) % ncols_grid != 0:
            term_pairs.append(("", ""))

        grid_rows_latex = ""
        n_grid_rows = len(term_pairs) // ncols_grid
        for r_idx in range(n_grid_rows):
            row_slice = term_pairs[r_idx * ncols_grid : (r_idx + 1) * ncols_grid]
            row_cells: List[str] = []
            for lbl, val in row_slice:
                if lbl:
                    row_cells.append(
                        rf"\textbf{{\textcolor{{mutedtext}}{{\strut {lbl}:}}}}\hfill \textbf{{\textcolor{{primary}}{{\strut {val}}}}}"
                    )
                else:
                    row_cells.append(r"\strut")
            row_bg = r"\rowcolor{cardbg} " if (r_idx % 2 == 1) else ""
            grid_rows_latex += row_bg + " & ".join(row_cells) + r" \\" + "\n"

        page1_terms_box_latex = rf"""\vspace{{{ "{section_gap}" }}}

% --- SECTION 5: FUND TERMS & COMMERCIAL OVERVIEW BOX (BOTTOM OF PAGE 1) ---
\begin{{tcolorbox}}[colback=white, colframe=primary, title=\textbf{{\small\strut Fund Terms \& Commercial Overview}}, fonttitle=\sffamily\bfseries\small, arc=5pt, boxrule=0.9pt, toptitle=3.5pt, bottomtitle=3.5pt, left=4pt, right=4pt, top=2.5pt, bottom=2.5pt, colbacktitle=primary, halign title=center]
\renewcommand{{\arraystretch}}{{1.38}}
\setlength{{\tabcolsep}}{{6pt}}
\scriptsize
\begin{{tabularx}}{{\textwidth}}{{X !{{\color{{cardborder}}\vrule width 0.6pt}} X !{{\color{{cardborder}}\vrule width 0.6pt}} X !{{\color{{cardborder}}\vrule width 0.6pt}} X}}
{grid_rows_latex}\end{{tabularx}}
\end{{tcolorbox}}"""
    else:
        page1_terms_box_latex = ""

    n_years_rows = len(monthly_matrix)

    # Dynamic vertical proportioning so the Monthly Return Matrix, Charts, and Terms Box fill Page 1 top-to-bottom!
    if n_years_rows <= 4:
        matrix_fontsize = r"\small"
        matrix_arraystretch = f"{2.42 - 0.12 * n_years_rows:.2f}" if has_any_db_terms else f"{2.65 - 0.14 * n_years_rows:.2f}"
        matrix_top_bot_pad = "6pt" if has_any_db_terms else "8pt"
        chart_height_cm = 4.30 if has_any_db_terms else 4.80
        stats_arraystretch = "1.25" if has_any_db_terms else "1.28"
        section_gap = "0.48em" if has_any_db_terms else "0.60em"
    elif n_years_rows <= 7:
        matrix_fontsize = r"\footnotesize"
        matrix_arraystretch = f"{2.05 - 0.07 * n_years_rows:.2f}" if has_any_db_terms else f"{2.25 - 0.08 * n_years_rows:.2f}"
        matrix_top_bot_pad = "4.5pt" if has_any_db_terms else "6pt"
        chart_height_cm = 3.75 if has_any_db_terms else 4.25
        stats_arraystretch = "1.21" if has_any_db_terms else "1.24"
        section_gap = "0.40em" if has_any_db_terms else "0.50em"
    elif n_years_rows <= 11:
        matrix_fontsize = r"\footnotesize"
        matrix_arraystretch = f"{1.78 - 0.04 * n_years_rows:.2f}" if has_any_db_terms else f"{1.95 - 0.045 * n_years_rows:.2f}"
        matrix_top_bot_pad = "3.5pt" if has_any_db_terms else "4.5pt"
        chart_height_cm = 3.20 if has_any_db_terms else 3.70
        stats_arraystretch = "1.17" if has_any_db_terms else "1.20"
        section_gap = "0.32em" if has_any_db_terms else "0.40em"
    elif n_years_rows <= 18:
        matrix_fontsize = r"\scriptsize"
        matrix_arraystretch = f"{1.45 - 0.018 * n_years_rows:.2f}" if has_any_db_terms else f"{1.56 - 0.022 * n_years_rows:.2f}"
        matrix_top_bot_pad = "2pt" if has_any_db_terms else "2.5pt"
        chart_height_cm = 2.40 if has_any_db_terms else 2.75
        stats_arraystretch = "1.13" if has_any_db_terms else "1.16"
        section_gap = "0.25em" if has_any_db_terms else "0.30em"
    else:
        matrix_fontsize = r"\tiny"
        matrix_arraystretch = f"{max(0.88, 1.24 - 0.013 * n_years_rows):.2f}" if has_any_db_terms else f"{max(0.95, 1.32 - 0.014 * n_years_rows):.2f}"
        matrix_top_bot_pad = "1pt"
        chart_height_cm = 1.95 if has_any_db_terms else 2.15
        stats_arraystretch = "1.06" if has_any_db_terms else "1.10"
        section_gap = "0.18em" if has_any_db_terms else "0.22em"

    if page1_terms_box_latex:
        page1_terms_box_latex = page1_terms_box_latex.replace("{section_gap}", section_gap)

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

    alpha_pct_only_str = fmt_pct(metrics["alpha"])
    alpha_tstat_only_str = fmt_num(metrics["alpha_tstat"])
    beta_num_only_str = fmt_num(metrics["beta"])
    beta_tstat_only_str = fmt_num(metrics["beta_tstat"])

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

    pearson_str = fmt_num(metrics["pearson_corr"], signed=True)
    spearman_str = fmt_num(metrics["spearman_corr"], signed=True)
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
        f"\\alpha={fmt_pct(metrics['up_alpha'], 1)},\\ \\beta={fmt_num(metrics['up_beta'])}"
        if not _isna(metrics["up_alpha"])
        else "-"
    )
    down_reg_str = (
        f"\\alpha={fmt_pct(metrics['down_alpha'], 1)},\\ \\beta={fmt_num(metrics['down_beta'])}"
        if not _isna(metrics["down_alpha"])
        else "-"
    )

    q1_corr_str = (
        f"r={fmt_num(metrics['q1_pearson'])},\\ \\rho={fmt_num(metrics['q1_spearman'])}\\ (n={metrics['n_q1']})"
        if not _isna(metrics["q1_pearson"])
        else "-"
    )
    d1_corr_str = (
        f"r={fmt_num(metrics['d1_pearson'])},\\ \\rho={fmt_num(metrics['d1_spearman'])}\\ (n={metrics['n_d1']})"
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
        lb_status = "Pass" if (lb1_pval >= 0.05 and lb3_pval >= 0.05) else "Serial Corr."
        lb_str = f"p_1={fmt_num(lb1_pval, 2)},\\ p_3={fmt_num(lb3_pval, 2)}\\ (\\text{{{lb_status}}})"
    else:
        lb_str = "-"

    start_date_str = escape_latex(str(metrics["start_date"]))
    end_date_str = escape_latex(str(metrics["end_date"]))
    period_str = escape_latex(
        f"{metrics['start_date']} - {metrics['end_date']} ({metrics['n_months']} Months / {metrics['years_elapsed']:.1f} Years)"
    )

    # Build the two side-by-side TikZ charts
    charts_section_latex = _build_tikz_charts_section(
        records=records,
        short_title=chart_short_title,
        chart_height_cm=chart_height_cm,
    )

    latex_doc = rf"""\documentclass[10pt,a4paper]{{article}}
\usepackage[utf8]{{inputenc}}
\usepackage[T1]{{fontenc}}
\usepackage[left=0.30in, right=0.30in, top=0.24in, bottom=0.24in]{{geometry}}
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
\begin{{minipage}}[c]{{0.69\textwidth}}
    {{\fontsize{{19}}{{23}}\selectfont \bfseries \textcolor{{primary}}{{{display_title}}}}}\\[2.5pt]
    {{\small \bfseries \textcolor{{accent}}{{{display_subtitle}}}}}\\[3pt]
    {{\footnotesize \textcolor{{primary}}{{\textbf{{Track Record: {start_date_str} -- {end_date_str}}}}} \ \textcolor{{goldaccent}}{{\textbf{{({metrics['n_months']} Months / {metrics['years_elapsed']:.1f} Years)}}}} \quad $\vert$ \quad \textcolor{{mutedtext}}{{\textbf{{Benchmark:}} S\&P 500 Total Return}}}}
\end{{minipage}}%
\hfill
\begin{{minipage}}[c]{{0.29\textwidth}}
    \raggedleft
    \includegraphics[height=1.08cm, keepaspectratio]{{{logo_rel_path}}}\\[1.5pt]
    {{\tiny \bfseries \textcolor{{goldaccent}}{{CAPITAL INTRODUCTION \& THIRD-PARTY MARKETING}}}}
\end{{minipage}}

\vspace{{0.22em}}
\noindent{{\color{{goldaccent}}\rule{{\textwidth}}{{1.4pt}}}}
\vspace{{{section_gap}}}

% --- SECTION 1: 6 TOP-LINE KPI HIGHLIGHT CARDS (INCL. DEDICATED ALPHA BOX + BETA & CORR BOX) ---
\noindent
\begin{{tcolorbox}}[nobeforeafter, box align=top, width=0.160\textwidth, colback=white, colframe=primary, title=\textbf{{\scriptsize\strut {cagr_card_title}}}, fonttitle=\sffamily\bfseries\scriptsize, arc=4pt, boxrule=0.8pt, toptitle=3pt, bottomtitle=3pt, left=1.5pt, right=1.5pt, top=3.5pt, bottom=3.5pt, colbacktitle=primary, halign title=center]
    \centering
    {{\large \bfseries \textcolor{{primary}}{{\strut {cagr_str}}}}}\\[1.5pt]
    {{\tiny \textcolor{{mutedtext}}{{\strut S\&P 500: {sp_cagr_str}}}}}
\end{{tcolorbox}}\hfill
\begin{{tcolorbox}}[nobeforeafter, box align=top, width=0.160\textwidth, colback=white, colframe=primary, title=\textbf{{\scriptsize\strut Ann. Volatility}}, fonttitle=\sffamily\bfseries\scriptsize, arc=4pt, boxrule=0.8pt, toptitle=3pt, bottomtitle=3pt, left=1.5pt, right=1.5pt, top=3.5pt, bottom=3.5pt, colbacktitle=primary, halign title=center]
    \centering
    {{\large \bfseries \textcolor{{primary}}{{\strut {vol_str}}}}}\\[1.5pt]
    {{\tiny \textcolor{{mutedtext}}{{\strut S\&P 500: {sp_vol_str}}}}}
\end{{tcolorbox}}\hfill
\begin{{tcolorbox}}[nobeforeafter, box align=top, width=0.160\textwidth, colback=white, colframe=primary, title=\textbf{{\scriptsize\strut Sharpe Ratio}}, fonttitle=\sffamily\bfseries\scriptsize, arc=4pt, boxrule=0.8pt, toptitle=3pt, bottomtitle=3pt, left=1.5pt, right=1.5pt, top=3.5pt, bottom=3.5pt, colbacktitle=primary, halign title=center]
    \centering
    {{\large \bfseries \textcolor{{primary}}{{\strut {sharpe_str}}}}}\\[1.5pt]
    {{\tiny \textcolor{{mutedtext}}{{\strut SPX: {sp_sharpe_str} $\vert$ Sortino: {sortino_str}}}}}
\end{{tcolorbox}}\hfill
\begin{{tcolorbox}}[nobeforeafter, box align=top, width=0.160\textwidth, colback=white, colframe=primary, title=\textbf{{\scriptsize\strut Max Drawdown}}, fonttitle=\sffamily\bfseries\scriptsize, arc=4pt, boxrule=0.8pt, toptitle=3pt, bottomtitle=3pt, left=1.5pt, right=1.5pt, top=3.5pt, bottom=3.5pt, colbacktitle=primary, halign title=center]
    \centering
    {{\large \bfseries \textcolor{{primary}}{{\strut {mdd_str}}}}}\\[1.5pt]
    {{\tiny \textcolor{{mutedtext}}{{\strut SPX: {sp_mdd_str} $\vert$ Calmar: {calmar_str}}}}}
\end{{tcolorbox}}\hfill
\begin{{tcolorbox}}[nobeforeafter, box align=top, width=0.160\textwidth, colback=white, colframe=primary, title=\textbf{{\scriptsize\strut Alpha (Ann.)}}, fonttitle=\sffamily\bfseries\scriptsize, arc=4pt, boxrule=0.8pt, toptitle=3pt, bottomtitle=3pt, left=1.5pt, right=1.5pt, top=3.5pt, bottom=3.5pt, colbacktitle=primary, halign title=center]
    \centering
    {{\large \bfseries \textcolor{{primary}}{{\strut {alpha_pct_only_str}}}}}\\[1.5pt]
    {{\tiny \textcolor{{mutedtext}}{{\strut $t$-stat: {alpha_tstat_only_str}}}}}
\end{{tcolorbox}}\hfill
\begin{{tcolorbox}}[nobeforeafter, box align=top, width=0.160\textwidth, colback=white, colframe=primary, title=\textbf{{\scriptsize\strut Beta \& Corr.}}, fonttitle=\sffamily\bfseries\scriptsize, arc=4pt, boxrule=0.8pt, toptitle=3pt, bottomtitle=3pt, left=1.5pt, right=1.5pt, top=3.5pt, bottom=3.5pt, colbacktitle=primary, halign title=center]
    \centering
    {{\large \bfseries \textcolor{{primary}}{{\strut {beta_num_only_str} $\vert$ {pearson_str}}}}}\\[1.5pt]
    {{\tiny \textcolor{{mutedtext}}{{\strut Beta $t$-stat: {beta_tstat_only_str}}}}}
\end{{tcolorbox}}

\vspace{{{section_gap}}}

% --- SECTION 2: COMPREHENSIVE SINGLE-FUND ANALYSIS INDICATORS (STRICTLY ALIGNED 13 ROWS EACH) ---
\noindent
\begin{{tcolorbox}}[nobeforeafter, box align=top, width=0.492\textwidth, colback=white, colframe=primary, title=\textbf{{\small\strut Performance, Risk \& Hit Rate Indicators}}, fonttitle=\sffamily\bfseries\small, arc=5pt, boxrule=0.9pt, toptitle=3.5pt, bottomtitle=3.5pt, left=4pt, right=4pt, top=1pt, bottom=1pt, colbacktitle=primary]
\renewcommand{{\arraystretch}}{{{stats_arraystretch}}}
\setlength{{\tabcolsep}}{{2pt}}
\scriptsize
\begin{{tabular*}}{{\textwidth}}{{@{{\extracolsep{{\fill}}}} l r r @{{}}}}
\rowcolor{{primary!10!white}}[0pt][0pt] \textbf{{\textcolor{{primary}}{{\strut Indicator}}}} & \textbf{{\textcolor{{primary}}{{\strut Fund}}}} & \textbf{{\textcolor{{mutedtext}}{{\strut S\&P 500}}}} \\
\textbf{{\textcolor{{primary}}{{\strut CAGR (Annualized)}}}} & \textbf{{\textcolor{{primary}}{{{cagr_str}}}}} & \textcolor{{mutedtext}}{{{sp_cagr_str}}} \\
\rowcolor{{cardbg}}[0pt][0pt] \textbf{{\textcolor{{primary}}{{\strut Annualized Mean Return}}}} & \textcolor{{primary}}{{{ann_mean_str}}} & \textcolor{{mutedtext}}{{{sp_ann_mean_str}}} \\
\textbf{{\textcolor{{primary}}{{\strut Annualized Volatility}}}} & \textcolor{{primary}}{{{vol_str}}} & \textcolor{{mutedtext}}{{{sp_vol_str}}} \\
\rowcolor{{cardbg}}[0pt][0pt] \textbf{{\textcolor{{primary}}{{\strut Proxy Sharpe Ratio ($r_f = 0\%$)}}}} & \textbf{{\textcolor{{primary}}{{{sharpe_str}}}}} & \textcolor{{mutedtext}}{{{sp_sharpe_str}}} \\
\textbf{{\textcolor{{primary}}{{\strut Annualized Sortino Ratio}}}} & \textcolor{{primary}}{{{sortino_str}}} & \textcolor{{mutedtext}}{{{sp_sortino_str}}} \\
\rowcolor{{cardbg}}[0pt][0pt] \textbf{{\textcolor{{primary}}{{\strut Maximum Drawdown (MDD)}}}} & \textbf{{\textcolor{{primary}}{{{mdd_str}}}}} & \textcolor{{mutedtext}}{{{sp_mdd_str}}} \\
\textbf{{\textcolor{{primary}}{{\strut Calmar Ratio (CAGR / $|$MDD$|$)}}}} & \textcolor{{primary}}{{{calmar_str}}} & \textcolor{{mutedtext}}{{{sp_calmar_str}}} \\
\rowcolor{{cardbg}}[0pt][0pt] \textbf{{\textcolor{{primary}}{{\strut Cumulative Total Return}}}} & \textcolor{{primary}}{{{cum_ret_str}}} & \textcolor{{mutedtext}}{{{sp_cum_ret_str}}} \\
\textbf{{\textcolor{{primary}}{{\strut Best / Worst Monthly}}}} & \textcolor{{primary}}{{{best_m_str} / {worst_m_str}}} & \textcolor{{mutedtext}}{{{sp_best_m_str} / {sp_worst_m_str}}} \\
\rowcolor{{cardbg}}[0pt][0pt] \textbf{{\textcolor{{primary}}{{\strut Positive Months (Hit Rate)}}}} & \textcolor{{primary}}{{{pos_months_str}}} & \textcolor{{mutedtext}}{{{sp_pos_months_str}}} \\
\textbf{{\textcolor{{primary}}{{\strut Crisis Hit Rate ($\text{{Fund}}>0 \mid \text{{SPX}}<0$)}}}} & \textbf{{\textcolor{{primary}}{{{crisis_hit_str}}}}} & \textcolor{{mutedtext}}{{--}} \\
\rowcolor{{cardbg}}[0pt][0pt] \textbf{{\textcolor{{primary}}{{\strut Up-Mkt Loss ($\text{{Fund}}<0 \mid \text{{SPX}}>0$)}}}} & \textcolor{{primary}}{{{up_loss_str}}} & \textcolor{{mutedtext}}{{--}} \\
\end{{tabular*}}
\end{{tcolorbox}}\hfill
\begin{{tcolorbox}}[nobeforeafter, box align=top, width=0.492\textwidth, colback=white, colframe=primary, title=\textbf{{\small\strut Alpha, Beta, Correlation \& Tail Analysis (vs. S\&P 500)}}, fonttitle=\sffamily\bfseries\small, arc=5pt, boxrule=0.9pt, toptitle=3.5pt, bottomtitle=3.5pt, left=4pt, right=4pt, top=1pt, bottom=1pt, colbacktitle=primary]
\renewcommand{{\arraystretch}}{{{stats_arraystretch}}}
\setlength{{\tabcolsep}}{{2pt}}
\scriptsize
\begin{{tabular*}}{{\textwidth}}{{@{{\extracolsep{{\fill}}}} l r @{{}}}}
\rowcolor{{primary!10!white}}[0pt][0pt] \textbf{{\textcolor{{primary}}{{\strut Quantitative Metric}}}} & \textbf{{\textcolor{{primary}}{{\strut Estimate / Diagnostic}}}} \\
\textbf{{\textcolor{{primary}}{{\strut Annualized Alpha ($\alpha$) \& $t$-stat}}}} & \textbf{{\textcolor{{primary}}{{{alpha_str}}}}} \\
\rowcolor{{cardbg}}[0pt][0pt] \textbf{{\textcolor{{primary}}{{\strut Market Beta ($\beta_{{\text{{SPX}}}}$) \& $t$-stat}}}} & \textcolor{{primary}}{{{beta_str} ($R^2={r2_str}$)}} \\
\textbf{{\textcolor{{primary}}{{\strut Pearson Correlation ($r$) to S\&P 500}}}} & \textbf{{\textcolor{{primary}}{{{pearson_str}}}}} \textcolor{{mutedtext}}{{(95\% Blk CI: {pearson_blk_ci_str})}} \\
\rowcolor{{cardbg}}[0pt][0pt] \textbf{{\textcolor{{primary}}{{\strut Spearman Rank Correlation ($\rho$)}}}} & \textcolor{{primary}}{{{spearman_str}}} \textcolor{{mutedtext}}{{(95\% Blk CI: {spearman_blk_ci_str})}} \\
\textbf{{\textcolor{{primary}}{{\strut Upside / Downside Capture Ratio}}}} & \textcolor{{primary}}{{Up: \textbf{{{up_cap_str}}} $\vert$ Down: \textbf{{{down_cap_str}}}}} \\
\rowcolor{{cardbg}}[0pt][0pt] \textbf{{\textcolor{{primary}}{{\strut Cond. Up-Market ($\text{{SPX}}>0$)}}}} & \textcolor{{primary}}{{${up_reg_str}$}} \\
\textbf{{\textcolor{{primary}}{{\strut Cond. Down-Market ($\text{{SPX}}<0$)}}}} & \textcolor{{primary}}{{${down_reg_str}$}} \\
\rowcolor{{cardbg}}[0pt][0pt] \textbf{{\textcolor{{primary}}{{\strut Tail Corr. ($\text{{SPX}} < Q_1$, Worst 25\%)}}}} & \textcolor{{primary}}{{${q1_corr_str}$}} \\
\textbf{{\textcolor{{primary}}{{\strut Tail Corr. ($\text{{SPX}} < D_1$, Worst 10\%)}}}} & \textcolor{{primary}}{{${d1_corr_str}$}} \\
\rowcolor{{cardbg}}[0pt][0pt] \textbf{{\textcolor{{primary}}{{\strut Worst 20\% SPX Months Avg. Return}}}} & \textcolor{{primary}}{{{worst20_str}}} \\
\textbf{{\textcolor{{primary}}{{\strut Cross-Asset Beta (WTI / BTC)}}}} & \textcolor{{primary}}{{{wti_btc_compact}}} \\
\rowcolor{{cardbg}}[0pt][0pt] \textbf{{\textcolor{{primary}}{{\strut Ljung-Box Serial Correlation}}}} & \textcolor{{primary}}{{${lb_str}$}} \\
\end{{tabular*}}
\end{{tcolorbox}}

\vspace{{{section_gap}}}

{charts_section_latex}

\vspace{{{section_gap}}}

% --- SECTION 4: MONTHLY RETURN MATRIX (NO BLACK HORIZONTAL RULES) ---
\begin{{tcolorbox}}[colback=white, colframe=primary, title=\textbf{{\small\strut {matrix_box_title}}}, fonttitle=\sffamily\bfseries\small, arc=5pt, boxrule=0.9pt, toptitle=3.5pt, bottomtitle=3.5pt, left=3pt, right=3pt, top={matrix_top_bot_pad}, bottom={matrix_top_bot_pad}, colbacktitle=primary, halign title=center]
\renewcommand{{\arraystretch}}{{{matrix_arraystretch}}}
{matrix_fontsize}
\begin{{tabularx}}{{\textwidth}}{{l *{{12}}{{>{{\centering\arraybackslash}}X}} >{{\centering\arraybackslash}}p{{1.15cm}}}}
\rowcolor{{primary!8!white}}
\textbf{{\textcolor{{primary}}{{Year}}}} & \textbf{{\textcolor{{primary}}{{Jan}}}} & \textbf{{\textcolor{{primary}}{{Feb}}}} & \textbf{{\textcolor{{primary}}{{Mar}}}} & \textbf{{\textcolor{{primary}}{{Apr}}}} & \textbf{{\textcolor{{primary}}{{May}}}} & \textbf{{\textcolor{{primary}}{{Jun}}}} & \textbf{{\textcolor{{primary}}{{Jul}}}} & \textbf{{\textcolor{{primary}}{{Aug}}}} & \textbf{{\textcolor{{primary}}{{Sep}}}} & \textbf{{\textcolor{{primary}}{{Oct}}}} & \textbf{{\textcolor{{primary}}{{Nov}}}} & \textbf{{\textcolor{{primary}}{{Dec}}}} & \textbf{{\textcolor{{primary}}{{Yearly}}}} \\
{matrix_rows_latex}\end{{tabularx}}
\end{{tcolorbox}}
{page1_terms_box_latex}

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
%% PAGE 2: LEGAL DISCLAIMER (TOP) + QUANTITATIVE METHODOLOGY & APPENDIX
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% --- PAGE 2 HEADER ---
\noindent
\begin{{minipage}}[c]{{0.68\textwidth}}
    {{\Large \bfseries \textcolor{{primary}}{{Risk Disclosures, Legal Notice \& Quantitative Appendix}}}}\\[2pt]
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
\vspace{{0.4em}}

% --- PART I (TOP OF PAGE 2): CAPITAL INTRODUCTION & RISK DISCLAIMER ---
\begin{{tcolorbox}}[colback=white, colframe=accent, title=\textbf{{\small\strut Important Legal Disclaimer, Risk Disclosures \& Capital Introduction Notice}}, fonttitle=\sffamily\bfseries\small, arc=5pt, boxrule=0.9pt, toptitle=4.5pt, bottomtitle=4.5pt, left=8pt, right=8pt, top=4.5pt, bottom=4.5pt, colbacktitle=accent]
\scriptsize
\textcolor{{primary}}{{
\textbf{{1. Role of Ath\'en\'ee Investment — Capital Introduction Services Only (No Investment Advice):}}\\[1.5pt]
This document has been prepared by \textbf{{Ath\'en\'ee Investment}} solely for informational and discussion purposes as part of its institutional \textbf{{Capital Introduction and Third-Party Marketing}} activities. \textbf{{This document does not constitute investment advice, financial advisory services, a personal recommendation, or an offer to sell or a solicitation of an offer to buy}} any shares, units, or interests in any investment fund or financial instrument. Prospective investors must conduct their own independent due diligence and consult their own professional legal, regulatory, tax, and financial advisors before making any investment decision.\\[4.5pt]
\textbf{{2. No Warranty of Data Accuracy or Completeness (Third-Party Manager Data):}}\\[1.5pt]
All historical performance figures, return series, and strategy descriptions presented herein are derived from information provided directly by the respective third-party hedge fund managers or external data providers. While Ath\'en\'ee Investment has compiled and analyzed these quantitative metrics in good faith, \textbf{{Ath\'en\'ee Investment has not independently audited or verified the underlying data and cannot guarantee—and makes no representation or warranty, express or implied, regarding—the accuracy, completeness, reliability, or timeliness}} of any information contained in this document. Any errors, omissions, or subsequent restatements by the underlying fund manager are the sole responsibility of such manager.\\[4.5pt]
\textbf{{3. Key Risk Factors of Alternative \& Hedge Fund Strategies:}}\\[1.5pt]
Investing in alternative investment funds and hedge funds involves a \textbf{{high degree of risk}} and is suitable only for sophisticated investors capable of bearing the loss of their entire investment. Material risks include, without limitation:
\begin{{itemize}}[leftmargin=1.3em, itemsep=1pt, topsep=1pt]
    \item \textbf{{Market, Leverage \& Derivative Risk:}} Underlying funds may employ substantial leverage, short-selling, options, futures, swaps, and other derivative instruments, which can amplify both gains and losses and cause rapid capital erosion during extreme market dislocations.
    \item \textbf{{Illiquidity \& Lock-Up Risk:}} Hedge fund interests are typically not listed on any regulated exchange and are subject to redemption gates, notice periods, lock-ups, and side-pocket arrangements.
    \item \textbf{{Model, Regime Shift \& Tail-Correlation Risk:}} Quantitative and systematic strategies rely on mathematical models and historical statistical relationships (such as low equity beta or negative downside capture) that may break down or experience sudden correlation spikes during systemic liquidity crises.
    \item \textbf{{Operational, Counterparty \& Valuation Risk:}} Strategies trading in over-the-counter (OTC) derivatives, digital assets, distressed debt, or emerging markets face heightened counterparty default, custody, regulatory, and mark-to-model valuation risks.
\end{{itemize}}
\vspace{{2.5pt}}
\textbf{{4. Past Performance \& Quantitative Limitations:}}\\[1.5pt]
\textbf{{Past performance is not indicative of, nor a guarantee of, future results.}} The value of investments and the income derived from them may go down as well as up. Simulated, bootstrap, or regression-based indicators (including Alpha, Beta, Sharpe Ratio, Sortino Ratio, and Capture Ratios) are backward-looking statistical estimates and do not represent a promise or forecast of future risk-adjusted returns.\\[4.5pt]
\textbf{{5. Qualified Investors Only \& Confidentiality:}}\\[1.5pt]
This document is strictly confidential and is directed exclusively at \textbf{{Institutional, Professional, and Qualified Investors}} (including Qualified Investors within the meaning of the Swiss Collective Investment Schemes Act (CISA) and Financial Services Act (FinSA)). It may not be copied, reproduced, distributed, or disclosed to any third party, nor distributed in any jurisdiction where such distribution would be unlawful.
}}
\end{{tcolorbox}}

\vspace{{0.45em}}

% --- PART II: EXTENDED SINGLE-FUND QUANTITATIVE DIAGNOSTICS ---
\begin{{tcolorbox}}[colback=white, colframe=primary, title=\textbf{{\small\strut Appendix A: Extended Statistical, Bootstrap \& Factor Diagnostics}}, fonttitle=\sffamily\bfseries\small, arc=5pt, boxrule=0.8pt, toptitle=4pt, bottomtitle=4pt, left=6pt, right=6pt, top=3.5pt, bottom=3.5pt, colbacktitle=primary]
\renewcommand{{\arraystretch}}{{1.22}}
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

% --- PART III: METHODOLOGY DEFINITIONS ---
\begin{{tcolorbox}}[colback=cardbg, colframe=cardborder, title=\textbf{{\small\strut Appendix B: Quantitative Framework \& Indicator Definitions}}, fonttitle=\sffamily\bfseries\small\color{{primary}}, arc=5pt, boxrule=0.8pt, toptitle=3.5pt, bottomtitle=3.5pt, left=6pt, right=6pt, top=3.5pt, bottom=3.5pt, colbacktitle=cardborder]
\scriptsize
\begin{{itemize}}[leftmargin=1.2em, itemsep=1.2pt, topsep=1pt]
    \item \textbf{{CAGR \& Annualized Volatility:}} Compound Annual Growth Rate is computed geometrically as $\text{{CAGR}} = \left(\prod_{{t=1}}^T (1 + r_t)\right)^{{12/T}} - 1$. Annualized Volatility is sample standard deviation scaled by $\sqrt{{12}}$: $\sigma_{{\text{{ann}}}} = \hat{{\sigma}}_m \sqrt{{12}}$. Proxy Sharpe Ratio assumes $r_f = 0\%$ ($\bar{{r}}_{{\text{{ann}}}} / \sigma_{{\text{{ann}}}}$).
    \item \textbf{{Maximum Drawdown (MDD) \& Calmar Ratio:}} Maximum peak-to-trough decline of cumulative compounded wealth $W_t = \prod_{{s \le t}}(1+r_s)$, defined as $\text{{MDD}} = \min_t \left((W_t - \max_{{s \le t}} W_s) / \max_{{s \le t}} W_s\right)$. Calmar Ratio is $\text{{CAGR}} / |\text{{MDD}}|$.
    \item \textbf{{OLS Alpha ($\alpha$), Beta ($\beta$) \& Capture Ratios:}} Estimated via Ordinary Least Squares $r_{{\text{{fund}},t}} = \alpha_m + \beta r_{{\text{{SPX}},t}} + \varepsilon_t$, where $\alpha_{{\text{{ann}}}} = 12 \times \alpha_m$. Upside (Downside) Capture measures the ratio of the fund's mean return to the S\&P 500's mean return during positive (negative) S\&P 500 months.
    \item \textbf{{Tail Correlations \& Moving Block Bootstrap:}} Tail correlations evaluate linear ($r$) and rank ($\rho$) co-movement during S\&P 500 drawdowns below the 25th percentile ($Q_1$) and 10th percentile ($D_1$). Moving Block Bootstrap ($B=3$ months) preserves local serial dependencies when constructing 95\% confidence intervals.
\end{{itemize}}
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
# Step 6: CSV Writers & Pipeline Runners (Single & Batch)
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
    fund_meta: Optional[Dict[str, str]] = None,
    compile_pdf: bool = True,
    anonymize: bool = True,
    save_csv_files: bool = False,
    keep_tex: bool = False,
) -> Dict[str, Any]:
    """
    Run the complete pipeline for a single fund CSV:
      1. Load returns from `data/hf_returns/<fund_csv_name>.csv` and align with S&P 500, WTI, BTC
      2. Compute all `single_fund_analysis` metrics
      3. Build the Year x Month + Yearly Return Matrix
      4. Load fund terms / return basis from `third_party_marketing/fund_database.csv` (plus any overrides in `fund_meta`)
      5. Apply deterministic readable anonymization (when `anonymize=True`) so no IP is leaked
      6. Generate the modern LaTeX document (Page 1 Tear Sheet + Page 2 Legal Disclaimer & Appendix)
      7. Compile to PDF using `pdflatex` (if compile_pdf=True) and clean up temporary .tex/logo files
    """
    stem = fund_csv_name.replace(".csv", "").strip()
    out_dir = Path(output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    # Ensure logo is present in output directory during compilation so pdflatex finds it cleanly
    target_logo = out_dir / "athenee_logo.png"
    logo_was_created = False
    if not target_logo.exists():
        if LOGO_PATH.exists():
            shutil.copy(LOGO_PATH, target_logo)
            logo_was_created = True
        else:
            fallback_logo = PROJECT_ROOT / "report" / "educational" / "educational_easier" / "athenee_logo.png"
            if fallback_logo.exists():
                shutil.copy(fallback_logo, LOGO_PATH)
                shutil.copy(LOGO_PATH, target_logo)
                logo_was_created = True

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
    anon_id = get_anonymized_fund_identity(stem)
    metrics = compute_single_fund_metrics(records, anon_id["anon_code"] if anonymize else stem)
    metrics["anonymized_code"] = anon_id["anon_code"]
    metrics["anonymized_name"] = anon_id["anon_name"]

    # 3. Build Monthly Return Matrix
    monthly_matrix = build_monthly_return_matrix(records)

    file_prefix = anon_id["anon_slug"] if anonymize else stem

    # Optional CSV exports of metrics and monthly return matrix
    metrics_csv_path = out_dir / f"{file_prefix}_metrics.csv"
    matrix_csv_path = out_dir / f"{file_prefix}_return_matrix.csv"
    if save_csv_files:
        _write_dict_csv(metrics_csv_path, [metrics])
        _write_return_matrix_csv(matrix_csv_path, monthly_matrix)

    # 4. Generate LaTeX file (automatically pulls metadata & terms from fund_database.csv)
    latex_code = generate_latex_tearsheet(
        fund_csv_name=stem,
        records=records,
        metrics=metrics,
        monthly_matrix=monthly_matrix,
        logo_rel_path="athenee_logo.png",
        custom_title=custom_title,
        custom_subtitle=custom_subtitle,
        fund_meta=fund_meta,
        anonymize=anonymize,
    )
    tex_path = out_dir / f"{file_prefix}_tearsheet.tex"
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(latex_code)

    pdf_path = None
    if compile_pdf:
        pdf_path = compile_tex_to_pdf(tex_path)
        if pdf_path and pdf_path.exists() and not keep_tex:
            if tex_path.exists():
                tex_path.unlink()
            if logo_was_created and target_logo.exists():
                target_logo.unlink()
    elif logo_was_created and not keep_tex and target_logo.exists():
        target_logo.unlink()

    db_meta = get_fund_metadata(stem, hf_returns_dir=Path(hf_returns_dir))
    if fund_meta:
        for k, v in fund_meta.items():
            if v is not None and str(v).strip() != "":
                db_meta[k] = str(v).strip()

    return {
        "fund": stem,
        "anon_id": anon_id,
        "anonymized": anonymize,
        "records": records,
        "metrics": metrics,
        "return_matrix": monthly_matrix,
        "db_meta": db_meta,
        "tex_path": str(tex_path) if tex_path.exists() else None,
        "pdf_path": str(pdf_path) if pdf_path else None,
        "metrics_csv_path": str(metrics_csv_path) if save_csv_files else None,
        "matrix_csv_path": str(matrix_csv_path) if save_csv_files else None,
    }


# ---------------------------------------------------------------------------
# Step 7: Institutional Multi-Sheet Excel Workbook Builder (.xlsx)
# ---------------------------------------------------------------------------
def _col_letter(col_idx_1based: int) -> str:
    """Convert 1-based column index (1 -> 'A', 27 -> 'AA') to Excel column letters."""
    res = ""
    n = col_idx_1based
    while n > 0:
        n, rem = divmod(n - 1, 26)
        res = chr(65 + rem) + res
    return res


def _col_letter_to_index(col_str: str) -> int:
    """Convert Excel column letters ('A' -> 1, 'AA' -> 27) to 1-based column index."""
    res = 0
    for ch in col_str.upper():
        if "A" <= ch <= "Z":
            res = res * 26 + (ord(ch) - 64)
    return res


def _sanitize_sheet_name(name: str, used_names: set) -> str:
    """Ensure Excel worksheet tab name is <= 31 chars, strips invalid chars, and is unique."""
    cleaned = "".join(c for c in name if c not in r"[]:*?/\\").strip()
    if not cleaned:
        cleaned = "Mandate"
    base = cleaned[:31].strip()
    candidate = base
    counter = 2
    while candidate.lower() in used_names:
        suffix = f" ({counter})"
        candidate = base[: 31 - len(suffix)].strip() + suffix
        counter += 1
    used_names.add(candidate.lower())
    return candidate


def _build_xlsx_styles_xml() -> str:
    """Return OpenXML xl/styles.xml with Athénée institutional colors, fonts, borders, and number formats."""
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <numFmts count="5">
    <numFmt numFmtId="164" formatCode="0.00%"/>
    <numFmt numFmtId="165" formatCode="+0.0%;-0.0%;0.0%"/>
    <numFmt numFmtId="166" formatCode="0.00"/>
    <numFmt numFmtId="167" formatCode="#,##0"/>
    <numFmt numFmtId="168" formatCode="$#,##0"/>
  </numFmts>
  <fonts count="7">
    <font><sz val="10"/><color rgb="FF0F172A"/><name val="Calibri"/></font>
    <font><b/><sz val="13"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font>
    <font><b/><sz val="10"/><color rgb="FFE2C799"/><name val="Calibri"/></font>
    <font><b/><sz val="10"/><color rgb="FFFFFFFF"/><name val="Calibri"/></font>
    <font><b/><sz val="10"/><color rgb="FF0F172A"/><name val="Calibri"/></font>
    <font><b/><sz val="9.5"/><color rgb="FF14532D"/><name val="Calibri"/></font>
    <font><b/><sz val="9.5"/><color rgb="FF7F1D1D"/><name val="Calibri"/></font>
  </fonts>
  <fills count="8">
    <fill><patternFill patternType="none"/></fill>
    <fill><patternFill patternType="gray125"/></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FF0F172A"/><bgColor indexed="64"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FF1A365D"/><bgColor indexed="64"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFF8FAFC"/><bgColor indexed="64"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFDCFCE7"/><bgColor indexed="64"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFFEE2E2"/><bgColor indexed="64"/></patternFill></fill>
    <fill><patternFill patternType="solid"><fgColor rgb="FFE2E8F0"/><bgColor indexed="64"/></patternFill></fill>
  </fills>
  <borders count="3">
    <border><left/><right/><top/><bottom/><diagonal/></border>
    <border>
      <left style="thin"><color rgb="FFCBD5E1"/></left>
      <right style="thin"><color rgb="FFCBD5E1"/></right>
      <top style="thin"><color rgb="FFCBD5E1"/></top>
      <bottom style="thin"><color rgb="FFCBD5E1"/></bottom>
      <diagonal/>
    </border>
    <border>
      <left style="thin"><color rgb="FF0F172A"/></left>
      <right style="thin"><color rgb="FF0F172A"/></right>
      <top style="medium"><color rgb="FF0F172A"/></top>
      <bottom style="medium"><color rgb="FFB08A57"/></bottom>
      <diagonal/>
    </border>
  </borders>
  <cellStyleXfs count="1">
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0"/>
  </cellStyleXfs>
  <cellXfs count="21">
    <!-- 0: Default -->
    <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
    <!-- 1: Banner Title (Deep Navy, Bold White 13pt) -->
    <xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyFont="1" applyFill="1" applyAlignment="1">
      <alignment vertical="center" indent="1"/>
    </xf>
    <!-- 2: Sub-Banner (Slate Navy, Bold Gold 10pt) -->
    <xf numFmtId="0" fontId="2" fillId="3" borderId="2" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">
      <alignment vertical="center" indent="1"/>
    </xf>
    <!-- 3: Section Header (Deep Navy, Bold White 10pt, Left) -->
    <xf numFmtId="0" fontId="3" fillId="2" borderId="2" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">
      <alignment horizontal="left" vertical="center" indent="1"/>
    </xf>
    <!-- 4: Table Header Centered (Slate Navy, Bold White, Single-Line Auto-Sized) -->
    <xf numFmtId="0" fontId="3" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">
      <alignment horizontal="center" vertical="center"/>
    </xf>
    <!-- 5: Table Header Left (Slate Navy, Bold White, Single-Line Auto-Sized) -->
    <xf numFmtId="0" fontId="3" fillId="3" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">
      <alignment horizontal="left" vertical="center"/>
    </xf>
    <!-- 6: Body Text Left (White) -->
    <xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyFont="1" applyBorder="1" applyAlignment="1">
      <alignment horizontal="left" vertical="center"/>
    </xf>
    <!-- 7: Body Text Left (Zebra Slate) -->
    <xf numFmtId="0" fontId="0" fillId="4" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">
      <alignment horizontal="left" vertical="center"/>
    </xf>
    <!-- 8: Body Text Center -->
    <xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyFont="1" applyBorder="1" applyAlignment="1">
      <alignment horizontal="center" vertical="center"/>
    </xf>
    <!-- 9: Bold Label Left (Light Slate) -->
    <xf numFmtId="0" fontId="4" fillId="4" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">
      <alignment horizontal="left" vertical="center"/>
    </xf>
    <!-- 10: Percentage 0.00% -->
    <xf numFmtId="164" fontId="0" fillId="0" borderId="1" xfId="0" applyNumberFormat="1" applyFont="1" applyBorder="1" applyAlignment="1">
      <alignment horizontal="right" vertical="center"/>
    </xf>
    <!-- 11: Percentage Bold 0.00% -->
    <xf numFmtId="164" fontId="4" fillId="4" borderId="1" xfId="0" applyNumberFormat="1" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">
      <alignment horizontal="right" vertical="center"/>
    </xf>
    <!-- 12: Matrix Positive Return (+0.0% Green Fill) -->
    <xf numFmtId="165" fontId="5" fillId="5" borderId="1" xfId="0" applyNumberFormat="1" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">
      <alignment horizontal="center" vertical="center"/>
    </xf>
    <!-- 13: Matrix Negative Return (-0.0% Red Fill) -->
    <xf numFmtId="165" fontId="6" fillId="6" borderId="1" xfId="0" applyNumberFormat="1" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">
      <alignment horizontal="center" vertical="center"/>
    </xf>
    <!-- 14: Float 0.00 -->
    <xf numFmtId="166" fontId="0" fillId="0" borderId="1" xfId="0" applyNumberFormat="1" applyFont="1" applyBorder="1" applyAlignment="1">
      <alignment horizontal="right" vertical="center"/>
    </xf>
    <!-- 15: Float Bold 0.00 -->
    <xf numFmtId="166" fontId="4" fillId="4" borderId="1" xfId="0" applyNumberFormat="1" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">
      <alignment horizontal="right" vertical="center"/>
    </xf>
    <!-- 16: Integer #,##0 Centered -->
    <xf numFmtId="167" fontId="0" fillId="0" borderId="1" xfId="0" applyNumberFormat="1" applyFont="1" applyBorder="1" applyAlignment="1">
      <alignment horizontal="center" vertical="center"/>
    </xf>
    <!-- 17: USD Currency $#,##0 Bold -->
    <xf numFmtId="168" fontId="4" fillId="4" borderId="1" xfId="0" applyNumberFormat="1" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">
      <alignment horizontal="right" vertical="center"/>
    </xf>
    <!-- 18: Disclaimer Section Heading -->
    <xf numFmtId="0" fontId="4" fillId="7" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">
      <alignment horizontal="left" vertical="center" indent="1"/>
    </xf>
    <!-- 19: Disclaimer Wrapped Paragraph -->
    <xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyFont="1" applyBorder="1" applyAlignment="1">
      <alignment horizontal="left" vertical="top" wrapText="1"/>
    </xf>
    <!-- 20: Bold Center (Year / Summary) -->
    <xf numFmtId="0" fontId="4" fillId="4" borderId="1" xfId="0" applyFont="1" applyFill="1" applyBorder="1" applyAlignment="1">
      <alignment horizontal="center" vertical="center"/>
    </xf>
  </cellXfs>
  <cellStyles count="1">
    <cellStyle name="Normal" xfId="0" builtinId="0"/>
  </cellStyles>
</styleSheet>"""


def _estimate_formatted_cell_length(val: Any, style_id: int) -> int:
    """Estimate visible character width of a cell value given its Excel style_id for auto-adjusting columns."""
    if val is None or (isinstance(val, float) and (math.isnan(val) or math.isinf(val))):
        return 0
    if style_id in (10, 11, 12, 13) and isinstance(val, (int, float)):
        return len(f"{val * 100:+.2f}%")
    if style_id in (14, 15) and isinstance(val, (int, float)):
        return len(f"{val:+.2f}")
    if style_id == 16 and isinstance(val, (int, float)):
        return len(f"{int(val):,}")
    if style_id == 17 and isinstance(val, (int, float)):
        return len(f"${val:,.0f}")
    s = str(val)
    if "\n" in s:
        return max(len(line) for line in s.splitlines())
    return len(s)


def _render_worksheet_xml(
    rows_data: List[Tuple[int, Optional[float], List[Tuple[int, Any, int]]]],
    col_widths: List[Tuple[int, int, float]],
    merges: Optional[List[str]] = None,
    freeze_row: Optional[int] = None,
    auto_fit_columns: bool = True,
) -> str:
    """
    Render an OpenXML worksheet XML string with:
      - `showGridLines="0"` on EVERY worksheet so there is NO grid background
      - Automatic column width calculation (`bestFit="1" customWidth="1"`) across all non-merged cells
        so every header and value fits without manual clicking
    """
    lines = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">',
    ]
    if freeze_row and freeze_row > 0:
        top_left = f"A{freeze_row + 1}"
        lines.append(
            f'  <sheetViews><sheetView workbookViewId="0" showGridLines="0">'
            f'<pane ySplit="{freeze_row}" topLeftCell="{top_left}" activePane="bottomLeft" state="frozen"/>'
            f'</sheetView></sheetViews>'
        )
    else:
        lines.append('  <sheetViews><sheetView workbookViewId="0" showGridLines="0"/></sheetViews>')

    # Build set of (row, col) coordinates that belong to multi-column horizontal merges so they don't bloat individual columns
    merged_coords: set = set()
    if merges:
        for m_ref in merges:
            if ":" in m_ref:
                left_ref, right_ref = m_ref.split(":", 1)
                c1_str = "".join(ch for ch in left_ref if ch.isalpha())
                r1_str = "".join(ch for ch in left_ref if ch.isdigit())
                c2_str = "".join(ch for ch in right_ref if ch.isalpha())
                r2_str = "".join(ch for ch in right_ref if ch.isdigit())
                c1, r1 = _col_letter_to_index(c1_str), int(r1_str)
                c2, r2 = _col_letter_to_index(c2_str), int(r2_str)
                if c2 > c1:
                    for rr in range(r1, r2 + 1):
                        for cc in range(c1, c2 + 1):
                            merged_coords.add((rr, cc))

    # Map baseline widths per column index
    computed_widths: Dict[int, float] = {}
    for cmin, cmax, w in col_widths:
        for cc in range(cmin, cmax + 1):
            computed_widths[cc] = max(computed_widths.get(cc, 0.0), float(w))

    if auto_fit_columns:
        for r_idx, _, cells in rows_data:
            for c_idx, val, style_id in cells:
                if (r_idx, c_idx) in merged_coords or style_id in (1, 2, 3, 18, 19):
                    continue
                char_len = _estimate_formatted_cell_length(val, style_id)
                if char_len > 0:
                    # Bold headers and bold labels get slightly wider multiplier + generous padding
                    mult = 1.24 if style_id in (4, 5, 9, 11, 15, 17, 20) else 1.15
                    pad = 5.0 if style_id in (4, 5) else 4.0
                    needed_w = char_len * mult + pad
                    computed_widths[c_idx] = max(computed_widths.get(c_idx, 10.0), needed_w)

    if computed_widths:
        lines.append("  <cols>")
        for cc in sorted(computed_widths.keys()):
            w = computed_widths[cc]
            lines.append(f'    <col min="{cc}" max="{cc}" width="{w:.2f}" bestFit="1" customWidth="1"/>')
        lines.append("  </cols>")

    lines.append("  <sheetData>")
    for r_idx, r_ht, cells in rows_data:
        eff_ht = r_ht if r_ht is not None else 20.0
        ht_attr = f' ht="{eff_ht:.1f}" customHeight="1"'
        lines.append(f'    <row r="{r_idx}"{ht_attr}>')
        for c_idx, val, style_id in sorted(cells, key=lambda x: x[0]):
            ref = f"{_col_letter(c_idx)}{r_idx}"
            if val is None or (isinstance(val, float) and (math.isnan(val) or math.isinf(val))):
                lines.append(f'      <c r="{ref}" s="{style_id}"/>')
            elif isinstance(val, (int, float)) and not isinstance(val, bool):
                lines.append(f'      <c r="{ref}" s="{style_id}"><v>{val}</v></c>')
            else:
                s_val = xml_escape(str(val))
                lines.append(f'      <c r="{ref}" t="inlineStr" s="{style_id}"><is><t xml:space="preserve">{s_val}</t></is></c>')
        lines.append("    </row>")
    lines.append("  </sheetData>")

    if merges:
        lines.append(f'  <mergeCells count="{len(merges)}">')
        for m_ref in merges:
            lines.append(f'    <mergeCell ref="{m_ref}"/>')
        lines.append("  </mergeCells>")

    lines.append("</worksheet>")
    return "\n".join(lines)


def _build_disclaimer_sheet_xml(n_funds: int) -> str:
    """Build Sheet 1: Third-Party Marketing (TPM) Proposition, Conflicts of Interest & Legal Disclaimer."""
    gen_date = datetime.now().strftime("%Y-%m-%d %H:%M")
    sections = [
        (
            "1. NATURE OF PROPOSITION — THIRD-PARTY MARKETING (TPM) & CAPITAL INTRODUCTION ONLY (NO INVESTMENT ADVICE)",
            "This workbook and the accompanying quantitative tear sheets have been prepared by Athénée Investment (Quai des Bergues 23, 1201 Geneva, Switzerland) strictly as a Third-Party Marketing (TPM) and institutional Capital Introduction proposition. Nothing contained in this workbook constitutes investment advice, financial advisory services, portfolio management, legal, tax, or regulatory advice, a personal recommendation, or an offer to sell or a solicitation of an offer to buy any shares, units, or interests in any investment fund or financial instrument. Prospective investors must conduct their own independent due diligence and consult their own professional legal, tax, regulatory, and financial advisors prior to making any investment decision.",
        ),
        (
            "2. DISCLOSURE OF POTENTIAL CONFLICTS OF INTEREST & REMUNERATION STRUCTURE",
            "Athénée Investment acts as an independent third-party marketer and capital introduction intermediary on behalf of certain alternative investment fund managers presented in this workbook. In connection with these Capital Introduction and Third-Party Marketing services, Athénée Investment may receive retainer fees, placement fees, marketing fees, or ongoing management/performance fee-sharing arrangements from the underlying fund managers or their affiliates. Consequently, a potential conflict of interest exists, as Athénée Investment may have a financial incentive to introduce prospective investors to the funds featured herein rather than to other investment opportunities.",
        ),
        (
            "3. ANONYMIZATION OF MANDATE NAMES & INTELLECTUAL PROPERTY PROTECTION",
            "To protect proprietary manager sourcing and institutional intellectual property during the initial evaluation stage, all underlying hedge fund mandates in this workbook and in the accompanying tear sheets are identified by deterministic Athénée Mandate Code Names (e.g., 'Schedar Bastion (ATH-514)'). Full manager identity, audited offering memoranda, and data room access are provided upon execution of mutual confidentiality and non-circumvention agreements with Athénée Investment.",
        ),
        (
            "4. NO WARRANTY OF DATA ACCURACY OR COMPLETENESS (THIRD-PARTY MANAGER DATA)",
            "All historical monthly return series, strategy classifications, assets under management (AUM), fee structures, liquidity terms, minimum investment thresholds, and vehicle descriptions contained in this workbook are derived from information provided directly by the respective third-party hedge fund managers or external data providers. While Athénée Investment has compiled and computed the quantitative metrics herein in good faith using its standardized single-fund analysis methodology, Athénée Investment has not independently audited or verified the underlying track records and makes no representation or warranty, express or implied, regarding the accuracy, completeness, reliability, or timeliness of any information presented.",
        ),
        (
            "5. KEY RISK FACTORS OF ALTERNATIVE & HEDGE FUND STRATEGIES",
            "Investing in alternative investment funds, commingled hedge funds, and separately managed accounts (SMAs) involves a high degree of risk and is suitable only for sophisticated institutional and qualified investors capable of bearing the loss of their entire investment. Material risks include: (i) Market, Leverage & Derivative Risk (substantial leverage, short-selling, futures, options, swaps, and OTC derivatives that can amplify losses); (ii) Illiquidity & Lock-Up Risk (quarterly or restricted redemption schedules, notice periods, gates, lock-ups, and side-pockets); (iii) Model, Regime Shift & Tail-Correlation Risk (historical low beta or crisis alpha relationships may break down during systemic market dislocations); and (iv) Operational, Counterparty & Custody Risk.",
        ),
        (
            "6. PAST PERFORMANCE, QUANTITATIVE LIMITATIONS & QUALIFIED INVESTORS NOTICE (SWISS CISA / FINSA)",
            f"PAST PERFORMANCE IS NOT INDICATIVE OF, NOR A GUARANTEE OF, FUTURE RESULTS. All statistical indicators computed in this workbook—including CAGR, Annualized Volatility, Sharpe Ratio (rf = 0%), Sortino Ratio, Maximum Drawdown (MDD), Calmar Ratio, OLS Alpha & Beta against the S&P 500 Total Return Index, Moving Block Bootstrap Confidence Intervals (B = 3 months), Upside/Downside Capture Ratios, and Tail Correlations—are backward-looking empirical estimates. This document is strictly confidential and is directed exclusively at Institutional, Professional, and Qualified Investors (within the meaning of Swiss CISA / FinSA).\n\nWorkbook Generated: {gen_date}  |  Total Mandates Included: {n_funds}  |  Contact: arthur.dhonneur@athenee-investment.com",
        ),
    ]

    rows_data = [
        (1, 34.0, [(1, "ATHÉNÉE INVESTMENT — THIRD-PARTY MARKETING (TPM) & CAPITAL INTRODUCTION PROPOSITION", 1)] + [(c, None, 1) for c in range(2, 9)]),
        (2, 24.0, [(1, "IMPORTANT LEGAL DISCLAIMER, CONFLICTS OF INTEREST DISCLOSURE & RISK NOTICE  |  Quai des Bergues 23, 1201 Geneva, Switzerland", 2)] + [(c, None, 2) for c in range(2, 9)]),
        (3, 12.0, []),
    ]
    merges = ["A1:H1", "A2:H2"]

    curr_row = 4
    # Total width across columns A..H is 8 * 22 = 176 chars; dynamically size each paragraph row height
    for title_txt, body_txt in sections:
        rows_data.append(
            (curr_row, 24.0, [(1, title_txt, 18)] + [(c, None, 18) for c in range(2, 9)])
        )
        merges.append(f"A{curr_row}:H{curr_row}")
        curr_row += 1

        est_lines = sum(max(1, math.ceil(len(p) / 130.0)) for p in body_txt.split("\n"))
        body_ht = max(54.0, est_lines * 16.5 + 14.0)
        rows_data.append(
            (curr_row, body_ht, [(1, body_txt, 19)] + [(c, None, 19) for c in range(2, 9)])
        )
        merges.append(f"A{curr_row}:H{curr_row}")
        curr_row += 1

        rows_data.append((curr_row, 10.0, []))
        curr_row += 1

    col_widths = [(1, 8, 22.0)]
    return _render_worksheet_xml(rows_data, col_widths, merges=merges, freeze_row=2, auto_fit_columns=False)


def _build_summary_sheet_xml(fund_results: List[Dict[str, Any]], anonymize: bool = True) -> str:
    """Build Sheet 2: Comprehensive Executive Summary Table across all analyzed funds (anonymized by default)."""
    headers = [
        "#",
        "Mandate Code" if anonymize else "Fund CSV ID",
        "Mandate Name" if anonymize else "Fund Name",
        "Strategy / Mandate Classification",
        "Vehicle",
        "Return Basis",
        "Start Date",
        "End Date",
        "Months",
        "Years",
        "CAGR",
        "S&P 500 CAGR",
        "Ann. Mean",
        "Ann. Volatility",
        "S&P 500 Vol",
        "Sharpe (rf=0%)",
        "S&P 500 Sharpe",
        "Sortino Ratio",
        "Max Drawdown",
        "S&P 500 MDD",
        "Calmar Ratio",
        "Cumul. Return",
        "Growth of $1M USD",
        "Alpha (Ann.)",
        "Alpha t-stat",
        "Beta (SPX)",
        "Beta t-stat",
        "Corr. to S&P 500",
        "Spearman Corr.",
        "Worst-Case Corr.",
        "Positive Months (%)",
        "Crisis Hit Rate (SPX<0)",
        "Upside Capture",
        "Downside Capture",
        "Worst 20% SPX (Fund)",
        "Worst 20% SPX (SPX)",
        "Best Month",
        "Worst Month",
        "Mgmt Fee",
        "Perf Fee",
        "Liquidity Terms",
        "Lock-Up",
        "Min. Investment",
        "Current AUM",
        "Domicile",
    ]
    ncols = len(headers)
    last_col_ltr = _col_letter(ncols)

    rows_data = [
        (
            1,
            32.0,
            [(1, "ATHÉNÉE INVESTMENT — EXECUTIVE SUMMARY OF ANALYZED MANDATES (VS. S&P 500 TOTAL RETURN)", 1)]
            + [(c, None, 1) for c in range(2, ncols + 1)],
        ),
        (
            2,
            22.0,
            [(1, f"Comparative Quantitative Performance, Risk, Alpha/Beta, Tail Diagnostics & Commercial Overview ({len(fund_results)} Mandates)", 2)]
            + [(c, None, 2) for c in range(2, ncols + 1)],
        ),
        (3, 10.0, []),
        (
            4,
            26.0,
            [(c_idx, h_text, 5 if c_idx in (2, 3, 4) else 4) for c_idx, h_text in enumerate(headers, 1)],
        ),
    ]
    merges = [f"A1:{last_col_ltr}1", f"A2:{last_col_ltr}2"]

    for idx, res in enumerate(fund_results, 1):
        r_num = 4 + idx
        stem = res["fund"]
        m = res["metrics"]
        meta = res.get("db_meta") or get_fund_metadata(stem)
        anon_id = res.get("anon_id") or get_anonymized_fund_identity(stem)
        real_disp = meta.get("display_name") or format_fund_title(stem)
        raw_sub = meta.get("strategy_subtitle") or format_fund_subtitle(stem)

        if anonymize:
            code_col_val = anon_id["anon_code"]
            name_col_val = anon_id["anon_name"]
            sub_col_val = scrub_fund_name_from_text(raw_sub, stem, real_disp)
        else:
            code_col_val = stem
            name_col_val = real_disp
            sub_col_val = raw_sub

        final_1m_usd = 1_000_000.0 * (1.0 + (m["cum_ret"] if not _isna(m["cum_ret"]) else 0.0))

        row_vals = [
            (1, idx, 16),
            (2, code_col_val, 8),
            (3, name_col_val, 9),
            (4, sub_col_val, 6),
            (5, meta.get("investment_vehicle", ""), 8),
            (6, meta.get("return_basis", ""), 8),
            (7, m["start_date"], 8),
            (8, m["end_date"], 8),
            (9, int(m["n_months"]), 16),
            (10, float(m["years_elapsed"]), 14),
            (11, float(m["cagr"]), 11),
            (12, float(m["sp_cagr"]), 10),
            (13, float(m["ann_mean"]), 10),
            (14, float(m["ann_vol"]), 10),
            (15, float(m["sp_ann_vol"]), 10),
            (16, float(m["sharpe"]), 15),
            (17, float(m["sp_sharpe"]), 14),
            (18, float(m["sortino"]), 14),
            (19, float(m["mdd"]), 11),
            (20, float(m["sp_mdd"]), 10),
            (21, float(m["calmar"]), 14),
            (22, float(m["cum_ret"]), 10),
            (23, float(final_1m_usd), 17),
            (24, float(m["alpha"]), 11),
            (25, float(m["alpha_tstat"]), 14),
            (26, float(m["beta"]), 14),
            (27, float(m["beta_tstat"]), 14),
            (28, float(m["pearson_corr"]), 15),
            (29, float(m["spearman_corr"]), 14),
            (30, float(m["worst_case_corr"]), 14),
            (31, float(m["fund_pos_rate"]), 10),
            (32, float(m["crisis_hit_rate"]), 10),
            (33, float(m["up_capture"]), 14),
            (34, float(m["down_capture"]), 14),
            (35, float(m["worst20_fund_mean"]), 10),
            (36, float(m["worst20_sp500_mean"]), 10),
            (37, float(m["best_month"]), 10),
            (38, float(m["worst_month"]), 10),
            (39, meta.get("management_fee", ""), 8),
            (40, meta.get("performance_fee", ""), 8),
            (41, meta.get("liquidity_terms", ""), 8),
            (42, meta.get("lockup", ""), 8),
            (43, meta.get("minimum_investment", ""), 8),
            (44, meta.get("current_aum", ""), 8),
            (45, meta.get("domicile_structure", ""), 8),
        ]
        rows_data.append((r_num, 21.0, row_vals))

    # Add Equal-Weighted Average row at the bottom if >= 2 funds
    if len(fund_results) >= 2:
        avg_row_num = 5 + len(fund_results)
        rows_data.append((avg_row_num, 8.0, []))
        avg_row_num += 1

        def _avg_metric(key: str) -> float:
            vals = [
                float(r["metrics"][key])
                for r in fund_results
                if key in r["metrics"] and not _isna(r["metrics"][key])
            ]
            return sum(vals) / len(vals) if vals else float("nan")

        avg_1m = sum(
            1_000_000.0 * (1.0 + (r["metrics"]["cum_ret"] if not _isna(r["metrics"]["cum_ret"]) else 0.0))
            for r in fund_results
        ) / len(fund_results)

        avg_cells = [
            (1, None, 9),
            (2, "AVERAGE", 20),
            (3, f"Equal-Weighted Average ({len(fund_results)} Mandates)", 9),
            (4, "", 9),
            (5, "", 9),
            (6, "", 9),
            (7, "", 9),
            (8, "", 9),
            (9, round(_avg_metric("n_months")), 16),
            (10, _avg_metric("years_elapsed"), 15),
            (11, _avg_metric("cagr"), 11),
            (12, _avg_metric("sp_cagr"), 11),
            (13, _avg_metric("ann_mean"), 11),
            (14, _avg_metric("ann_vol"), 11),
            (15, _avg_metric("sp_ann_vol"), 11),
            (16, _avg_metric("sharpe"), 15),
            (17, _avg_metric("sp_sharpe"), 15),
            (18, _avg_metric("sortino"), 15),
            (19, _avg_metric("mdd"), 11),
            (20, _avg_metric("sp_mdd"), 11),
            (21, _avg_metric("calmar"), 15),
            (22, _avg_metric("cum_ret"), 11),
            (23, avg_1m, 17),
            (24, _avg_metric("alpha"), 11),
            (25, _avg_metric("alpha_tstat"), 15),
            (26, _avg_metric("beta"), 15),
            (27, _avg_metric("beta_tstat"), 15),
            (28, _avg_metric("pearson_corr"), 15),
            (29, _avg_metric("spearman_corr"), 15),
            (30, _avg_metric("worst_case_corr"), 15),
            (31, _avg_metric("fund_pos_rate"), 11),
            (32, _avg_metric("crisis_hit_rate"), 11),
            (33, _avg_metric("up_capture"), 15),
            (34, _avg_metric("down_capture"), 15),
            (35, _avg_metric("worst20_fund_mean"), 11),
            (36, _avg_metric("worst20_sp500_mean"), 11),
            (37, _avg_metric("best_month"), 11),
            (38, _avg_metric("worst_month"), 11),
        ] + [(c, "", 9) for c in range(39, ncols + 1)]
        rows_data.append((avg_row_num, 23.0, avg_cells))

    col_widths = [(1, 1, 6.0)]
    return _render_worksheet_xml(rows_data, col_widths, merges=merges, freeze_row=4, auto_fit_columns=True)


def _build_single_fund_sheet_xml(res: Dict[str, Any], anonymize: bool = True) -> str:
    """Build an individual Fund Worksheet containing Terms, Full Quantitative Indicators, Return Matrix, and $1M Track Record."""
    stem = res["fund"]
    m = res["metrics"]
    matrix = res["return_matrix"]
    records = res.get("records") or []
    meta = res.get("db_meta") or get_fund_metadata(stem)
    anon_id = res.get("anon_id") or get_anonymized_fund_identity(stem)

    real_disp = meta.get("display_name") or format_fund_title(stem)
    raw_sub = meta.get("strategy_subtitle") or format_fund_subtitle(stem)
    if anonymize:
        disp_title = f"{anon_id['anon_name']} ({anon_id['anon_code']})"
        disp_sub = scrub_fund_name_from_text(raw_sub, stem, real_disp)
    else:
        disp_title = real_disp
        disp_sub = raw_sub

    period_desc = f"Track Record: {m['start_date']} to {m['end_date']} ({m['n_months']} Months / {m['years_elapsed']:.1f} Years)  |  Benchmark: S&P 500 Total Return"

    rows_data = [
        (1, 32.0, [(1, f"{disp_title} — {disp_sub}", 1)] + [(c, None, 1) for c in range(2, 15)]),
        (2, 22.0, [(1, period_desc, 2)] + [(c, None, 2) for c in range(2, 15)]),
        (3, 10.0, []),
    ]
    merges = ["A1:N1", "A2:N2"]

    # --- Section 1: Fund Terms & Commercial Overview (Rows 4-6) ---
    rows_data.append((4, 24.0, [(1, "FUND TERMS & COMMERCIAL OVERVIEW", 3)] + [(c, None, 3) for c in range(2, 15)]))
    merges.append("A4:N4")

    rows_data.append(
        (
            5,
            21.0,
            [
                (1, "Investment Vehicle", 9),
                (2, meta.get("investment_vehicle", ""), 8),
                (3, "Return Basis", 9),
                (4, meta.get("return_basis", ""), 8),
                (5, "Management Fee", 9),
                (6, meta.get("management_fee", ""), 8),
                (7, "Performance Fee", 9),
                (8, meta.get("performance_fee", ""), 8),
            ],
        )
    )
    rows_data.append(
        (
            6,
            21.0,
            [
                (1, "Liquidity Terms", 9),
                (2, meta.get("liquidity_terms", ""), 8),
                (3, "Lock-Up Period", 9),
                (4, meta.get("lockup", ""), 8),
                (5, "Min. Investment", 9),
                (6, meta.get("minimum_investment", ""), 8),
                (7, "Current AUM / Domicile", 9),
                (
                    8,
                    f"{meta.get('current_aum', '')} ({meta.get('domicile_structure', '')})"
                    if meta.get("domicile_structure")
                    else meta.get("current_aum", ""),
                    8,
                ),
            ],
        )
    )
    rows_data.append((7, 10.0, []))

    # --- Section 2: Side-by-Side Quantitative Indicators (Rows 8-22) ---
    rows_data.append(
        (
            8,
            24.0,
            [(1, "PERFORMANCE, RISK & HIT RATE INDICATORS", 3), (2, None, 3), (3, None, 3)]
            + [(5, "ALPHA, BETA, CORRELATION & TAIL ANALYSIS (VS. S&P 500)", 3), (6, None, 3), (7, None, 3), (8, None, 3)],
        )
    )
    merges.extend(["A8:C8", "E8:H8"])

    rows_data.append(
        (
            9,
            22.0,
            [
                (1, "Indicator", 5),
                (2, "Mandate" if anonymize else "Fund", 4),
                (3, "S&P 500", 4),
                (5, "Quantitative Metric", 5),
                (6, "Estimate", 4),
                (7, "t-stat / Diagnostic", 4),
                (8, "95% CI / Specification", 4),
            ],
        )
    )

    left_rows = [
        ("CAGR (Annualized)", m["cagr"], m["sp_cagr"], 11, 10),
        ("Annualized Mean Return", m["ann_mean"], m["sp_ann_mean"], 10, 10),
        ("Annualized Volatility", m["ann_vol"], m["sp_ann_vol"], 10, 10),
        ("Proxy Sharpe Ratio (rf = 0%)", m["sharpe"], m["sp_sharpe"], 15, 14),
        ("Annualized Sortino Ratio", m["sortino"], m["sp_sortino"], 14, 14),
        ("Maximum Drawdown (MDD)", m["mdd"], m["sp_mdd"], 11, 10),
        ("Calmar Ratio (CAGR / |MDD|)", m["calmar"], m["sp_calmar"], 14, 14),
        ("Cumulative Total Return", m["cum_ret"], m["sp_cum_ret"], 10, 10),
        ("Final Value of $1,000,000 USD", 1_000_000.0 * (1.0 + m["cum_ret"]), 1_000_000.0 * (1.0 + m["sp_cum_ret"]), 17, 17),
        ("Best Monthly Return", m["best_month"], m["sp_best_month"], 10, 10),
        ("Worst Monthly Return", m["worst_month"], m["sp_worst_month"], 10, 10),
        ("Positive Months (Hit Rate)", m["fund_pos_rate"], m["sp500_pos_rate"], 10, 10),
        ("Crisis Hit Rate (Fund>0 | SPX<0)", m["crisis_hit_rate"], None, 11, 8),
    ]

    right_rows = [
        ("Annualized Alpha (α)", m["alpha"], m["alpha_tstat"], f"R² = {m['r_squared']*100:.1f}%" if not _isna(m["r_squared"]) else "", 11, 14),
        ("Market Beta (β SPX)", m["beta"], m["beta_tstat"], "OLS vs. S&P 500 TR", 15, 14),
        ("Pearson Correlation (r)", m["pearson_corr"], None, f"Blk CI: [{m['pearson_blk_ci_low']:.2f}, {m['pearson_blk_ci_high']:.2f}]" if not _isna(m["pearson_blk_ci_low"]) else "", 15, 8),
        ("Spearman Rank Correlation (ρ)", m["spearman_corr"], None, f"Blk CI: [{m['spearman_blk_ci_low']:.2f}, {m['spearman_blk_ci_high']:.2f}]" if not _isna(m["spearman_blk_ci_low"]) else "", 14, 8),
        ("Worst-Case Co-Dependence", m["worst_case_corr"], None, "97.5th Pct Block Bootstrap", 14, 8),
        ("Upside Capture Ratio", m["up_capture"], None, f"SPX > 0 (n={m['n_sp500_pos']})", 14, 8),
        ("Downside Capture Ratio", m["down_capture"], None, f"SPX < 0 (n={m['n_sp500_neg']})", 14, 8),
        ("Cond. Up-Market Alpha / Beta", m["up_alpha"], m["up_beta"], f"t(α) = {m['up_alpha_t']:.2f}" if not _isna(m["up_alpha_t"]) else "", 10, 14),
        ("Cond. Down-Market Alpha / Beta", m["down_alpha"], m["down_beta"], f"t(α) = {m['down_alpha_t']:.2f}" if not _isna(m["down_alpha_t"]) else "", 10, 14),
        ("Tail Corr. (SPX < Q1, Worst 25%)", m["q1_pearson"], m["q1_spearman"], f"n = {m['n_q1']} months", 14, 14),
        ("Tail Corr. (SPX < D1, Worst 10%)", m["d1_pearson"], m["d1_spearman"], f"n = {m['n_d1']} months", 14, 14),
        ("Worst 20% SPX Months Avg.", m["worst20_fund_mean"], m["worst20_sp500_mean"], "Mandate vs. S&P 500 Avg.", 11, 10),
        ("Ljung-Box Serial Corr. (p1 / p3)", m["lb_lag1_pval"], m["lb_lag3_pval"], "Pass (No Smoothing)" if (not _isna(m["lb_lag1_pval"]) and m["lb_lag1_pval"] >= 0.05 and m["lb_lag3_pval"] >= 0.05) else "Serial Corr.", 14, 14),
    ]

    for i in range(len(left_rows)):
        r_num = 10 + i
        l_lbl, l_f, l_sp, l_fs, l_sps = left_rows[i]
        r_lbl, r_est, r_diag, r_note, r_es, r_ds = right_rows[i]
        row_cells = [
            (1, l_lbl, 9 if i % 2 == 1 else 6),
            (2, l_f, l_fs),
            (3, l_sp, l_sps),
            (5, r_lbl, 9 if i % 2 == 1 else 6),
            (6, r_est, r_es),
            (7, r_diag, r_ds),
            (8, r_note, 7 if i % 2 == 1 else 6),
        ]
        rows_data.append((r_num, 20.5, row_cells))

    curr_row = 24
    rows_data.append((curr_row, 10.0, []))
    curr_row += 1

    # --- Section 3: Historical Monthly & Yearly Return Matrix (%) ---
    basis_lbl = meta.get("return_basis", "").strip()
    matrix_hdr_title = (
        f"HISTORICAL MONTHLY & YEARLY {basis_lbl.upper()} RETURN MATRIX (%)"
        if basis_lbl
        else "HISTORICAL MONTHLY & YEARLY RETURN MATRIX (%)"
    )
    rows_data.append((curr_row, 24.0, [(1, matrix_hdr_title, 3)] + [(c, None, 3) for c in range(2, 15)]))
    merges.append(f"A{curr_row}:N{curr_row}")
    curr_row += 1

    matrix_cols = ["Year"] + MONTH_ABBR + ["Yearly"]
    rows_data.append((curr_row, 22.0, [(c_i, col_name, 4) for c_i, col_name in enumerate(matrix_cols, 1)]))
    curr_row += 1

    for year in sorted(matrix.keys()):
        y_row = matrix[year]
        m_cells = [(1, int(year), 20)]
        for m_idx in range(1, 13):
            v = y_row[m_idx]
            if _isna(v):
                m_cells.append((m_idx + 1, "-", 8))
            else:
                st = 12 if v >= 0 else 13
                m_cells.append((m_idx + 1, float(v), st))
        vy = y_row["Yearly"]
        if _isna(vy):
            m_cells.append((14, "-", 8))
        else:
            m_cells.append((14, float(vy), 11))
        rows_data.append((curr_row, 20.0, m_cells))
        curr_row += 1

    rows_data.append((curr_row, 12.0, []))
    curr_row += 1

    # --- Section 4: Chronological Monthly Track Record & Growth of $1,000,000 USD ---
    if records:
        rows_data.append(
            (curr_row, 24.0, [(1, "CHRONOLOGICAL MONTHLY TRACK RECORD & CUMULATIVE GROWTH OF $1,000,000 USD", 3)] + [(c, None, 3) for c in range(2, 7)])
        )
        merges.append(f"A{curr_row}:F{curr_row}")
        curr_row += 1

        ts_headers = [
            "Date (YYYY-MM)",
            "Mandate Monthly Return" if anonymize else "Fund Monthly Return",
            "S&P 500 Monthly Return",
            "Active Spread vs. S&P 500",
            "Mandate Value ($1M Initial)" if anonymize else "Fund Value ($1M Initial)",
            "S&P 500 Value ($1M Initial)",
        ]
        rows_data.append((curr_row, 22.0, [(c_i, h_t, 4) for c_i, h_t in enumerate(ts_headers, 1)]))
        curr_row += 1

        w_fund = 1_000_000.0
        w_sp = 1_000_000.0
        for rec in records:
            rf = float(rec["fund"])
            rsp = float(rec["sp500"])
            w_fund *= 1.0 + rf
            w_sp *= 1.0 + rsp
            rows_data.append(
                (
                    curr_row,
                    19.5,
                    [
                        (1, f"{rec['year']:04d}-{rec['month']:02d}", 8),
                        (2, rf, 10),
                        (3, rsp, 10),
                        (4, rf - rsp, 10),
                        (5, w_fund, 17),
                        (6, w_sp, 17),
                    ],
                )
            )
            curr_row += 1

    col_widths = [
        (1, 1, 28.0),
        (2, 3, 18.0),
        (4, 4, 18.0),
        (5, 5, 28.0),
        (6, 7, 18.0),
        (8, 8, 26.0),
        (9, 13, 11.5),
        (14, 14, 13.5),
    ]
    return _render_worksheet_xml(rows_data, col_widths, merges=merges, freeze_row=2, auto_fit_columns=True)


def build_tpm_excel_workbook(
    fund_results: List[Dict[str, Any]],
    excel_path: Optional[Union[str, Path]] = None,
    also_save_to_output_dir: Optional[Union[str, Path]] = None,
    anonymize: bool = True,
    timestamp_str: Optional[str] = None,
) -> Path:
    """
    Build the multi-sheet institutional Excel (.xlsx) workbook:
      - Sheet 1: '1. TPM Disclaimer & Notice' (TPM proposition explanation, non-advice notice, conflicts of interest & IP anonymization disclosure)
      - Sheet 2: '2. Summary of Funds' (Executive summary table comparing CAGR, Vol, Sharpe, MDD, Alpha, Beta, Corr, Months, Terms, etc.)
      - Sheet 3..N+2: Separate worksheet for each fund (Terms, Quantitative Indicators, Monthly Return Matrix, & $1M Track Record)
    Saves with a timestamp to `/Users/arthurdhonneur/Downloads/Athenee_TPM_Fund_Analysis_YYYYMMDD_HHMMSS.xlsx`
    (and copies into the timestamped local run subfolder).
    """
    ts = timestamp_str or datetime.now().strftime("%Y%m%d_%H%M%S")
    if excel_path is None or Path(excel_path).resolve() == DEFAULT_DOWNLOADS_EXCEL_PATH.resolve():
        target_path = DOWNLOADS_DIR / f"Athenee_TPM_Fund_Analysis_{ts}.xlsx"
    else:
        raw_p = Path(excel_path).expanduser().resolve()
        if ts not in raw_p.stem:
            target_path = raw_p.with_name(f"{raw_p.stem}_{ts}{raw_p.suffix or '.xlsx'}")
        else:
            target_path = raw_p

    target_path.parent.mkdir(parents=True, exist_ok=True)

    used_sheet_names: set = set()
    sheets: List[Tuple[str, str]] = []

    # 1. Sheet 1: Disclaimer & TPM Proposition Notice
    s1_name = _sanitize_sheet_name("1. TPM Disclaimer & Notice", used_sheet_names)
    sheets.append((s1_name, _build_disclaimer_sheet_xml(len(fund_results))))

    # 2. Sheet 2: Summary of All Selected Funds
    s2_name = _sanitize_sheet_name("2. Summary of Funds", used_sheet_names)
    sheets.append((s2_name, _build_summary_sheet_xml(fund_results, anonymize=anonymize)))

    # 3. Separate Sheet for Each Fund (Anonymized Tab Name by Default)
    for res in fund_results:
        stem = res["fund"]
        meta = res.get("db_meta") or get_fund_metadata(stem)
        anon_id = res.get("anon_id") or get_anonymized_fund_identity(stem)
        if anonymize:
            raw_tab = f"{anon_id['anon_name']} ({anon_id['anon_code']})"
        else:
            raw_tab = meta.get("display_name") or format_fund_title(stem)
        tab_name = _sanitize_sheet_name(raw_tab, used_sheet_names)
        sheets.append((tab_name, _build_single_fund_sheet_xml(res, anonymize=anonymize)))

    # Package into OpenXML .xlsx ZIP archive
    content_types_Overrides = [
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>',
    ]
    wb_sheets_xml = []
    wb_rels_xml = [
        '<Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
    ]

    for idx, (s_name, _) in enumerate(sheets, 1):
        content_types_Overrides.append(
            f'<Override PartName="/xl/worksheets/sheet{idx}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        )
        wb_sheets_xml.append(
            f'<sheet name="{xml_escape(s_name)}" sheetId="{idx}" r:id="rId{idx}"/>'
        )
        wb_rels_xml.append(
            f'<Relationship Id="rId{idx}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{idx}.xml"/>'
        )

    content_types_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
        '  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
        '  <Default Extension="xml" ContentType="application/xml"/>\n  '
        + "\n  ".join(content_types_Overrides)
        + "\n</Types>"
    )

    root_rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        '  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>\n'
        "</Relationships>"
    )

    workbook_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">\n'
        "  <sheets>\n    "
        + "\n    ".join(wb_sheets_xml)
        + "\n  </sheets>\n</workbook>"
    )

    workbook_rels_xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n  '
        + "\n  ".join(wb_rels_xml)
        + "\n</Relationships>"
    )

    with zipfile.ZipFile(target_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types_xml)
        zf.writestr("_rels/.rels", root_rels_xml)
        zf.writestr("xl/workbook.xml", workbook_xml)
        zf.writestr("xl/_rels/workbook.xml.rels", workbook_rels_xml)
        zf.writestr("xl/styles.xml", _build_xlsx_styles_xml())
        for idx, (_, s_xml) in enumerate(sheets, 1):
            zf.writestr(f"xl/worksheets/sheet{idx}.xml", s_xml)

    if also_save_to_output_dir is not None:
        out_copy = Path(also_save_to_output_dir).resolve() / target_path.name
        if out_copy != target_path:
            out_copy.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(target_path, out_copy)

    return target_path


def run_batch_pipeline(
    selected_funds: Union[List[str], str],
    output_dir: Union[str, Path] = DEFAULT_OUTPUT_DIR,
    hf_returns_dir: Union[str, Path] = HF_RETURNS_DIR,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    fund_configs: Optional[Dict[str, Dict]] = None,
    compile_pdf: bool = True,
    build_excel: bool = True,
    excel_path: Union[str, Path] = DEFAULT_DOWNLOADS_EXCEL_PATH,
    anonymize: bool = True,
    use_timestamp_subfolder: bool = True,
    save_csv_files: bool = False,
    keep_tex: bool = False,
) -> List[Dict[str, Any]]:
    """
    Run the tear sheet & Excel generation pipeline for multiple funds in one shot:
      - Stores runs inside `<output_dir>/runs/run_YYYYMMDD_HHMMSS/`
      - Inside each run folder:
          * `Athenee_TPM_Fund_Analysis_YYYYMMDD_HHMMSS.xlsx` (the timestamped Excel workbook)
          * `factsheet/` subfolder containing all related PDF factsheets (`*_tearsheet.pdf`)
      - Anonymizes all fund names deterministically (`anonymize=True` by default) so no IP is leaked
      - Also saves the timestamped Excel workbook directly to `~/Downloads/Athenee_TPM_Fund_Analysis_YYYYMMDD_HHMMSS.xlsx`
    """
    init_or_load_fund_database(hf_returns_dir=Path(hf_returns_dir))

    if isinstance(selected_funds, str):
        if selected_funds.lower() == "all":
            fund_list = list_available_funds(Path(hf_returns_dir))
        else:
            fund_list = [f.strip() for f in selected_funds.split(",") if f.strip()]
    else:
        fund_list = list(selected_funds)

    run_ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_out_dir = Path(output_dir).resolve()
    if use_timestamp_subfolder:
        runs_root = base_out_dir if base_out_dir.name == "runs" else (base_out_dir / "runs")
        run_dir = runs_root / f"run_{run_ts}"
    else:
        run_dir = base_out_dir

    factsheet_dir = run_dir / "factsheet"
    run_dir.mkdir(parents=True, exist_ok=True)
    if compile_pdf or keep_tex:
        factsheet_dir.mkdir(parents=True, exist_ok=True)
    fund_configs = fund_configs or {}

    all_metrics: List[Dict[str, Any]] = []
    fund_results: List[Dict[str, Any]] = []
    print(f"=== Running Athénée Third-Party Marketing Pipeline for {len(fund_list)} fund(s) [Anonymize={anonymize}] ===")
    print(f"=== Local Run Folder: {run_dir} ===")
    print(f"=== Factsheets Folder: {factsheet_dir} ===")

    for idx, fund_name in enumerate(fund_list, 1):
        stem = fund_name.replace(".csv", "").strip()
        cfg = fund_configs.get(stem, {})
        try:
            res = run_fund_pipeline(
                fund_csv_name=stem,
                output_dir=factsheet_dir,
                hf_returns_dir=hf_returns_dir,
                start_date=cfg.get("start_date", start_date),
                end_date=cfg.get("end_date", end_date),
                leverage=cfg.get("leverage", None),
                annual_financing_cost=cfg.get("annual_financing_cost", 0.0),
                custom_title=cfg.get("title", cfg.get("display_name", None)),
                custom_subtitle=cfg.get("subtitle", cfg.get("strategy_subtitle", None)),
                fund_meta=cfg,
                compile_pdf=compile_pdf,
                anonymize=anonymize,
                save_csv_files=save_csv_files,
                keep_tex=keep_tex,
            )
            m = res["metrics"]
            anon_id = res["anon_id"]
            all_metrics.append(m)
            fund_results.append(res)
            status_label = (
                f"factsheet/{os.path.basename(res['pdf_path'])}"
                if res["pdf_path"]
                else (f"factsheet/{os.path.basename(res['tex_path'])}" if res["tex_path"] else "excel-only")
            )
            anon_label = f"{anon_id['anon_name']} ({anon_id['anon_code']})"
            print(
                f"  [{idx}/{len(fund_list)}] {anon_label:<28} | "
                f"CAGR: {m['cagr']*100:6.2f}% | Vol: {m['ann_vol']*100:5.2f}% | "
                f"Sharpe: {m['sharpe']:5.2f} | MDD: {m['mdd']*100:6.2f}% | "
                f"Corr SPX: {m['pearson_corr']:+5.2f} | Out: {status_label}"
            )
        except Exception as e:
            print(f"  [{idx}/{len(fund_list)}] ERROR processing '{stem}': {e}")

    if all_metrics:
        if save_csv_files:
            summary_csv = run_dir / f"summary_selected_funds_metrics_{run_ts}.csv"
            _write_dict_csv(summary_csv, all_metrics)
        if build_excel and fund_results:
            saved_xlsx = build_tpm_excel_workbook(
                fund_results=fund_results,
                excel_path=excel_path,
                also_save_to_output_dir=run_dir,
                anonymize=anonymize,
                timestamp_str=run_ts,
            )
            print(f"=== Timestamped Excel Spreadsheet saved to Downloads: {saved_xlsx} ===")
            print(f"=== Timestamped Excel Spreadsheet saved in Run Folder: {run_dir / saved_xlsx.name} ===")
        print(f"=== Batch Complete! Run folder: {run_dir} ===")
    return all_metrics


# ---------------------------------------------------------------------------
# CLI Entrypoint
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Athénée Investment — Third-Party Marketing & Capital Introduction Tear Sheet & Excel Pipeline"
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
        help="Base output directory where timestamped run_<YYYYMMDD_HHMMSS> folders are created.",
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
        help="Generate CSVs, .tex files, and Excel workbook without running pdflatex.",
    )
    parser.add_argument(
        "--excel",
        action="store_true",
        default=True,
        help="Build the timestamped multi-sheet Excel spreadsheet in ~/Downloads/ (enabled by default).",
    )
    parser.add_argument(
        "--no-excel",
        action="store_true",
        help="Disable building the Excel spreadsheet.",
    )
    parser.add_argument(
        "--excel-only",
        action="store_true",
        help="Fast mode: compute metrics and build the timestamped Excel spreadsheet in ~/Downloads without compiling PDFs.",
    )
    parser.add_argument(
        "--excel-path",
        type=str,
        default=str(DEFAULT_DOWNLOADS_EXCEL_PATH),
        help="Base target path for the generated Excel workbook in ~/Downloads.",
    )
    parser.add_argument(
        "--no-anonymize",
        action="store_true",
        help="Disable fund name anonymization (for internal use only; by default all outputs are anonymized).",
    )
    parser.add_argument(
        "--list-funds",
        action="store_true",
        help="List all available fund CSV names and their deterministic anonymized names and exit.",
    )
    parser.add_argument(
        "--init-db",
        action="store_true",
        help="Initialize or sync third_party_marketing/fund_database.csv and confidential_fund_mapping.csv.",
    )

    args = parser.parse_args()
    init_or_load_fund_database()

    if args.init_db:
        print(f"Fund database initialized and synced at: {FUND_DATABASE_PATH}")
        print(f"Confidential IP mapping table saved at: {CONFIDENTIAL_MAPPING_PATH}")
        return

    if args.list_funds:
        funds = list_available_funds()
        print(f"Available funds in {HF_RETURNS_DIR} ({len(funds)}):")
        for f in funds:
            aid = get_anonymized_fund_identity(f)
            print(f"  - {f:<28} -> {aid['anon_name']:<20} ({aid['anon_code']})")
        return

    compile_pdf_flag = (not args.no_pdf) and (not args.excel_only)
    build_excel_flag = (not args.no_excel) or args.excel_only
    anonymize_flag = not args.no_anonymize

    target_funds: Union[str, List[str]] = (
        "all" if (len(args.funds) == 1 and args.funds[0].lower() == "all") else args.funds
    )
    run_batch_pipeline(
        target_funds,
        output_dir=args.output_dir,
        start_date=args.start_date,
        end_date=args.end_date,
        compile_pdf=compile_pdf_flag,
        build_excel=build_excel_flag,
        excel_path=args.excel_path,
        anonymize=anonymize_flag,
        use_timestamp_subfolder=True,
    )


if __name__ == "__main__":
    main()

