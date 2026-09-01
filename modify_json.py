import json

with open("target_pflio.ipynb", "r", encoding="utf-8") as f:
    data = json.load(f)

for c in data.get("cells", []):
    if c.get("cell_type") == "code":
        src = c.get("source", [])
        new_src = []
        i = 0
        while i < len(src):
            line = src[i]
            
            # 1. Return matrix start
            if "latex_monthly = " in line and "begin{table}" in line:
                # replace lines i to i+3
                new_src.extend([
                    "latex_monthly = r\"\"\"\\begin{tcolorbox}[colback=white, colframe=primary, title=\\textbf{\\large Historical net monthly returns of the selected Hedge Fund basket}, fonttitle=\\sffamily\\bfseries\\large, arc=6pt, boxrule=1pt, toptitle=6pt, bottomtitle=6pt, left=4pt, right=4pt, top=0pt, bottom=0pt, colbacktitle=primary, halign title=center]\n",
                    "\\renewcommand{\\arraystretch}{1.3}\n",
                    "\\begin{tabularx}{\\textwidth}{l *{13}{>{\\centering\\arraybackslash}X}}\n"
                ])
                i += 4  # skip the 4 old lines
                continue
            
            # 2. Return matrix end
            if "latex_monthly +=" in line and "bottomrule" in line and i+2 < len(src) and "end{table}" in src[i+2]:
                new_src.extend([
                    "latex_monthly += r\"\"\"\\bottomrule\n",
                    "\\end{tabularx}\n",
                    "\\end{tcolorbox}\"\"\"\n"
                ])
                i += 3
                continue

            # 3. Top four boxes style and vfill
            if "\\begin{minipage}[t]{0.24\\textwidth}" in line and i+1 < len(src) and "\\begin{tcolorbox}[colback=primary" in src[i+1]:
                # We want to replace the whole 4-box block + some newlines
                # Just replace until we hit the latex_strat_stats line
                new_boxes = [
                    "\\begin{minipage}[t]{0.24\\textwidth}\n",
                    "\\begin{tcolorbox}[colback=white, colframe=primary, title=\\textbf{\\large Diversified}, fonttitle=\\sffamily\\bfseries\\large, arc=6pt, boxrule=1pt, toptitle=6pt, bottomtitle=6pt, left=0pt, right=0pt, top=6pt, bottom=6pt, colbacktitle=primary, halign title=center]\n",
                    "    \\centering \\footnotesize \\textcolor{primary}{10-15 strategies}\n",
                    "\\end{tcolorbox}\n",
                    "\\end{minipage}\\hfill\n",
                    "\\begin{minipage}[t]{0.24\\textwidth}\n",
                    "\\begin{tcolorbox}[colback=white, colframe=primary, title=\\textbf{\\large Return}, fonttitle=\\sffamily\\bfseries\\large, arc=6pt, boxrule=1pt, toptitle=6pt, bottomtitle=6pt, left=0pt, right=0pt, top=6pt, bottom=6pt, colbacktitle=primary, halign title=center]\n",
                    "    \\centering \\footnotesize \\textcolor{primary}{20\\% Net Target}\n",
                    "\\end{tcolorbox}\n",
                    "\\end{minipage}\\hfill\n",
                    "\\begin{minipage}[t]{0.24\\textwidth}\n",
                    "\\begin{tcolorbox}[colback=white, colframe=primary, title=\\textbf{\\large Volatility}, fonttitle=\\sffamily\\bfseries\\large, arc=6pt, boxrule=1pt, toptitle=6pt, bottomtitle=6pt, left=0pt, right=0pt, top=6pt, bottom=6pt, colbacktitle=primary, halign title=center]\n",
                    "    \\centering \\footnotesize \\textcolor{primary}{5\\% Target}\n",
                    "\\end{tcolorbox}\n",
                    "\\end{minipage}\\hfill\n",
                    "\\begin{minipage}[t]{0.24\\textwidth}\n",
                    "\\begin{tcolorbox}[colback=white, colframe=primary, title=\\textbf{\\large Risk Control}, fonttitle=\\sffamily\\bfseries\\large, arc=6pt, boxrule=1pt, toptitle=6pt, bottomtitle=6pt, left=0pt, right=0pt, top=6pt, bottom=6pt, colbacktitle=primary, halign title=center]\n",
                    "    \\centering \\footnotesize \\textcolor{primary}{5\\% Max DD}\n",
                    "\\end{tcolorbox}\n",
                    "\\end{minipage}\n",
                    "\n",
                    "\\vspace{0.5em}\n",
                    "\n",
                    "\"\"\" + latex_monthly + r\"\"\"\n",
                    "\n",
                    "\\vfill\n",
                    "\n",
                    "\"\"\" + latex_strat_stats + r\"\"\"\n"
                ]
                new_src.extend(new_boxes)
                # Skip lines until we pass latex_strat_stats
                while i < len(src) and "\"\"\" + latex_strat_stats + r\"\"\"" not in src[i]:
                    i += 1
                i += 1 # skip the latex_strat_stats line itself
                continue

            new_src.append(line)
            i += 1
        c["source"] = new_src

with open("target_pflio.ipynb", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=1, ensure_ascii=False)
