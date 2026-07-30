import os
import subprocess
import numpy as np
import statsmodels.api as sm
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Create report folder so we don't pollute the repo
REPORT_DIR = 'report'
os.makedirs(REPORT_DIR, exist_ok=True)

# Helper function to escape LaTeX special characters
def escape_latex(text):
    if not isinstance(text, str):
        text = str(text)
    return text.replace('%', '\\%').replace('&', '\\&').replace('_', '\\_')

# 2. Calculate Comprehensive Statistics
def compute_stats(fund_ret, sp500_ret):
    c_idx = fund_ret.dropna().index.intersection(sp500_ret.index)
    f_align = fund_ret.loc[c_idx]
    s_align = sp500_ret.loc[c_idx]
    
    n_months = len(f_align)
    if n_months == 0: return {}
    
    n_years = n_months / 12
    cum_wealth = (1 + f_align).cumprod()
    cagr = cum_wealth.iloc[-1]**(1/n_years) - 1 if cum_wealth.iloc[-1] > 0 else np.nan
    std = f_align.std() * np.sqrt(12)
    proxy_sharpe = (f_align.mean() * 12) / std if std != 0 else np.nan
    
    peak = cum_wealth.cummax()
    mdd = ((cum_wealth - peak) / peak).min()
    calmar = cagr / abs(mdd) if mdd != 0 else np.nan
    
    pos_months = (f_align > 0).sum() / n_months * 100
    
    s_pos = s_align > 0
    s_neg = s_align < 0
    up_capture = f_align[s_pos].mean() / s_align[s_pos].mean() if s_pos.sum() > 0 else np.nan
    down_capture = f_align[s_neg].mean() / s_align[s_neg].mean() if s_neg.sum() > 0 else np.nan
    
    corr = f_align.corr(s_align)
    q25 = s_align.quantile(0.25)
    mask_25 = s_align < q25
    corr_25 = f_align[mask_25].corr(s_align[mask_25]) if mask_25.sum() > 1 else np.nan
    
    X = sm.add_constant(s_align)
    model = sm.OLS(f_align, X).fit()
    alpha = model.params['const'] * 12
    alpha_t = model.tvalues['const']
    beta = model.params['sp500']
    
    return {
        'CAGR': f"{cagr:.2%}" if pd.notna(cagr) else "-",
        'Std': f"{std:.2%}" if pd.notna(std) else "-",
        'Proxy Sharpe': f"{proxy_sharpe:.2f}" if pd.notna(proxy_sharpe) else "-",
        'MDD': f"{mdd:.2%}" if pd.notna(mdd) else "-",
        'Calmar': f"{calmar:.2f}" if pd.notna(calmar) else "-",
        'Pos Months': f"{pos_months:.1f}%",
        'Up Capture': f"{up_capture:.2f}" if pd.notna(up_capture) else "-",
        'Down Capture': f"{down_capture:.2f}" if pd.notna(down_capture) else "-",
        'Alpha (t-stat)': f"{alpha:.2%} ({alpha_t:.2f})" if pd.notna(alpha) else "-",
        'Beta': f"{beta:.2f}" if pd.notna(beta) else "-",
        'Corr SP500': f"{corr:.2f}" if pd.notna(corr) else "-",
        'N Months': n_months
    }

funds_stats_list = []
fund_names = []
for f in selected_funds:
    if f in df_funds_full.columns:
        s = compute_stats(df_funds_full[f], sp500)
        if s:
            funds_stats_list.append(s)
            fund_names.append(f.replace('_', ' ').title())

funds_df = pd.DataFrame(funds_stats_list, index=fund_names)
funds_df.to_csv(f'{REPORT_DIR}/funds_statistics.csv')

port_6m = all_portfolios_df['6-Month Reb Initial Alloc']
common_idx = port_6m.index.intersection(sp500.index)
p_6m_align = port_6m.loc[common_idx]

strat_stats = compute_stats(port_6m, sp500)
strat_df = pd.DataFrame([strat_stats], index=['Lazarus Alpha'])
strat_df.to_csv(f'{REPORT_DIR}/6m_strategy_statistics.csv')

# Generate 6m monthly returns table
ret_monthly = p_6m_align.copy()
ret_monthly.index = pd.to_datetime(ret_monthly.index)
grouped = ret_monthly.groupby([ret_monthly.index.year, ret_monthly.index.month]).sum()
monthly_df = grouped.unstack()
for m in range(1, 13):
    if m not in monthly_df.columns:
        monthly_df[m] = np.nan
monthly_df = monthly_df.sort_index(axis=1)
monthly_df['YTD'] = (1 + monthly_df.fillna(0)).prod(axis=1) - 1

def format_ret_csv(val):
    if pd.isna(val) or val == 0:
        return "-"
    return f"{val*100:.1f}%"

csv_df = monthly_df.copy()
csv_df = csv_df.map(format_ret_csv)
csv_df.columns = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'YTD']
csv_df.index.name = 'Year'
csv_df.to_csv(f'{REPORT_DIR}/6m_monthly_returns.csv')

def format_ret_latex(val):
    if pd.isna(val) or val == 0:
        return "-"
    str_val = escape_latex(f"{val*100:.1f}%")
    intensity = min(int(abs(val) * 1000), 100)
    if val > 0:
        return f"\\cellcolor{{posgreen!{intensity}!white}}{str_val}"
    elif val < 0:
        return f"\\cellcolor{{negred!{intensity}!white}}{str_val}"
    return str_val

latex_monthly = r"""\begin{table}[h]
\centering
\renewcommand{\arraystretch}{1.3}
\begin{tabularx}{\textwidth}{l *{13}{>{\centering\arraybackslash}X}}
\toprule
\textbf{Year} & \textbf{Jan} & \textbf{Feb} & \textbf{Mar} & \textbf{Apr} & \textbf{May} & \textbf{Jun} & \textbf{Jul} & \textbf{Aug} & \textbf{Sep} & \textbf{Oct} & \textbf{Nov} & \textbf{Dec} & \textbf{YTD} \\
\midrule
"""
for year in monthly_df.index:
    row = monthly_df.loc[year]
    formatted_row = " & ".join([format_ret_latex(row[m]) for m in range(1, 13)] + [format_ret_latex(row['YTD'])])
    latex_monthly += f"{year} & {formatted_row} \\\\\n"
latex_monthly += r"""\bottomrule
\end{tabularx}
\end{table}"""

latex_funds_stats = r"""\begin{table}[h]
\centering
\renewcommand{\arraystretch}{1.3}
\scriptsize
\begin{tabularx}{\textwidth}{l *{12}{>{\centering\arraybackslash}X}}
\toprule
 & \textbf{CAGR} & \textbf{Std} & \textbf{Proxy Sharpe} & \textbf{MDD} & \textbf{Calmar} & \textbf{Pos Months} & \textbf{Up Capture} & \textbf{Down Capture} & \textbf{Alpha (t-stat)} & \textbf{Beta} & \textbf{Corr SP500} & \textbf{N months}\\
\midrule
"""
for idx in funds_df.index:
    row = funds_df.loc[idx]
    row_vals = [escape_latex(str(x)) for x in row.values]
    idx_clean = escape_latex(str(idx))
    latex_funds_stats += f"\\textbf{{{idx_clean}}} & " + " & ".join(row_vals) + r" \\" + "\n"
latex_funds_stats += r"""\bottomrule
\end{tabularx}
\end{table}"""

latex_strat_stats = r"""\begin{table}[h]
\centering
\renewcommand{\arraystretch}{1.3}
\scriptsize
\begin{tabularx}{\textwidth}{*{12}{>{\centering\arraybackslash}X}}
\toprule
\textbf{CAGR} & \textbf{Std} & \textbf{Proxy Sharpe} & \textbf{MDD} & \textbf{Calmar} & \textbf{Pos Months} & \textbf{Up Capture} & \textbf{Down Capture} & \textbf{Alpha (t-stat)} & \textbf{Beta} & \textbf{Corr SP500} & \textbf{N months}\\
\midrule
"""
for idx in strat_df.index:
    row = strat_df.loc[idx]
    row_vals = [escape_latex(str(x)) for x in row.values]
    latex_strat_stats += " & ".join(row_vals) + r" \\" + "\n"
latex_strat_stats += r"""\bottomrule
\end{tabularx}
\end{table}"""

latex_portfolios_other = ""
latex_6m_plots = ""

try:
    port_cols = portfolios_df.columns
except NameError:
    port_cols = []

# for port_name in port_cols:
#     safe_name = port_name.replace(' ', '_').replace('-', '_').lower()
#     plot_str = f"\\begin{{figure}}[h]\n    \\centering\n    \\includegraphics[width=0.95\\textwidth, height=0.25\\textheight, keepaspectratio]{{growth_{safe_name}_vs_sp500.pdf}}\n\\end{{figure}}\n\n"
#     plot_str += f"\\begin{{figure}}[h]\n    \\centering\n    \\includegraphics[width=0.95\\textwidth, height=0.25\\textheight, keepaspectratio]{{scatter_{safe_name}_vs_sp500.pdf}}\n\\end{{figure}}\n\n"
    
#     if safe_name == '6_month_reb_initial_alloc':
#         latex_6m_plots += plot_str
#     else:
#         latex_portfolios_other += plot_str


latex_6m_plots += "\\begin{figure}[h]\n    \\centering\n    \\includegraphics[width=0.95\\textwidth, height=0.35\\textheight, keepaspectratio]{combined_growth_worst20_sp500.pdf}\n\\end{figure}\n\n"
latex_6m_plots += "\\begin{figure}[h]\n    \\centering\n    \\includegraphics[width=0.95\\textwidth, height=0.25\\textheight, keepaspectratio]{scatter_6_month_reb_initial_alloc_vs_sp500.pdf}\n\\end{figure}\n\n"

fund_descriptions = {
    'm1': 'Crypto carry trade market neutral fund.',
    'vadantia': 'Trading-oriented fund on FX and precious metals with more than 4 trades per day.',
    'enko': 'Africa debt fund that invests to maturity in sovereign bonds, arbitraging between onshore and offshore bonds.',
    'wizard_quant': 'Chinese equity market neutral fund that is strictly quant-driven.',
    'arr': 'Trading fund on equities and macro, utilizing a quantamental approach to identify equities with high upside, backed by a strict risk management policy.',
    'r_squared': 'Equities futures arbitrage and dividend futures arbitrage relative value style fund.',
    'shiprock': 'Fund investing in highly distressed debt and bond contracts.',
    'grasshoper': 'Market maker in Singapore investing in high-frequency strategies. They launched their open commingled fund for strategies that are highly scalable.',
    '26_miles': 'Indian-based fund investing in medium-frequency strategies across a lot of asset classes (intra-day trading with holdings of 2-3 hours). Founded by a team with strong prop trading desk experience who spun out to create this fund.',
    'quanstream': 'Volatility seller across more than 150 commodities underlying with over 20 years of experience in these strategies.',
    'edge_capital': 'Edge capital fund description.',
    'adar1': 'Adar1 fund description.',
    'coban_clarion_multi_asset': 'Coban clarion multi asset fund description.',
    'coban_pod_1': 'Coban pod 1 fund description.',
    'coban_orca': 'Coban orca fund description.',
    'anvik': 'Anvik fund description.',
    'smithson': 'Smithson fund description.',
    'spear_digital': 'Spear digital fund description.',
    'blackrock_sta': 'Blackrock sta fund description.',
    'sam_capital': 'Sam capital fund description.'
}

# Ensure allocations is available, if not define a dummy one to avoid name errors 
try:
    allocs = allocations
except NameError:
    allocs = {k: 0.05 for k in fund_descriptions.keys()}

latex_fund_descriptions = ""
for fund in allocs.keys():
    fund_name_display = fund.replace('_', ' ').title()
    if fund == 'm1': fund_name_display = 'M1'
    if fund == 'arr': fund_name_display = 'ARR'
    desc = escape_latex(fund_descriptions.get(fund, 'Description to be added.'))
    alloc_val = allocs.get(fund, 0)
    alloc_pct = (alloc_val / sum(allocs.values())) * 100 if sum(allocs.values()) > 0 else 0
    alloc_str = escape_latex(f"{alloc_pct:.1f}%") if alloc_val else ""
    
    card_template = f"""
\\begin{{tcolorbox}}[colback=cardbg, colframe=cardborder, boxrule=0.5pt, arc=4pt, left=6pt, right=6pt, top=6pt, bottom=6pt]
    \\textbf{{\\textcolor{{primary}}{{{escape_latex(fund_name_display)}}}}} \\hfill \\textbf{{\\textcolor{{accent}}{{{alloc_str}}}}} \\\\[4pt]
    \\textcolor{{primary}}{{{desc}}}
\\end{{tcolorbox}}
"""
    latex_fund_descriptions += card_template

latex_template = r"""
\documentclass[11pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[left=0.2in, right=0.2in, top=0.4in, bottom=0.8in]{geometry}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{xcolor}
\usepackage{colortbl}
\usepackage{tabularx}
\usepackage{tcolorbox}
\usepackage{titlesec}
\usepackage{microtype}
\usepackage{helvet}
\usepackage{hyperref}

\renewcommand{\familydefault}{\sfdefault}

\definecolor{primary}{RGB}{15, 23, 42}
\definecolor{accent}{RGB}{26, 54, 93}
\definecolor{cardbg}{RGB}{248, 250, 252}
\definecolor{cardborder}{RGB}{226, 232, 240}
\definecolor{posgreen}{RGB}{34, 197, 94}
\definecolor{negred}{RGB}{239, 68, 68}

\titleformat{\section}
  {\normalfont\Large\bfseries\color{primary}}
  {}{0em}
  {\color{accent}\vrule width 4pt\hspace{6pt}\color{primary}}

\begin{document}

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% PAGE 1: 6-Month Strategy Deep Dive
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

{\Huge \bfseries \color{accent} Athenee Lazarus Alpha AMC}\\[2.5em]

\begin{tcolorbox}[boxrule=0pt, leftrule=4pt, colframe=primary, colback=cardbg, sharp corners]
\textbf{\large Executive Summary} \\[4pt]
This product is a fund of hedge funds. The core idea is to pick strong performers that are uncorrelated, ensuring that returns keep up while overall volatility and max drawdown are significantly reduced. By blending distinct, non-overlapping strategies, the portfolio aims for robust risk-adjusted returns across market cycles.
\end{tcolorbox}

\subsection*{Monthly Returns Breakdown}
""" + latex_monthly + r"""

\subsection*{Strategy Statistics}
""" + latex_strat_stats + r"""

""" + latex_6m_plots + r"""

\clearpage
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% PAGE 2: Fund Allocation & Strategy Descriptions
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\section*{Fund Allocation \& Strategy Descriptions}
The table below highlights the initial capital allocation weights alongside a brief description of each underlying fund's distinct edge and methodology.

""" + latex_fund_descriptions + r"""
\clearpage

\section*{Detailed Fund Statistics}
""" + latex_funds_stats + r"""
\clearpage

\section*{Performance \& Correlation}
The following visuals illustrate the fund-level statistics and the diversification benefits.

\begin{figure}[h]
    \centering
    \includegraphics[width=0.95\textwidth, height=0.25\textheight, keepaspectratio]{fund_stats.pdf}
\end{figure}

\begin{figure}[h]
    \centering
    \includegraphics[width=0.95\textwidth, height=0.25\textheight, keepaspectratio]{correlation.pdf}
\end{figure}

\begin{figure}[h]
    \centering
    \includegraphics[width=0.95\textwidth, height=0.25\textheight, keepaspectratio]{worst_sp500_months.pdf}
\end{figure}

\clearpage
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% LAST PAGE: Portfolio Backtest Methodologies
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\section*{Portfolio Growth Analysis}
Here we compare four portfolio weighting methodologies.

\begin{figure}[h]
    \centering
    \includegraphics[width=0.95\textwidth, height=0.25\textheight, keepaspectratio]{4_strategies_growth.pdf}
\end{figure}

""" + latex_portfolios_other + r"""

\end{document}
"""

with open(f'{REPORT_DIR}/presentation.tex', 'w') as f:
    f.write(latex_template)

print("Compiling LaTeX to PDF...")
result = subprocess.run(['pdflatex', '-interaction=nonstopmode', 'presentation.tex'], capture_output=True, text=True, cwd=REPORT_DIR)
if result.returncode != 0:
    print(result.stdout)
subprocess.run(['pdflatex', '-interaction=nonstopmode', 'presentation.tex'], capture_output=True, cwd=REPORT_DIR)
print("Done! presentation.pdf and detailed CSVs generated successfully in the 'report' directory.")

# Copy to Google Drive
import shutil
import os
pdf_path = f'{REPORT_DIR}/presentation.pdf'
drive_dir = '/Users/arthurdhonneur/Google Drive/My Drive/Athenee/Presentation_Final_Product'
if os.path.exists(pdf_path) and os.path.exists(drive_dir):
    try:
        shutil.copy(pdf_path, drive_dir)
        print('Successfully copied presentation.pdf to Google Drive!')
    except Exception as e:
        print(f'Failed to copy to Google Drive: {e}')
