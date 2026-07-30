import json

with open('target_pflio.ipynb', 'r') as f:
    nb = json.load(f)

source = "".join(nb['cells'][13]['source'])

target = """    card_template = f\"\"\"
\\begin{tcolorbox}[colback=cardbg, colframe=cardborder, boxrule=0.5pt, arc=4pt, left=6pt, right=6pt, top=6pt, bottom=6pt]
    \\textbf{\\textcolor{primary}{{{escape_latex(fund_name_display)}}}} \\hfill \\textbf{\\textcolor{accent}{{{alloc_str}}}} \\\\[4pt]
    \\textcolor{primary}{{{desc}}}
\\end{tcolorbox}
\"\"\""""

target_rep = """    card_template = f\"\"\"
\\begin{tcolorbox}[colback=cardbg, colframe=cardborder, boxrule=0.5pt, arc=2pt, left=2pt, right=2pt, top=2pt, bottom=2pt]
    \\textbf{\\textcolor{primary}{{{escape_latex(fund_name_display)}}}} \\hfill \\textbf{\\textcolor{accent}{{{alloc_str}}}} \\\\[2pt]
    \\textcolor{primary}{{\\scriptsize {desc}}}
\\end{tcolorbox}
\"\"\""""

if target in source:
    source = source.replace(target, target_rep)
    print("Replaced target")
else:
    print("Could not find target, trying backup...")
    
    # Try replacing line by line
    source = source.replace("arc=4pt, left=6pt, right=6pt, top=6pt, bottom=6pt", "arc=2pt, left=2pt, right=2pt, top=2pt, bottom=2pt")
    source = source.replace("\\\\[4pt]", "\\\\[2pt]")
    source = source.replace("\\textcolor{primary}{{{desc}}}", "\\textcolor{primary}{{\\scriptsize {desc}}}")
    print("Used line-by-line replace")

lines = []
for line in source.split('\n'):
    lines.append(line + '\n')
if not source.endswith('\n'):
    lines[-1] = lines[-1][:-1]

nb['cells'][13]['source'] = lines

with open('target_pflio.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)
