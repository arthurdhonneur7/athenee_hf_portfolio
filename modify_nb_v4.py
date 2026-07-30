import json
import re

with open("target_pflio.ipynb") as f:
    nb = json.load(f)

for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        source = "".join(cell["source"])
        
        # Modify Correlation matrix plot sizes
        if "correlation.pdf" in source and "sns.heatmap" in source:
            source = source.replace("plt.figure(figsize=(16, 12))", "plt.figure(figsize=(26, 20))")
            source = source.replace("annot_kws={\"size\": 14}", "annot_kws={\"size\": 22}")
            source = source.replace("plt.xticks(fontsize=16,", "plt.xticks(fontsize=22,")
            source = source.replace("plt.yticks(fontsize=16,", "plt.yticks(fontsize=22,")
            source = source.replace("fontsize=24", "fontsize=34")
            
        # Modify LaTeX block
        if "latex_template = r\"\"\"" in source:
            source = re.sub(
                r'(\\includegraphics\[width=0\.95\\textwidth, height=)[0-9.]+(\\textheight, keepaspectratio\]\{correlation\.pdf\})',
                r'\g<1>0.45\g<2>',
                source
            )

        if cell["source"] != source:
            # Update the cell source if changed
            cell["source"] = [line + ("\n" if not line.endswith("\n") else "") for line in source.split("\n")][:-1]
            if not cell["source"]:
                cell["source"] = [""]

with open("target_pflio.ipynb", "w") as f:
    json.dump(nb, f, indent=1)
