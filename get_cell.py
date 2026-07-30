import json

with open('target_pflio.ipynb', 'r') as f:
    nb = json.load(f)

for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        if 'def escape_latex' in source:
            with open('cell_13.py', 'w') as out:
                out.write(source)
            print("Wrote cell 13 to cell_13.py")
