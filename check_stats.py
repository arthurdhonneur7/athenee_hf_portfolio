import json

with open('target_pflio.ipynb', 'r') as f:
    nb = json.load(f)

source = "".join(nb['cells'][13]['source'])

for i, line in enumerate(source.split('\n')):
    if 'latex_funds_stats =' in line:
        for j in range(i, i+15):
            print(repr(source.split('\n')[j]))
