import json

with open("target_pflio.ipynb", "r") as f:
    nb = json.load(f)

for cell in nb.get("cells", []):
    if cell.get("cell_type") == "code":
        source = cell.get("source", [])
        new_source = []
        for line in source:
            if "alpha = model.params['const'] * 12\n" in line:
                new_source.append("    alpha = model.params['const'] * 12\n")
                new_source.append("    alpha_t = model.tvalues['const']\n")
            elif "beta = model.params['sp500']\n" in line:
                new_source.append("    beta = model.params['sp500']\n")
            elif "beta_t = model.tvalues['sp500']\n" in line:
                continue
            elif "'Alpha': f\"{alpha:.2%}\" if pd.notna(alpha) else \"-\",\n" in line:
                new_source.append("        'Alpha (t-stat)': f\"{alpha:.2%} ({alpha_t:.2f})\" if pd.notna(alpha) else \"-\",\n")
            elif "'Beta (t-stat)': f\"{beta:.2f} ({beta_t:.2f})\" if pd.notna(beta) else \"-\",\n" in line:
                new_source.append("        'Beta': f\"{beta:.2f}\" if pd.notna(beta) else \"-\",\n")
            elif "& \\textbf{Alpha} & \\textbf{Beta (t-stat)}" in line:
                line = line.replace("& \\textbf{Alpha} & \\textbf{Beta (t-stat)}", "& \\textbf{Alpha (t-stat)} & \\textbf{Beta}")
                new_source.append(line)
            else:
                new_source.append(line)
        cell["source"] = new_source

with open("target_pflio.ipynb", "w") as f:
    json.dump(nb, f, indent=1)
