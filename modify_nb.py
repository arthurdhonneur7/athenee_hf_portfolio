import json

with open('target_pflio.ipynb', 'r') as f:
    nb = json.load(f)

# Find cell 13
cell = nb['cells'][13]
source = "".join(cell['source'])

original_source = source

# 1. Scatter plot
s1 = 'latex_6m_plots += "\\\\begin{figure}[h]\\n    \\\\centering\\n    \\\\includegraphics[width=0.95\\\\textwidth, height=0.25\\\\textheight, keepaspectratio]{scatter_6_month_reb_initial_alloc_vs_sp500.pdf}\\n\\\\end{figure}\\n\\n"'
s1_rep = ''
if s1 in source:
    source = source.replace(s1, s1_rep)
    print("Replaced 1 (part a)")
else:
    print("Could not find s1")
    print(repr(s1))

s2 = '\\begin{figure}[h]\n    \\centering\n    \\includegraphics[width=0.95\\textwidth, height=0.25\\textheight, keepaspectratio]{4_strategies_growth.pdf}\n\\end{figure}\n'
s2_rep = '\\begin{figure}[h]\n    \\centering\n    \\includegraphics[width=0.95\\textwidth, height=0.25\\textheight, keepaspectratio]{4_strategies_growth.pdf}\n\\end{figure}\n\n\\begin{figure}[h]\n    \\centering\n    \\includegraphics[width=0.95\\textwidth, height=0.25\\textheight, keepaspectratio]{scatter_6_month_reb_initial_alloc_vs_sp500.pdf}\n\\end{figure}\n'

if s2 in source:
    source = source.replace(s2, s2_rep)
    print("Replaced 1 (part b)")
else:
    print("Could not find s2")


# 2. Card template
s3 = '''    card_template = f"""
\\begin{{tcolorbox}}[colback=cardbg, colframe=cardborder, boxrule=0.5pt, arc=4pt, left=6pt, right=6pt, top=6pt, bottom=6pt]
    \\textbf{{\\textcolor{{primary}}{{{escape_latex(fund_name_display)}}}}} \\hfill \\textbf{{\\textcolor{{accent}}{{{alloc_str}}}}} \\\\[4pt]
    \\textcolor{{primary}}{{{desc}}}
\\end{{tcolorbox}}
"""'''

s3_rep = '''    card_template = f"""
\\begin{{tcolorbox}}[colback=cardbg, colframe=cardborder, boxrule=0.5pt, arc=2pt, left=2pt, right=2pt, top=2pt, bottom=2pt]
    \\textbf{{\\textcolor{{primary}}{{{escape_latex(fund_name_display)}}}}} \\hfill \\textbf{{\\textcolor{{accent}}{{{alloc_str}}}}} \\\\[2pt]
    \\textcolor{{primary}}{{\\scriptsize {desc}}}
\\end{{tcolorbox}}
"""'''

if s3 in source:
    source = source.replace(s3, s3_rep)
    print("Replaced 2")
else:
    print("Could not find s3")


# 3. Alloc section
s4 = r'''\section*{Fund Allocation \& Strategy Descriptions}
The table below highlights the initial capital allocation weights alongside a brief description of each underlying fund's distinct edge and methodology.

""" + latex_fund_descriptions + r"""
\clearpage

\section*{Detailed Fund Statistics}
""" + latex_funds_stats + r"""
\clearpage'''

s4_rep = r'''\section*{Fund Allocation \& Strategy Descriptions}

""" + latex_fund_descriptions + r"""

\vspace{1em}
\section*{Detailed Fund Statistics}
""" + latex_funds_stats + r"""
\clearpage'''

if s4 in source:
    source = source.replace(s4, s4_rep)
    print("Replaced 3")
else:
    print("Could not find s4")

# 4. Performance & Correlation figures
s5 = r'''\section*{Performance \& Correlation}
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
\end{figure}'''

s5_rep = r'''\section*{Performance \& Correlation}
The following visuals illustrate the fund-level statistics and the diversification benefits.

\begin{figure}[h]
    \centering
    \includegraphics[width=0.95\textwidth, height=0.22\textheight, keepaspectratio]{fund_stats.pdf}
\end{figure}
\vspace{-1.5em}

\begin{figure}[h]
    \centering
    \includegraphics[width=0.95\textwidth, height=0.22\textheight, keepaspectratio]{correlation.pdf}
\end{figure}
\vspace{-1.5em}

\begin{figure}[h]
    \centering
    \includegraphics[width=0.95\textwidth, height=0.22\textheight, keepaspectratio]{worst_sp500_months.pdf}
\end{figure}'''

if s5 in source:
    source = source.replace(s5, s5_rep)
    print("Replaced 4")
else:
    print("Could not find s5")

# Split lines back
lines = []
for line in source.split('\n'):
    lines.append(line + '\n')
# fix the last newline
if not source.endswith('\n'):
    lines[-1] = lines[-1][:-1]

cell['source'] = lines

with open('target_pflio.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)

print("Done updating ipynb")
