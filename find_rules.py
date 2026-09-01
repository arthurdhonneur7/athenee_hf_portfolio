import json

with open("target_pflio.ipynb", "r", encoding="utf-8") as f:
    data = json.load(f)

for c in data.get("cells", []):
    if c.get("cell_type") == "code":
        src = c.get("source", [])
        for line in src:
            if "toprule" in line or "bottomrule" in line:
                print(repr(line))
