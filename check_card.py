import json

with open('target_pflio.ipynb', 'r') as f:
    nb = json.load(f)

source = "".join(nb['cells'][13]['source'])

for i, line in enumerate(source.split('\n')):
    if 'card_template =' in line:
        for j in range(i, i+10):
            print(repr(source.split('\n')[j]))
            if '"""' in source.split('\n')[j] and j > i:
                break
