import json

with open("target_pflio.ipynb", "r") as f:
    nb = json.load(f)

for cell in nb.get("cells", []):
    if cell.get("cell_type") == "code":
        source = cell.get("source", [])
        new_source = []
        for line in source:
            # 1. Growth plot
            if "plt.plot(cum_s.index, cum_s, label='S&P 500', color='lightgray', linewidth=2.5, linestyle='--')" in line:
                line = line.replace("color='lightgray'", "color='gray'").replace("linestyle='--'", "linestyle='-'")
                new_source.append(line)
            
            # 2. Scatter plot 6-month returns
            elif "plt.scatter(sp500_aligned, fund_aligned, alpha=0.7, color='steelblue')" in line:
                line = line.replace("color='steelblue'", "color='#1A365D'")
                new_source.append(line)
            elif "plt.axvline(0, color='grey', linestyle='--', linewidth=1)" in line:
                line = line.replace("color='grey'", "color='gray'")
                new_source.append(line)
            elif "plt.axhline(0, color='grey', linestyle='--', linewidth=1)" in line:
                line = line.replace("color='grey'", "color='gray'")
                new_source.append(line)
            elif "plt.plot(x_vals, y_vals, color='firebrick'" in line and "label=f\"Fit: y =" in line:
                line = line.replace("color='firebrick'", "color='#D4AF37'")
                new_source.append(line)
            
            # 3. Fund statistics plot
            elif "ax1.bar(x - width/2, stats_df_sorted[\"Annualized Mean\"], width, label='Annualized Mean', color='steelblue')" in line:
                line = line.replace("color='steelblue'", "color='#1A365D'")
                new_source.append(line)
            elif "ax1.bar(x + width/2, stats_df_sorted[\"Annualized Std\"], width, label='Annualized Std', color='firebrick')" in line:
                line = line.replace("color='firebrick'", "color='gray'")
                new_source.append(line)
            elif "ax2.plot(x, stats_df_sorted[\"Proxy Sharpe\"], color='darkgreen'" in line:
                line = line.replace("color='darkgreen'", "color='#D4AF37'")
                new_source.append(line)
            
            # 4. Correlation plot
            elif "sns.heatmap(corr_matrix, annot=True, cmap='coolwarm'" in line:
                new_source.append("    import matplotlib.colors as mcolors\n")
                new_source.append("    custom_cmap = mcolors.LinearSegmentedColormap.from_list(\"custom\", [\"#1A365D\", \"#E0E0E0\", \"#D4AF37\"])\n")
                line = line.replace("cmap='coolwarm'", "cmap=custom_cmap")
                new_source.append(line)
            else:
                new_source.append(line)
                
        cell["source"] = new_source

with open("target_pflio.ipynb", "w") as f:
    json.dump(nb, f, indent=1)
