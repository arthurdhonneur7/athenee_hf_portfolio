import json
import re

with open('target_pflio.ipynb', 'r') as f:
    nb = json.load(f)

source = "".join(nb['cells'][13]['source'])

source = source.replace("arc=2pt, left=2pt, right=2pt, top=2pt, bottom=2pt", "arc=4pt, left=6pt, right=6pt, top=6pt, bottom=6pt")
source = source.replace("\\\\[2pt]", "\\\\[4pt]")
source = source.replace("\\textcolor{primary}{{\\tiny {desc}}}", "\\textcolor{primary}{{{desc}}}")

lines = []
for line in source.split('\n'):
    lines.append(line + '\n')
if not source.endswith('\n'):
    lines[-1] = lines[-1][:-1]

nb['cells'][13]['source'] = lines

with open('target_pflio.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)

print("Reverted card_template with simple replace")
