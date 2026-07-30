import json

with open('target_pflio.ipynb', 'r') as f:
    nb = json.load(f)

# The mapping dictionary
qualifications_str = """
fund_qualifications = {
    'quanstream': 'Quant volatility sellers',
    'm1': 'Crypto carry trade',
    'vadantia': 'Quant FX / Metals trading',
    'arr': 'Equity trading oriented',
    'r_squared': 'Div future & Index future arbitrage',
    'shiprock': 'Distressed Debt',
    'smithson': 'Systematic multi asset',
    '26_miles': 'Quant Indian medium frequency',
    'adar1': 'Biotech focused',
    'grasshoper': 'Quant high frequency'
}
"""

# Insert at the end of cell 0
if nb['cells'][0]['cell_type'] == 'code':
    nb['cells'][0]['source'].append(qualifications_str)

for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        source = "".join(cell['source'])
        
        # 1. Replace the xticklabels replace logic
        source = source.replace(
            "[str(c).replace('_', ' ').title() for c in stats_df_sel.index]",
            "[fund_qualifications.get(str(c), 'Generic strategy') for c in stats_df_sel.index]"
        )
        
        # 2. Replace funds_names append
        source = source.replace(
            "fund_names.append(f.replace('_', ' ').title())",
            "fund_names.append(fund_qualifications.get(f, 'Generic strategy'))"
        )
        
        # 3. Replace fund_name_display in latex_fund_descriptions
        source = source.replace(
            "fund_name_display = fund.replace('_', ' ').title()",
            "fund_name_display = fund_qualifications.get(fund, 'Generic strategy')"
        )
        
        # 4. Correlation matrix rename
        if "corr_matrix_sel = df_funds_full[df_funds_full.columns.intersection(selected_funds)].corr()" in source:
            source = source.replace(
                "corr_matrix_sel = df_funds_full[df_funds_full.columns.intersection(selected_funds)].corr()\n",
                "corr_matrix_sel = df_funds_full[df_funds_full.columns.intersection(selected_funds)].corr()\ncorr_matrix_sel.rename(columns=lambda x: fund_qualifications.get(x, 'Generic strategy'), index=lambda x: fund_qualifications.get(x, 'Generic strategy'), inplace=True)\n"
            )
            
        # 5. Worst SP500 Months Plot DataFrame rename
        if "plot_worst_sp500_months_interactive(df[['sp500'] + [f for f in selected_funds if f in df.columns]]" in source:
            source = source.replace(
                "plot_worst_sp500_months_interactive(df[['sp500'] + [f for f in selected_funds if f in df.columns]]",
                "df_worst = df[['sp500'] + [f for f in selected_funds if f in df.columns]].rename(columns=lambda x: fund_qualifications.get(x, 'Generic strategy') if x != 'sp500' else 'sp500')\nplot_worst_sp500_months_interactive(df_worst"
            )
            
        # Restore as list of lines to preserve valid JSON for jupyter
        cell['source'] = [line + '\n' for line in source.split('\n')]
        # Remove trailing newline from the last element if it was artificially added by split
        if cell['source'] and cell['source'][-1] == '\n':
            cell['source'] = cell['source'][:-1]
        elif cell['source'] and cell['source'][-1].endswith('\n\n'):
             cell['source'][-1] = cell['source'][-1][:-1]

with open('target_pflio.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)
    f.write('\n')
