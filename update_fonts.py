import json

with open('target_pflio.ipynb', 'r') as f:
    nb = json.load(f)

source = "".join(nb['cells'][13]['source'])

# 1. Update latex_funds_stats
old_stats = r"""latex_funds_stats = r'''\begin{table}[h]
\centering
\renewcommand{\arraystretch}{1.3}
\scriptsize
\begin{tabularx}{\textwidth}{l *{12}{>{\centering\arraybackslash}X}}
\toprule
 & \textbf{CAGR} & \textbf{Std} & \textbf{Proxy Sharpe} & \textbf{MDD} & \textbf{Calmar} & \textbf{Pos Months} & \textbf{Up Capture} & \textbf{Down Capture} & \textbf{Alpha (t-stat)} & \textbf{Beta} & \textbf{Corr SP500} & \textbf{N months}\\
\midrule
'''"""

# wait, the string has triple quotes inside raw string in python...
# Let's just do a direct string replace on the pieces

if '\\renewcommand{\\arraystretch}{1.3}\n\\scriptsize' in source:
    source = source.replace(
        '\\renewcommand{\\arraystretch}{1.3}\n\\scriptsize\n\\begin{tabularx}{\\textwidth}',
        '\\renewcommand{\\arraystretch}{1.1}\n\\tiny\n\\setlength{\\tabcolsep}{2pt}\n\\begin{tabularx}{\\textwidth}'
    )
    print("Updated latex_funds_stats")
else:
    print("Could not find exact match for latex_funds_stats replacement")

# 2. Update card_template desc
old_desc = '\\\\textcolor{{primary}}{{{desc}}}'
new_desc = '\\\\textcolor{{primary}}{{\\\\tiny {desc}}}'
if old_desc in source:
    source = source.replace(old_desc, new_desc)
    print("Updated card_template desc")
else:
    # Try looking for \scriptsize if it was replaced before
    old_desc_script = '\\\\textcolor{{primary}}{{\\\\scriptsize {desc}}}'
    if old_desc_script in source:
        source = source.replace(old_desc_script, new_desc)
        print("Updated card_template desc from scriptsize to tiny")
    else:
        print("Could not find desc in card_template")

lines = []
for line in source.split('\n'):
    lines.append(line + '\n')
if not source.endswith('\n'):
    lines[-1] = lines[-1][:-1]

nb['cells'][13]['source'] = lines

with open('target_pflio.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)
