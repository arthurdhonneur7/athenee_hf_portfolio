import json

with open('target_pflio.ipynb', 'r') as f:
    nb = json.load(f)

source = "".join(nb['cells'][13]['source'])

if '\\renewcommand{\\arraystretch}{1.3}\n\\scriptsize\n\\begin{tabularx}{\\textwidth}' in source:
    source = source.replace(
        '\\renewcommand{\\arraystretch}{1.3}\n\\scriptsize\n\\begin{tabularx}{\\textwidth}',
        '\\renewcommand{\\arraystretch}{1.5}\n\\footnotesize\n\\begin{tabularx}{\\textwidth}'
    )
    print("Replaced scriptsize with footnotesize and arraystretch 1.5 in latex_funds_stats")
elif '\\scriptsize\n\\begin{tabularx}{\\textwidth}' in source:
    # Just in case arraystretch is missing or different
    source = source.replace(
        '\\scriptsize\n\\begin{tabularx}{\\textwidth}',
        '\\footnotesize\n\\begin{tabularx}{\\textwidth}'
    )
    print("Replaced scriptsize with footnotesize")
else:
    print("Could not find the target string to replace")

lines = []
for line in source.split('\n'):
    lines.append(line + '\n')
if not source.endswith('\n'):
    lines[-1] = lines[-1][:-1]

nb['cells'][13]['source'] = lines

with open('target_pflio.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)
