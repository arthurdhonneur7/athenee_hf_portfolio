import json

with open("target_pflio.ipynb", "r") as f:
    nb = json.load(f)

for cell in nb.get("cells", []):
    if cell.get("cell_type") == "code":
        source = cell.get("source", [])
        new_source = []
        skip_next = 0
        for i, line in enumerate(source):
            if skip_next > 0:
                skip_next -= 1
                continue
            
            if "plt.plot(cum_p.index, cum_p, label=port_name, color='purple', linewidth=2)" in line:
                new_source[-1] = "    plt.figure(figsize=(12, 6))\n"
                new_source.append("    plt.plot(cum_p.index, cum_p, label=port_name, color='#1A365D', linewidth=3)\n")
                new_source.append("    plt.plot(cum_s.index, cum_s, label='S&P 500', color='lightgray', linewidth=2.5, linestyle='--')\n")
                new_source.append("    plt.title(f'Growth of {port_name} vs S&P 500', fontsize=14, fontweight='bold')\n")
                new_source.append("    plt.ylabel('Growth of $1', fontsize=12)\n")
                new_source.append("    plt.grid(True, linestyle='--', alpha=0.5)\n")
                new_source.append("    plt.legend(fontsize=12, loc='upper left')\n")
                new_source.append("    plt.tight_layout()\n")
                skip_next = 5  # Skip the next 5 lines from the original source
            else:
                new_source.append(line)
        cell["source"] = new_source

with open("target_pflio.ipynb", "w") as f:
    json.dump(nb, f, indent=1)
