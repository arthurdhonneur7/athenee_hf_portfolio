import nbformat

with open('target_pflio.ipynb', 'r') as f:
    nb = nbformat.read(f, as_version=4)

target_cell_idx = -1
for i, cell in enumerate(nb.cells):
    if cell.cell_type == 'code' and "REPORT_DIR = 'report/lazarus_admin'" in cell.source:
        target_cell_idx = i
        break

if target_cell_idx != -1:
    source = nb.cells[target_cell_idx].source
    
    # We will print the code snippet from the cell to understand it better
    print("Found cell. Excerpt:")
    start = source.find('latex_strat_stats =')
    end = source.find('latex_portfolios_other =')
    if start != -1 and end != -1:
        print(source[start:end])
    
    start_latex = source.find(r'\subsection*{Strategy Statistics}')
    end_latex = source.find(r'""" + latex_strat_stats + r"""')
    print("Latex output excerpt:")
    if start_latex != -1 and end_latex != -1:
        print(source[start_latex:end_latex+32])
