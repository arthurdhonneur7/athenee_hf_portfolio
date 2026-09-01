import json
with open("target_pflio.ipynb", "r", encoding="utf-8") as f:
    data = json.load(f)

for c in data.get("cells", []):
    if c.get("cell_type") == "code":
        src = c.get("source", [])
        for i, line in enumerate(src):
            if "latex_monthly =" in line and "begin{table}" in line:
                print("FOUND TABLE START at", i)
                for j in range(i, i+5): print(repr(src[j]))
