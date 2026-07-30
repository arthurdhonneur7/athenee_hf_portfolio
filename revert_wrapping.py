import json

with open('target_pflio.ipynb', 'r') as f:
    nb = json.load(f)

source = "".join(nb['cells'][13]['source'])

# 1. Remove \setlength{\tabcolsep}{2pt} from latex_funds_stats
old_funds_pre = '\\renewcommand{\\arraystretch}{1.5}\n\\footnotesize\n\\setlength{\\tabcolsep}{2pt}\n\\begin{tabularx}{\\textwidth}'
new_funds_pre = '\\renewcommand{\\arraystretch}{1.5}\n\\footnotesize\n\\begin{tabularx}{\\textwidth}'
if old_funds_pre in source:
    source = source.replace(old_funds_pre, new_funds_pre)
    print("Reverted tabcolsep in latex_funds_stats")

# 2. Remove \setlength{\tabcolsep}{2pt} from latex_strat_stats
old_strat_pre = '\\renewcommand{\\arraystretch}{1.8}\n\\footnotesize\n\\setlength{\\tabcolsep}{2pt}\n\\begin{tabularx}{\\textwidth}'
new_strat_pre = '\\renewcommand{\\arraystretch}{1.8}\n\\footnotesize\n\\begin{tabularx}{\\textwidth}'
if old_strat_pre in source:
    source = source.replace(old_strat_pre, new_strat_pre)
    print("Reverted tabcolsep in latex_strat_stats")

# 3. Revert shortened headers in latex_funds_stats
old_headers = '\\textbf{CAGR} & \\textbf{Std} & \\textbf{Sharpe} & \\textbf{MDD} & \\textbf{Calmar} & \\textbf{Pos \\%} & \\textbf{Up Cap} & \\textbf{Down Cap} & \\textbf{Alpha} & \\textbf{Beta} & \\textbf{Corr} & \\textbf{N}'
new_headers = '\\textbf{CAGR} & \\textbf{Std} & \\textbf{Proxy Sharpe} & \\textbf{MDD} & \\textbf{Calmar} & \\textbf{Pos Months} & \\textbf{Up Capture} & \\textbf{Down Capture} & \\textbf{Alpha (t-stat)} & \\textbf{Beta} & \\textbf{Corr SP500} & \\textbf{N months}'
if old_headers in source:
    source = source.replace(old_headers, new_headers)
    print("Reverted headers")

# 4. Remove \mbox{} wrapper for values (which is present 2 times)
old_row_vals = 'row_vals = [f"\\\\mbox{{{escape_latex(str(x))}}}" for x in row.values]'
new_row_vals = 'row_vals = [escape_latex(str(x)) for x in row.values]'
if old_row_vals in source:
    source = source.replace(old_row_vals, new_row_vals)
    print("Reverted \mbox{} wrappers")

lines = []
for line in source.split('\n'):
    lines.append(line + '\n')
if not source.endswith('\n'):
    lines[-1] = lines[-1][:-1]

nb['cells'][13]['source'] = lines

with open('target_pflio.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)

print("Done reverting")
