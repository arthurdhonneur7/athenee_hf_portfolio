import nbformat

with open('target_pflio.ipynb', 'r') as f:
    nb = nbformat.read(f, as_version=4)

old_table_def = r'''latex_strat_stats = r"""\begin{table}[h]
\centering
\renewcommand{\arraystretch}{1.8}
\footnotesize
\begin{tabularx}{\textwidth}{*{3}{>{\centering\arraybackslash}X} c *{8}{>{\centering\arraybackslash}X}}
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
\end{table}"""'''

new_table_def = r'''latex_strat_stats = ""
for idx in strat_df.index:
    row = strat_df.loc[idx]
    row_vals = [escape_latex(str(x)) for x in row.values]
    
    latex_strat_stats += r"""
\begin{minipage}[t]{0.48\textwidth}
\begin{tcolorbox}[colback=white, colframe=primary, title=\textbf{\large Performance \& Risk}, fonttitle=\sffamily\bfseries\large, arc=6pt, boxrule=1pt, toptitle=6pt, bottomtitle=6pt, left=0pt, right=0pt, top=0pt, bottom=0pt, colbacktitle=primary]
\renewcommand{\arraystretch}{1.8}
\begin{tabularx}{\textwidth}{>{\columncolor{white}}X >{\columncolor{white}}r}
\rowcolor{cardbg} \textbf{\textcolor{primary}{CAGR}} & \textcolor{primary}{""" + row_vals[0] + r"""} \\
\textbf{\textcolor{primary}{Std}} & \textcolor{primary}{""" + row_vals[1] + r"""} \\
\rowcolor{cardbg} \textbf{\textcolor{primary}{Proxy Sharpe}} & \textcolor{primary}{""" + row_vals[2] + r"""} \\
\textbf{\textcolor{primary}{MDD}} & \textcolor{primary}{""" + row_vals[3] + r"""} \\
\rowcolor{cardbg} \textbf{\textcolor{primary}{Calmar}} & \textcolor{primary}{""" + row_vals[4] + r"""} \\
\textbf{\textcolor{primary}{Pos Months}} & \textcolor{primary}{""" + row_vals[5] + r"""} \\
\end{tabularx}
\end{tcolorbox}
\end{minipage}\hfill
\begin{minipage}[t]{0.48\textwidth}
\begin{tcolorbox}[colback=white, colframe=primary, title=\textbf{\large Market Analysis}, fonttitle=\sffamily\bfseries\large, arc=6pt, boxrule=1pt, toptitle=6pt, bottomtitle=6pt, left=0pt, right=0pt, top=0pt, bottom=0pt, colbacktitle=primary]
\renewcommand{\arraystretch}{1.8}
\begin{tabularx}{\textwidth}{>{\columncolor{white}}X >{\columncolor{white}}r}
\rowcolor{cardbg} \textbf{\textcolor{primary}{Up Capture}} & \textcolor{primary}{""" + row_vals[6] + r"""} \\
\textbf{\textcolor{primary}{Down Capture}} & \textcolor{primary}{""" + row_vals[7] + r"""} \\
\rowcolor{cardbg} \textbf{\textcolor{primary}{Alpha (t-stat)}} & \textcolor{primary}{""" + row_vals[8] + r"""} \\
\textbf{\textcolor{primary}{Beta}} & \textcolor{primary}{""" + row_vals[9] + r"""} \\
\rowcolor{cardbg} \textbf{\textcolor{primary}{Corr SP500}} & \textcolor{primary}{""" + row_vals[10] + r"""} \\
\textbf{\textcolor{primary}{N months}} & \textcolor{primary}{""" + row_vals[11] + r"""} \\
\end{tabularx}
\end{tcolorbox}
\end{minipage}
"""'''

for i, cell in enumerate(nb.cells):
    if cell.cell_type == 'code':
        if old_table_def in cell.source:
            cell.source = cell.source.replace(old_table_def, new_table_def)
            print(f"Replaced table def in cell {i}")
            
        if r'\subsection*{Strategy Statistics}' in cell.source:
            cell.source = cell.source.replace(r'\subsection*{Strategy Statistics}', '')
            print(f"Removed subsection title in cell {i}")

with open('target_pflio.ipynb', 'w') as f:
    nbformat.write(nb, f)

print("Notebook updated.")
