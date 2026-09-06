import csv
import sys

def csv_to_tex(csv_path, tex_path, columns_align, is_monthly=False):
    try:
        with open(csv_path, 'r') as f:
            reader = csv.reader(f)
            data = list(reader)
    except Exception as e:
        print(f"Error reading {csv_path}: {e}")
        return
    
    if not data: return
    
    # Process header
    header = data[0]
    if header[0] == "":
        header[0] = "Strategy"
    if is_monthly and header[0] == "":
        header[0] = "Year"
        
    tex_str = ""
    tex_str += "\\begin{tabular}{" + columns_align + "}\n"
    tex_str += "\\toprule\n"
    tex_str += " & ".join(["\\bfseries " + h for h in header]) + " \\\\\n"
    tex_str += "\\midrule\n"
    
    for row in data[1:]:
        if not row or not any(row): continue
        # Escape any special characters like %
        row = [str(x).replace("%", "\\%") for x in row]
        tex_str += " & ".join(row) + " \\\\\n"
        
    tex_str += "\\bottomrule\n"
    tex_str += "\\end{tabular}\n"
    
    with open(tex_path, 'w') as f:
        f.write(tex_str)
    print(f"Generated {tex_path}")

if __name__ == "__main__":
    csv_to_tex('../../lazarus/funds_statistics.csv', 'table_fund_stats.tex', 'l' + 'r'*12)
    csv_to_tex('../../lazarus/6m_strategy_statistics.csv', 'table_lazarus_stats.tex', 'l' + 'r'*12)
    csv_to_tex('../../lazarus/6m_monthly_returns.csv', 'table_lazarus_monthly.tex', 'l' + 'r'*13, is_monthly=True)
