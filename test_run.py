import json

with open('target_pflio.ipynb', 'r') as f:
    nb = json.load(f)

source = "".join(nb['cells'][13]['source'])
with open('test_cell_13.py', 'w') as out:
    out.write(source)
