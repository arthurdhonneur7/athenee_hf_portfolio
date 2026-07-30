import json

with open('target_pflio.ipynb', 'r') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = cell['source']
        new_source = []
        for line in source:
            if "if fund == 'm1': fund_name_display = 'M1'" in line:
                continue
            if "if fund == 'arr': fund_name_display = 'ARR'" in line:
                continue
            new_source.append(line)
        cell['source'] = new_source

with open('target_pflio.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)
    f.write('\n')
