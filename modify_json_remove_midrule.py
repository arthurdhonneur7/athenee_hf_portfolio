import json

with open("target_pflio.ipynb", "r", encoding="utf-8") as f:
    data = json.load(f)

for c in data.get("cells", []):
    if c.get("cell_type") == "code":
        src = c.get("source", [])
        new_src = []
        in_latex_monthly = False
        
        for line in src:
            if "latex_monthly = " in line and "begin{tcolorbox}" in line:
                in_latex_monthly = True
                new_src.append(line)
                continue
            
            if "latex_funds_stats =" in line or "latex_strat_stats =" in line:
                in_latex_monthly = False
                
            if in_latex_monthly and line == "\\midrule\n":
                # Skip midrule in latex_monthly
                continue
                
            new_src.append(line)
        c["source"] = new_src

with open("target_pflio.ipynb", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=1, ensure_ascii=False)
