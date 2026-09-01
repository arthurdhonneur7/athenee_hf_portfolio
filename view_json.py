import json
with open("target_pflio.ipynb", "r", encoding="utf-8") as f:
    data = json.load(f)

for c in data.get("cells", []):
    if c.get("cell_type") == "code":
        src = c.get("source", [])
        for i, line in enumerate(src):
            if "latex_monthly = " in line:
                print("FOUND at", i, repr(line))
                print("NEXT:", repr(src[i+1]))
            if "Diversified" in line and "textbf" in line:
                print("FOUND Diversified at", i, repr(line))
