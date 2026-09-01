import nbformat
import re

with open('target_pflio.ipynb', 'r') as f:
    nb = nbformat.read(f, as_version=4)

for i, cell in enumerate(nb.cells):
    if cell.cell_type == 'code' and "REPORT_DIR = 'report/lazarus_admin'" in cell.source:
        source = cell.source
        
        # 1. Revert monthly returns matrix size
        source = source.replace(
            r'\renewcommand{\arraystretch}{1.1}' + '\n' + r'\scriptsize',
            r'\renewcommand{\arraystretch}{1.3}'
        )
        
        # 2. Make the 4 blocks of data smaller
        # To make the 4 bottom blocks smaller, we can use \footnotesize inside them and arraystretch 1.2 or 1.0 instead of 1.8
        
        # Performance & Risk and Market Analysis are defined in latex_strat_stats
        # Change their arraystretch from 1.8 to 1.3, and use \footnotesize
        source = source.replace(
            r'\renewcommand{\arraystretch}{1.8}' + '\n' + r'\begin{tabularx}{\textwidth}',
            r'\renewcommand{\arraystretch}{1.3}' + '\n' + r'\footnotesize' + '\n' + r'\begin{tabularx}{\textwidth}'
        )
        
        # Remove the last empty row in Company Information
        source = source.replace(
            r'\rowcolor{cardbg} & \\' + '\n' + r'\end{tabularx}' + '\n' + r'\end{tcolorbox}' + '\n' + r'\end{minipage}',
            r'\end{tabularx}' + '\n' + r'\end{tcolorbox}' + '\n' + r'\end{minipage}'
        )
        
        # Also remove \rowcolor{cardbg} & \\ in Performance & Risk and Market Analysis if they have it?
        # In my previous edit I didn't add empty rows to them.
        
        # Wait, what if the \vspace before General Info is missing?
        # Let's print the area around General Info and Company Info to inspect alignment issues.
        start = source.find(r'\begin{tcolorbox}[colback=white, colframe=primary, title=\textbf{\large General Information}')
        if start != -1:
            print(source[start-150:start+800])
        
        cell.source = source
        print(f"Updated cell {i}")

with open('target_pflio.ipynb', 'w') as f:
    nbformat.write(nb, f)
