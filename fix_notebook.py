import json

with open('target_pflio.ipynb', 'r') as f:
    nb = json.load(f)

short_names_str = """
fund_short_names = {
    'quanstream': 'Quant Vol',
    'm1': 'Crypto Carry',
    'vadantia': 'Quant FX',
    'arr': 'Equity Trading',
    'r_squared': 'Futures Arb',
    'shiprock': 'Distr Debt',
    'smithson': 'Syst Multi Asset',
    '26_miles': 'Quant Indian',
    'adar1': 'Biotech',
    'grasshoper': 'Quant HFT'
}
"""

for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        
        # Insert short names dict after qualifications
        if "fund_qualifications = {" in source and "fund_short_names = {" not in source:
            source = source + "\n" + short_names_str
            
        # Fix the worst sp500 months function
        if "cols_to_plot = ['sp500'] + [f for f in funds if f in df_plot.columns]" in source:
            source = source.replace(
                "cols_to_plot = ['sp500'] + [f for f in funds if f in df_plot.columns]",
                "cols_to_plot = ['sp500'] + [c for c in df_plot.columns if c != 'sp500']"
            )
            
        # Replace the mapping in plots and tables
        if "fund_qualifications.get" in source:
            # We want to change fund_qualifications to fund_short_names everywhere EXCEPT in latex_fund_descriptions
            lines = source.split('\n')
            new_lines = []
            for line in lines:
                if "fund_name_display = fund_qualifications.get" in line:
                    new_lines.append(line)
                elif "fund_qualifications.get" in line:
                    new_lines.append(line.replace("fund_qualifications.get", "fund_short_names.get"))
                else:
                    new_lines.append(line)
            source = "\n".join(new_lines)
            
        # Restore as list of lines
        cell['source'] = [line + '\n' for line in source.split('\n')]
        if cell['source'] and cell['source'][-1].endswith('\n\n'):
             cell['source'][-1] = cell['source'][-1][:-1]
        elif cell['source'] and cell['source'][-1] == '\n':
            cell['source'] = cell['source'][:-1]

with open('target_pflio.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)
    f.write('\n')
