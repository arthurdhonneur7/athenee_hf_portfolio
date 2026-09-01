with open("target_pflio.ipynb", "r", encoding="utf-8") as f:
    text = f.read()

# 1. Email fix
text = text.replace(
    '\\\\textbf{\\\\textcolor{primary}{E-mail}} & \\\\small \\\\href{mailto:arthur.dhonneur@athenee-investment.com}',
    '\\\\textbf{\\\\textcolor{primary}{E-mail}} & \\\\href{mailto:arthur.dhonneur@athenee-investment.com}'
)

# 2. Return matrix style
text = text.replace(
    'latex_monthly = r\"\"\"\\begin{table}[h]\\n\",\n    \"\\centering\\n\",\n    \"\\renewcommand{\\arraystretch}{1.3}\\n\",\n    \"\\begin{tabularx}{\\textwidth}{l *{13}{>{\\centering\\arraybackslash}X}}\\n\",\n',
    'latex_monthly = r\"\"\"\\begin{tcolorbox}[colback=white, colframe=primary, title=\\textbf{\\large Historical net monthly returns of the selected Hedge Fund basket}, fonttitle=\\sffamily\\bfseries\\large, arc=6pt, boxrule=1pt, toptitle=6pt, bottomtitle=6pt, left=4pt, right=4pt, top=0pt, bottom=0pt, colbacktitle=primary, halign title=center]\\n\",\n    \"\\renewcommand{\\arraystretch}{1.3}\\n\",\n    \"\\begin{tabularx}{\\textwidth}{l *{13}{>{\\centering\\arraybackslash}X}}\\n\",\n'
)

text = text.replace(
    'latex_monthly += r\"\"\"\\bottomrule\\n\",\n    \"\\end{tabularx}\\n\",\n    \"\\end{table}\"\"\"\\n\",',
    'latex_monthly += r\"\"\"\\bottomrule\\n\",\n    \"\\end{tabularx}\\n\",\n    \"\\end{tcolorbox}\"\"\"\\n\",'
)

# 3. Top four boxes style and vfill
old_boxes = '''    "\\begin{minipage}[t]{0.24\\textwidth}\\n",
    "\\begin{tcolorbox}[colback=primary, colframe=primary, boxrule=0pt, arc=4pt, left=2pt, right=2pt, top=6pt, bottom=6pt, coltext=white]\\n",
    "    \\centering \\large \\textbf{Diversified} \\\\[4pt]\\n",
    "    \\footnotesize 10-15 strategies\\n",
    "\\end{tcolorbox}\\n",
    "\\end{minipage}\\hfill\\n",
    "\\begin{minipage}[t]{0.24\\textwidth}\\n",
    "\\begin{tcolorbox}[colback=primary, colframe=primary, boxrule=0pt, arc=4pt, left=2pt, right=2pt, top=6pt, bottom=6pt, coltext=white]\\n",
    "    \\centering \\large \\textbf{Return} \\\\[4pt]\\n",
    "    \\footnotesize 20\\\\% Net Target\\n",
    "\\end{tcolorbox}\\n",
    "\\end{minipage}\\hfill\\n",
    "\\begin{minipage}[t]{0.24\\textwidth}\\n",
    "\\begin{tcolorbox}[colback=primary, colframe=primary, boxrule=0pt, arc=4pt, left=2pt, right=2pt, top=6pt, bottom=6pt, coltext=white]\\n",
    "    \\centering \\large \\textbf{Volatility} \\\\[4pt]\\n",
    "    \\footnotesize 5\\\\% Target\\n",
    "\\end{tcolorbox}\\n",
    "\\end{minipage}\\hfill\\n",
    "\\begin{minipage}[t]{0.24\\textwidth}\\n",
    "\\begin{tcolorbox}[colback=primary, colframe=primary, boxrule=0pt, arc=4pt, left=2pt, right=2pt, top=6pt, bottom=6pt, coltext=white]\\n",
    "    \\centering \\large \\textbf{Risk Control} \\\\[4pt]\\n",
    "    \\footnotesize 5\\\\% Max DD\\n",
    "\\end{tcolorbox}\\n",
    "\\end{minipage}\\n",
    "\\n",
    "\\vspace{0.25em}\\n",
    "\\n",
    "\\subsection*{Historical net monthly returns of the selected Hedge Fund basket}\\n",
    "\"\"\" + latex_monthly + r\"\"\"\\n",
    "\\n",
    "\\n",
    "\"\"\" + latex_strat_stats + r\"\"\"\\n"'''

new_boxes = '''    "\\begin{minipage}[t]{0.24\\textwidth}\\n",
    "\\begin{tcolorbox}[colback=white, colframe=primary, title=\\textbf{\\large Diversified}, fonttitle=\\sffamily\\bfseries\\large, arc=6pt, boxrule=1pt, toptitle=6pt, bottomtitle=6pt, left=0pt, right=0pt, top=6pt, bottom=6pt, colbacktitle=primary, halign title=center]\\n",
    "    \\centering \\footnotesize \\textcolor{primary}{10-15 strategies}\\n",
    "\\end{tcolorbox}\\n",
    "\\end{minipage}\\hfill\\n",
    "\\begin{minipage}[t]{0.24\\textwidth}\\n",
    "\\begin{tcolorbox}[colback=white, colframe=primary, title=\\textbf{\\large Return}, fonttitle=\\sffamily\\bfseries\\large, arc=6pt, boxrule=1pt, toptitle=6pt, bottomtitle=6pt, left=0pt, right=0pt, top=6pt, bottom=6pt, colbacktitle=primary, halign title=center]\\n",
    "    \\centering \\footnotesize \\textcolor{primary}{20\\\\% Net Target}\\n",
    "\\end{tcolorbox}\\n",
    "\\end{minipage}\\hfill\\n",
    "\\begin{minipage}[t]{0.24\\textwidth}\\n",
    "\\begin{tcolorbox}[colback=white, colframe=primary, title=\\textbf{\\large Volatility}, fonttitle=\\sffamily\\bfseries\\large, arc=6pt, boxrule=1pt, toptitle=6pt, bottomtitle=6pt, left=0pt, right=0pt, top=6pt, bottom=6pt, colbacktitle=primary, halign title=center]\\n",
    "    \\centering \\footnotesize \\textcolor{primary}{5\\\\% Target}\\n",
    "\\end{tcolorbox}\\n",
    "\\end{minipage}\\hfill\\n",
    "\\begin{minipage}[t]{0.24\\textwidth}\\n",
    "\\begin{tcolorbox}[colback=white, colframe=primary, title=\\textbf{\\large Risk Control}, fonttitle=\\sffamily\\bfseries\\large, arc=6pt, boxrule=1pt, toptitle=6pt, bottomtitle=6pt, left=0pt, right=0pt, top=6pt, bottom=6pt, colbacktitle=primary, halign title=center]\\n",
    "    \\centering \\footnotesize \\textcolor{primary}{5\\\\% Max DD}\\n",
    "\\end{tcolorbox}\\n",
    "\\end{minipage}\\n",
    "\\n",
    "\\vspace{0.5em}\\n",
    "\\n",
    "\"\"\" + latex_monthly + r\"\"\"\\n",
    "\\n",
    "\\vfill\\n",
    "\\n",
    "\"\"\" + latex_strat_stats + r\"\"\"\\n"'''

text = text.replace(old_boxes, new_boxes)

with open("target_pflio.ipynb", "w", encoding="utf-8") as f:
    f.write(text)
