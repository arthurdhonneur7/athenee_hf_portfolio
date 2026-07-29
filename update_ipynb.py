import json

file_path = '/Users/arthurdhonneur/Desktop/Athenee/athenee_hf_pflio/target_pflio.ipynb'
with open(file_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb.get('cells', []):
    if cell.get('cell_type') == 'code':
        source = cell.get('source', [])
        for i, line in enumerate(source):
            # Change 1: more space between the title and the executive summary
            if "{\\Huge \\bfseries \\color{accent} Athenee Lazarus Alpha AMC}" in line:
                if "\\\\[1.5em]" not in line:
                    source[i] = line.replace("{\\Huge \\bfseries \\color{accent} Athenee Lazarus Alpha AMC}", "{\\Huge \\bfseries \\color{accent} Athenee Lazarus Alpha AMC}\\\\[2.5em]")
            
            # Change 2: make sure that after the fund allocation & strategy descriptions we go to a new page
            if '""" + latex_fund_descriptions + r"""' in line:
                if "\\clearpage" not in line:
                    source[i] = line.replace('""" + latex_fund_descriptions + r"""', '""" + latex_fund_descriptions + r"""\n\\clearpage')
                    
            # Change 3: make sure that the detailed fund statistics only show the table and then we go to a next page
            if '""" + latex_funds_stats + r"""' in line:
                if "\\clearpage" not in line:
                    source[i] = line.replace('""" + latex_funds_stats + r"""', '""" + latex_funds_stats + r"""\n\\clearpage')
                    
            # Change 5: last page should be the comparison of the portfolio computation methods
            if "%% PAGE 3: Portfolio Backtest Methodologies" in line:
                source[i] = line.replace("%% PAGE 3: Portfolio Backtest Methodologies", "%% LAST PAGE: Portfolio Backtest Methodologies")

        cell['source'] = source

with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f)
