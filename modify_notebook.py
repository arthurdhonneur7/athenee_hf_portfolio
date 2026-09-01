import json

with open("target_pflio.ipynb", "r", encoding="utf-8") as f:
    data = json.load(f)

for cell in data.get("cells", []):
    if cell.get("cell_type") == "code":
        source = cell.get("source", [])
        new_source = []
        i = 0
        while i < len(source):
            line = source[i]
            
            # Email fix
            if "\\\\textbf{\\\\textcolor{primary}{E-mail}} & \\\\small \\\\href" in line:
                line = line.replace("\\\\small ", "")
                
            # Table start replace
            if "latex_monthly = r\"\"\"\\begin{table}[h]\\n" in line:
                if i+3 < len(source) and "\\begin{tabularx}{\\textwidth}" in source[i+3]:
                    new_source.extend([
                        "    \"latex_monthly = r\\\"\\\"\\\"\\\\begin{tcolorbox}[colback=white, colframe=primary, title=\\\\textbf{\\\\large Historical net monthly returns of the selected Hedge Fund basket}, fonttitle=\\\\sffamily\\\\bfseries\\\\large, arc=6pt, boxrule=1pt, toptitle=6pt, bottomtitle=6pt, left=4pt, right=4pt, top=0pt, bottom=0pt, colbacktitle=primary, halign title=center]\\n\",\n",
                        "    \"\\\\renewcommand{\\\\arraystretch}{1.3}\\n\",\n",
                        "    \"\\\\begin{tabularx}{\\\\textwidth}{l *{13}{>{\\\\centering\\\\arraybackslash}X}}\\n\",\n"
                    ])
                    i += 4
                    continue
            
            # Table end replace
            if "latex_monthly += r\"\"\"\\bottomrule\\n" in line:
                if i+2 < len(source) and "\\end{table}\"\"\"\\n" in source[i+2]:
                    new_source.extend([
                        "    \"latex_monthly += r\\\"\\\"\\\"\\\\bottomrule\\n\",\n",
                        "    \"\\\\end{tabularx}\\n\",\n",
                        "    \"\\\\end{tcolorbox}\\\"\\\"\\\"\\n\",\n"
                    ])
                    i += 3
                    continue

            # Top four boxes replace
            if "\\begin{minipage}[t]{0.24\\textwidth}\\n" in line and i+31 < len(source):
                if "\\begin{tcolorbox}[colback=primary, colframe=primary" in source[i+1] and "Diversified" in source[i+2]:
                    replacement = [
                        "    \"\\\\begin{minipage}[t]{0.24\\\\textwidth}\\n\",\n",
                        "    \"\\\\begin{tcolorbox}[colback=white, colframe=primary, title=\\\\textbf{\\\\large Diversified}, fonttitle=\\\\sffamily\\\\bfseries\\\\large, arc=6pt, boxrule=1pt, toptitle=6pt, bottomtitle=6pt, left=0pt, right=0pt, top=6pt, bottom=6pt, colbacktitle=primary, halign title=center]\\n\",\n",
                        "    \"    \\\\centering \\\\footnotesize \\\\textcolor{primary}{10-15 strategies}\\n\",\n",
                        "    \"\\\\end{tcolorbox}\\n\",\n",
                        "    \"\\\\end{minipage}\\\\hfill\\n\",\n",
                        "    \"\\\\begin{minipage}[t]{0.24\\\\textwidth}\\n\",\n",
                        "    \"\\\\begin{tcolorbox}[colback=white, colframe=primary, title=\\\\textbf{\\\\large Return}, fonttitle=\\\\sffamily\\\\bfseries\\\\large, arc=6pt, boxrule=1pt, toptitle=6pt, bottomtitle=6pt, left=0pt, right=0pt, top=6pt, bottom=6pt, colbacktitle=primary, halign title=center]\\n\",\n",
                        "    \"    \\\\centering \\\\footnotesize \\\\textcolor{primary}{20\\\\% Net Target}\\n\",\n",
                        "    \"\\\\end{tcolorbox}\\n\",\n",
                        "    \"\\\\end{minipage}\\\\hfill\\n\",\n",
                        "    \"\\\\begin{minipage}[t]{0.24\\\\textwidth}\\n\",\n",
                        "    \"\\\\begin{tcolorbox}[colback=white, colframe=primary, title=\\\\textbf{\\\\large Volatility}, fonttitle=\\\\sffamily\\\\bfseries\\\\large, arc=6pt, boxrule=1pt, toptitle=6pt, bottomtitle=6pt, left=0pt, right=0pt, top=6pt, bottom=6pt, colbacktitle=primary, halign title=center]\\n\",\n",
                        "    \"    \\\\centering \\\\footnotesize \\\\textcolor{primary}{5\\\\% Target}\\n\",\n",
                        "    \"\\\\end{tcolorbox}\\n\",\n",
                        "    \"\\\\end{minipage}\\\\hfill\\n\",\n",
                        "    \"\\\\begin{minipage}[t]{0.24\\\\textwidth}\\n\",\n",
                        "    \"\\\\begin{tcolorbox}[colback=white, colframe=primary, title=\\\\textbf{\\\\large Risk Control}, fonttitle=\\\\sffamily\\\\bfseries\\\\large, arc=6pt, boxrule=1pt, toptitle=6pt, bottomtitle=6pt, left=0pt, right=0pt, top=6pt, bottom=6pt, colbacktitle=primary, halign title=center]\\n\",\n",
                        "    \"    \\\\centering \\\\footnotesize \\\\textcolor{primary}{5\\\\% Max DD}\\n\",\n",
                        "    \"\\\\end{tcolorbox}\\n\",\n",
                        "    \"\\\\end{minipage}\\n\",\n",
                        "    \"\\n\",\n",
                        "    \"\\\\vspace{0.5em}\\n\",\n",
                        "    \"\\n\",\n",
                        "    \"\\\"\\\"\\\" + latex_monthly + r\\\"\\\"\\\"\\n\",\n",
                        "    \"\\n\",\n",
                        "    \"\\\\vfill\\n\",\n",
                        "    \"\\n\",\n",
                        "    \"\\\"\\\"\\\" + latex_strat_stats + r\\\"\\\"\\\"\\n\",\n"
                    ]
                    new_source.extend(replacement)
                    i += 32
                    continue
            
            new_source.append(line)
            i += 1
        
        cell["source"] = new_source

with open("target_pflio_modified.ipynb", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=1, ensure_ascii=False)
