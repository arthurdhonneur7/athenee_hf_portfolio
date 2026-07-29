import json

file_path = '/Users/arthurdhonneur/Desktop/Athenee/athenee_hf_pflio/target_pflio.ipynb'
with open(file_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb.get('cells', []):
    if cell.get('cell_type') == 'code':
        source = cell.get('source', [])
        for i, line in enumerate(source):
            if "\\definecolor{accent}{RGB}{37, 99, 235}" in line:
                source[i] = line.replace("\\definecolor{accent}{RGB}{37, 99, 235}", "\\definecolor{accent}{RGB}{26, 54, 93}")

        cell['source'] = source

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)
