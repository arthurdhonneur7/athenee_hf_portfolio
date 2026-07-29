import json

file_path = '/Users/arthurdhonneur/Desktop/Athenee/athenee_hf_pflio/target_pflio.ipynb'
with open(file_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb.get('cells', []):
    if cell.get('cell_type') == 'code':
        source = cell.get('source', [])
        for i, line in enumerate(source):
            if "alloc_val = allocs.get(fund, 0)" in line:
                # We need to insert total_alloc = sum(allocs.values()) before the loop.
                # Actually, just computing it on the fly or looking back. 
                # Let's replace the alloc_str line.
                pass
            
            if 'alloc_str = escape_latex(f"{alloc_val*100:.1f}%") if alloc_val else ""' in line:
                source[i] = line.replace('alloc_str = escape_latex(f"{alloc_val*100:.1f}%") if alloc_val else ""', 'alloc_pct = (alloc_val / sum(allocs.values())) * 100 if sum(allocs.values()) > 0 else 0\\n    alloc_str = escape_latex(f"{alloc_pct:.1f}%") if alloc_val else ""')

        cell['source'] = source

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1)
