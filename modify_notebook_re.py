import re

with open("target_pflio.ipynb", "r", encoding="utf-8") as f:
    text = f.read()

# 2. Return matrix style
text = re.sub(
    r'latex_monthly = r"""\\begin{table}\[h\]\\n",\n\s*"\\centering\\n",\n\s*"\\renewcommand{\\arraystretch}{1\.3}\\n",\n\s*"\\begin{tabularx}{\\textwidth}',
    r'latex_monthly = r"""\\begin{tcolorbox}[colback=white, colframe=primary, title=\\textbf{\\large Historical net monthly returns of the selected Hedge Fund basket}, fonttitle=\\sffamily\\bfseries\\large, arc=6pt, boxrule=1pt, toptitle=6pt, bottomtitle=6pt, left=4pt, right=4pt, top=0pt, bottom=0pt, colbacktitle=primary, halign title=center]\\n",\n    "\\renewcommand{\\arraystretch}{1.3}\\n",\n    "\\begin{tabularx}{\\textwidth}',
    text
)

text = re.sub(
    r'latex_monthly \+= r"""\\bottomrule\\n",\n\s*"\\end{tabularx}\\n",\n\s*"\\end{table}"""\\n"',
    r'latex_monthly += r"""\\bottomrule\\n",\n    "\\end{tabularx}\\n",\n    "\\end{tcolorbox}"""\\n"',
    text
)

# 3. Top four boxes style and vfill
old_boxes_re = r'"\\begin{minipage}\[t\]{0\.24\\textwidth}\\n",\n\s*"\\begin{tcolorbox}\[colback=primary, colframe=primary, boxrule=0pt, arc=4pt, left=2pt, right=2pt, top=6pt, bottom=6pt, coltext=white\]\\n",\n\s*"\\s*\\centering \\large \\textbf{Diversified} \\\\\[4pt\]\\n",\n\s*"\\s*\\footnotesize 10-15 strategies\\n",\n\s*"\\end{tcolorbox}\\n",\n\s*"\\end{minipage}\\\\hfill\\n",\n\s*"\\begin{minipage}\[t\]{0\.24\\textwidth}\\n",\n\s*"\\begin{tcolorbox}\[colback=primary, colframe=primary, boxrule=0pt, arc=4pt, left=2pt, right=2pt, top=6pt, bottom=6pt, coltext=white\]\\n",\n\s*"\\s*\\centering \\large \\textbf{Return} \\\\\[4pt\]\\n",\n\s*"\\s*\\footnotesize 20\\\\% Net Target\\n",\n\s*"\\end{tcolorbox}\\n",\n\s*"\\end{minipage}\\\\hfill\\n",\n\s*"\\begin{minipage}\[t\]{0\.24\\textwidth}\\n",\n\s*"\\begin{tcolorbox}\[colback=primary, colframe=primary, boxrule=0pt, arc=4pt, left=2pt, right=2pt, top=6pt, bottom=6pt, coltext=white\]\\n",\n\s*"\\s*\\centering \\large \\textbf{Volatility} \\\\\[4pt\]\\n",\n\s*"\\s*\\footnotesize 5\\\\% Target\\n",\n\s*"\\end{tcolorbox}\\n",\n\s*"\\end{minipage}\\\\hfill\\n",\n\s*"\\begin{minipage}\[t\]{0\.24\\textwidth}\\n",\n\s*"\\begin{tcolorbox}\[colback=primary, colframe=primary, boxrule=0pt, arc=4pt, left=2pt, right=2pt, top=6pt, bottom=6pt, coltext=white\]\\n",\n\s*"\\s*\\centering \\large \\textbf{Risk Control} \\\\\[4pt\]\\n",\n\s*"\\s*\\footnotesize 5\\\\% Max DD\\n",\n\s*"\\end{tcolorbox}\\n",\n\s*"\\end{minipage}\\n",\n\s*"\\n",\n\s*"\\vspace{0\.25em}\\n",\n\s*"\\n",\n\s*"\\subsection\*{Historical net monthly returns of the selected Hedge Fund basket}\\n",\n\s*"\"\"\" \+ latex_monthly \+ r\"\"\"\\n",\n\s*"\\n",\n\s*"\\n",\n\s*"\"\"\" \+ latex_strat_stats \+ r\"\"\"\\n"'

new_boxes = '''    "\\\\begin{minipage}[t]{0.24\\\\textwidth}\\n",
    "\\\\begin{tcolorbox}[colback=white, colframe=primary, title=\\\\textbf{\\\\large Diversified}, fonttitle=\\\\sffamily\\\\bfseries\\\\large, arc=6pt, boxrule=1pt, toptitle=6pt, bottomtitle=6pt, left=0pt, right=0pt, top=6pt, bottom=6pt, colbacktitle=primary, halign title=center]\\n",
    "    \\\\centering \\\\footnotesize \\\\textcolor{primary}{10-15 strategies}\\n",
    "\\\\end{tcolorbox}\\n",
    "\\\\end{minipage}\\\\hfill\\n",
    "\\\\begin{minipage}[t]{0.24\\\\textwidth}\\n",
    "\\\\begin{tcolorbox}[colback=white, colframe=primary, title=\\\\textbf{\\\\large Return}, fonttitle=\\\\sffamily\\\\bfseries\\\\large, arc=6pt, boxrule=1pt, toptitle=6pt, bottomtitle=6pt, left=0pt, right=0pt, top=6pt, bottom=6pt, colbacktitle=primary, halign title=center]\\n",
    "    \\\\centering \\\\footnotesize \\\\textcolor{primary}{20\\\\% Net Target}\\n",
    "\\\\end{tcolorbox}\\n",
    "\\\\end{minipage}\\\\hfill\\n",
    "\\\\begin{minipage}[t]{0.24\\\\textwidth}\\n",
    "\\\\begin{tcolorbox}[colback=white, colframe=primary, title=\\\\textbf{\\\\large Volatility}, fonttitle=\\\\sffamily\\\\bfseries\\\\large, arc=6pt, boxrule=1pt, toptitle=6pt, bottomtitle=6pt, left=0pt, right=0pt, top=6pt, bottom=6pt, colbacktitle=primary, halign title=center]\\n",
    "    \\\\centering \\\\footnotesize \\\\textcolor{primary}{5\\\\% Target}\\n",
    "\\\\end{tcolorbox}\\n",
    "\\\\end{minipage}\\\\hfill\\n",
    "\\\\begin{minipage}[t]{0.24\\\\textwidth}\\n",
    "\\\\begin{tcolorbox}[colback=white, colframe=primary, title=\\\\textbf{\\\\large Risk Control}, fonttitle=\\\\sffamily\\\\bfseries\\\\large, arc=6pt, boxrule=1pt, toptitle=6pt, bottomtitle=6pt, left=0pt, right=0pt, top=6pt, bottom=6pt, colbacktitle=primary, halign title=center]\\n",
    "    \\\\centering \\\\footnotesize \\\\textcolor{primary}{5\\\\% Max DD}\\n",
    "\\\\end{tcolorbox}\\n",
    "\\\\end{minipage}\\n",
    "\\n",
    "\\\\vspace{0.5em}\\n",
    "\\n",
    "\\"\\"\\" + latex_monthly + r\\"\\"\\"\\n",
    "\\n",
    "\\\\vfill\\n",
    "\\n",
    "\\"\\"\\" + latex_strat_stats + r\\"\\"\\"\\n"'''

text = re.sub(old_boxes_re, new_boxes.replace('\\\\', '\\'), text)

with open("target_pflio.ipynb", "w", encoding="utf-8") as f:
    f.write(text)
