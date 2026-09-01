import nbformat
import re

with open('target_pflio.ipynb', 'r') as f:
    nb = nbformat.read(f, as_version=4)

for i, cell in enumerate(nb.cells):
    if cell.cell_type == 'code':
        original = cell.source
        
        # 1. Reduce monthly table arraystretch and add scriptsize
        # It's currently: \renewcommand{\arraystretch}{1.3}
        if r'\renewcommand{\arraystretch}{1.3}' in cell.source and 'latex_monthly' in cell.source:
            cell.source = cell.source.replace(
                r'\renewcommand{\arraystretch}{1.3}',
                r'\renewcommand{\arraystretch}{1.1}' + '\n' + r'\scriptsize'
            )
            print(f"Reduced arraystretch in latex_monthly in cell {i}")
            
        # 2. Reduce margins
        if r'\usepackage[left=0.2in, right=0.2in, top=0.4in, bottom=0.4in]{geometry}' in cell.source:
            cell.source = cell.source.replace(
                r'\usepackage[left=0.2in, right=0.2in, top=0.4in, bottom=0.4in]{geometry}',
                r'\usepackage[left=0.2in, right=0.2in, top=0.25in, bottom=0.25in]{geometry}'
            )
            print(f"Reduced page margins in cell {i}")
            
        # 3. Reduce title space
        if r'Athenee Lazarus Alpha AMC}\\[1.5em]' in cell.source:
            cell.source = cell.source.replace(
                r'Athenee Lazarus Alpha AMC}\\[1.5em]',
                r'Athenee Lazarus Alpha AMC}\\[0.5em]'
            )
            print(f"Reduced title space in cell {i}")
            
        # 4. Reduce vspace before Historical net monthly returns
        if r'\vspace{1em}' + '\n\n' + r'\subsection*{Historical net monthly returns' in cell.source:
            cell.source = cell.source.replace(
                r'\vspace{1em}' + '\n\n' + r'\subsection*{Historical net monthly returns',
                r'\vspace{0.25em}' + '\n\n' + r'\subsection*{Historical net monthly returns'
            )
            print(f"Reduced space before monthly returns in cell {i}")

with open('target_pflio.ipynb', 'w') as f:
    nbformat.write(nb, f)

print("Notebook updated to fit in one page.")
