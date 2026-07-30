import json

with open('target_pflio.ipynb', 'r') as f:
    nb = json.load(f)

for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        if 'latex' in source.lower() or 'plot' in source.lower() or 'scatter' in source.lower() or 'figure' in source.lower():
            print(f"--- Cell {i} ---")
            print(source[:500] + ("..." if len(source) > 500 else ""))
