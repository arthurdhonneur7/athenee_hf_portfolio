import json

with open('target_pflio.ipynb', 'r') as f:
    nb = json.load(f)

source = "".join(nb['cells'][13]['source'])

# 1. Update latex_funds_stats tabularx definition
old_funds_col = '\\begin{tabularx}{\\textwidth}{l *{12}{>{\\centering\\arraybackslash}X}}'
new_funds_col = '\\begin{tabularx}{\\textwidth}{l *{3}{>{\\centering\\arraybackslash}X} c *{8}{>{\\centering\\arraybackslash}X}}'
if old_funds_col in source:
    source = source.replace(old_funds_col, new_funds_col)
    print("Updated latex_funds_stats columns")
else:
    print("Could not find old_funds_col")

# 2. Update latex_strat_stats tabularx definition
# Note: In my previous check it was *{11} for some reason, so let's try replacing both *{11} and *{12} just in case
old_strat_col_11 = '\\begin{tabularx}{\\textwidth}{*{11}{>{\\centering\\arraybackslash}X}}'
old_strat_col_12 = '\\begin{tabularx}{\\textwidth}{*{12}{>{\\centering\\arraybackslash}X}}'
new_strat_col = '\\begin{tabularx}{\\textwidth}{*{3}{>{\\centering\\arraybackslash}X} c *{8}{>{\\centering\\arraybackslash}X}}'

if old_strat_col_11 in source:
    source = source.replace(old_strat_col_11, new_strat_col)
    print("Updated latex_strat_stats columns from *{11}")
elif old_strat_col_12 in source:
    source = source.replace(old_strat_col_12, new_strat_col)
    print("Updated latex_strat_stats columns from *{12}")
else:
    print("Could not find old_strat_col")

lines = []
for line in source.split('\n'):
    lines.append(line + '\n')
if not source.endswith('\n'):
    lines[-1] = lines[-1][:-1]

nb['cells'][13]['source'] = lines

with open('target_pflio.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)

print("Done fixing MDD column")
