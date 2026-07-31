import json

with open('target_pflio.ipynb') as f:
    nb = json.load(f)

# Update cell 9
cell9_source = ''.join(nb['cells'][9]['source'])
old_call = 'plot_yearly_returns_interactive(df_worst, "(Since 2022, Selected Funds)", start_date="2022-01-01")'
new_call = 'plot_yearly_returns_interactive(df_worst, "(Since 2022, Selected Funds)", start_date="2022-01-01", save_path="report/yearly_returns_all_funds.pdf")'
cell9_source = cell9_source.replace(old_call, new_call)

# Update cell 15
cell15_source = ''.join(nb['cells'][15]['source'])
cell15_source = cell15_source.replace('yearly_returns_6m_reb.pdf', 'yearly_returns_all_funds.pdf')

def to_list_of_lines(s):
    lines = s.split('\n')
    return [line + '\n' for line in lines[:-1]] + [lines[-1]] if lines[-1] != '' else [line + '\n' for line in lines[:-1]]
    
nb['cells'][9]['source'] = to_list_of_lines(cell9_source)
nb['cells'][15]['source'] = to_list_of_lines(cell15_source)

with open('target_pflio.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)

print("Updates applied successfully.")
