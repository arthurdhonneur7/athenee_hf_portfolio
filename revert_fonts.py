import json

with open('target_pflio.ipynb', 'r') as f:
    nb = json.load(f)

source = "".join(nb['cells'][13]['source'])

# 1. Revert latex_funds_stats
if '\\renewcommand{\\arraystretch}{1.1}\n\\tiny\n\\setlength{\\tabcolsep}{2pt}\n\\begin{tabularx}{\\textwidth}' in source:
    source = source.replace(
        '\\renewcommand{\\arraystretch}{1.1}\n\\tiny\n\\setlength{\\tabcolsep}{2pt}\n\\begin{tabularx}{\\textwidth}',
        '\\renewcommand{\\arraystretch}{1.3}\n\\scriptsize\n\\begin{tabularx}{\\textwidth}'
    )
    print("Reverted latex_funds_stats")
else:
    print("Could not find latex_funds_stats to revert")

# 2. Revert card_template
current_card = '''    card_template = f"""
\\begin{{tcolorbox}}[colback=cardbg, colframe=cardborder, boxrule=0.5pt, arc=2pt, left=2pt, right=2pt, top=2pt, bottom=2pt]
    \\textbf{{\\textcolor{{primary}}{{{escape_latex(fund_name_display)}}}}} \\hfill \\textbf{{\\textcolor{{accent}}{{{alloc_str}}}}} \\\\[2pt]
    \\textcolor{{primary}}{{\\\\tiny {desc}}}
\\end{{tcolorbox}}
"""'''

original_card = '''    card_template = f"""
\\begin{{tcolorbox}}[colback=cardbg, colframe=cardborder, boxrule=0.5pt, arc=4pt, left=6pt, right=6pt, top=6pt, bottom=6pt]
    \\textbf{{\\textcolor{{primary}}{{{escape_latex(fund_name_display)}}}}} \\hfill \\textbf{{\\textcolor{{accent}}{{{alloc_str}}}}} \\\\[4pt]
    \\textcolor{{primary}}{{{desc}}}
\\end{{tcolorbox}}
"""'''

if current_card in source:
    source = source.replace(current_card, original_card)
    print("Reverted card_template")
else:
    print("Could not find card_template to revert")

# 3. Revert Fund Allocation section
current_section = r'''\section*{Fund Allocation \& Strategy Descriptions}

""" + latex_fund_descriptions + r"""

\vspace{1em}
\section*{Detailed Fund Statistics}
""" + latex_funds_stats + r"""
\clearpage'''

original_section = r'''\section*{Fund Allocation \& Strategy Descriptions}
The table below highlights the initial capital allocation weights alongside a brief description of each underlying fund's distinct edge and methodology.

""" + latex_fund_descriptions + r"""
\clearpage

\section*{Detailed Fund Statistics}
""" + latex_funds_stats + r"""
\clearpage'''

if current_section in source:
    source = source.replace(current_section, original_section)
    print("Reverted Fund Allocation section")
else:
    print("Could not find Fund Allocation section to revert")

lines = []
for line in source.split('\n'):
    lines.append(line + '\n')
if not source.endswith('\n'):
    lines[-1] = lines[-1][:-1]

nb['cells'][13]['source'] = lines

with open('target_pflio.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)
