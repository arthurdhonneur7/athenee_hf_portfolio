import json

file_path = '/Users/arthurdhonneur/Desktop/Athenee/athenee_hf_pflio/target_pflio.ipynb'
with open(file_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)
