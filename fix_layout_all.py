import nbformat

with open('target_pflio.ipynb', 'r') as f:
    nb = nbformat.read(f, as_version=4)

for i, cell in enumerate(nb.cells):
    if cell.cell_type == 'code' and ('latex_strat_stats =' in cell.source or 'latex_monthly =' in cell.source):
        source = cell.source
        
        # 1. Revert monthly returns matrix size
        source = source.replace(
            r'\renewcommand{\arraystretch}{1.1}' + '\n' + r'\scriptsize',
            r'\renewcommand{\arraystretch}{1.3}'
        )
        
        # 2. Make sure the 4 blocks have \footnotesize and arraystretch 1.3
        # Since I might have replaced them partially, let's just do a regex or find-replace
        # We need to make sure we don't double replace
        if r'\renewcommand{\arraystretch}{1.8}' in source:
            source = source.replace(r'\renewcommand{\arraystretch}{1.8}', r'\renewcommand{\arraystretch}{1.3}' + '\n' + r'\footnotesize')
            
        # 3. Remove empty row in Company Information
        # It's \rowcolor{cardbg} & \\ right before \end{tabularx} in Company Information
        if r'\rowcolor{cardbg} & \\' + '\n' + r'\end{tabularx}' + '\n' + r'\end{tcolorbox}' + '\n' + r'\end{minipage}' in source:
            source = source.replace(
                r'\rowcolor{cardbg} & \\' + '\n' + r'\end{tabularx}' + '\n' + r'\end{tcolorbox}' + '\n' + r'\end{minipage}',
                r'\end{tabularx}' + '\n' + r'\end{tcolorbox}' + '\n' + r'\end{minipage}'
            )
            
        # Also fix any missing \noindent before \begin{minipage} for General Info
        if r'\vspace{1.5em}' + '\n\n' + r'\begin{minipage}[t]{0.48\textwidth}' in source:
            source = source.replace(
                r'\vspace{1.5em}' + '\n\n' + r'\begin{minipage}[t]{0.48\textwidth}',
                r'\vspace{1.5em}' + '\n\\noindent\n' + r'\begin{minipage}[t]{0.48\textwidth}'
            )

        if r'\vspace{0.5em}' + '\n\n' + r'\begin{minipage}[t]{0.48\textwidth}' in source:
            source = source.replace(
                r'\vspace{0.5em}' + '\n\n' + r'\begin{minipage}[t]{0.48\textwidth}',
                r'\vspace{0.5em}' + '\n\\noindent\n' + r'\begin{minipage}[t]{0.48\textwidth}'
            )
            
        # Add \noindent to latex_strat_stats
        if r'latex_strat_stats += r"""' + '\n' + r'\begin{minipage}[t]{0.48\textwidth}' in source:
             source = source.replace(
                r'latex_strat_stats += r"""' + '\n' + r'\begin{minipage}[t]{0.48\textwidth}',
                r'latex_strat_stats += r"""' + '\n\\noindent\n' + r'\begin{minipage}[t]{0.48\textwidth}'
             )

        cell.source = source
        print(f"Updated cell {i}")

with open('target_pflio.ipynb', 'w') as f:
    nbformat.write(nb, f)
