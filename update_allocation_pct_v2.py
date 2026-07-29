import json

file_path = '/Users/arthurdhonneur/Desktop/Athenee/athenee_hf_pflio/target_pflio.ipynb'
with open(file_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb.get('cells', []):
    if cell.get('cell_type') == 'code':
        source = cell.get('source', [])
        new_source = []
        for line in source:
            if 'alloc_pct = (alloc_val / sum(allocs.values())) * 100' in line:
                # Revert to standard 2 lines if we messed up earlier
                new_source.append('    alloc_pct = (alloc_val / sum(allocs.values())) * 100 if sum(allocs.values()) > 0 else 0\n')
                new_source.append('    alloc_str = escape_latex(f"{alloc_pct:.1f}%") if alloc_val else ""\n')
            else:
                new_source.append(line)
        cell['source'] = new_source

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)
