import csv
import sys
import math

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
    if not is_monthly:
        tex_str += "\\makebox[\\textwidth][c]{%\n"
    tex_str += "\\begin{tabular}{" + columns_align + "}\n"
    tex_str += "\\toprule\n"
    tex_str += " & ".join(["\\bfseries " + h for h in header]) + " \\\\\n"
    tex_str += "\\midrule\n"
    
    for row in data[1:]:
        if not row or not any(row): continue
        processed_row = []
        # The first column is usually the Year/Strategy, we don't color it
        processed_row.append(str(row[0]).replace("%", "\\%"))
        
        for x in row[1:]:
            val_str = str(x).replace("%", "\\%")
            cell_prefix = ""
            if is_monthly and "%" in val_str:
                try:
                    val = float(str(x).replace('%', '').strip())
                    if val > 0:
                        pct = min(100, max(0, int(val * 10)))
                        if pct > 0:
                            cell_prefix = f"\\cellcolor{{posgreen!{pct}!white}}"
                    elif val < 0:
                        pct = min(100, max(0, int(-val * 10)))
                        if pct > 0:
                            cell_prefix = f"\\cellcolor{{negred!{pct}!white}}"
                except ValueError:
                    pass
            processed_row.append(cell_prefix + val_str)
            
        tex_str += " & ".join(processed_row) + " \\\\\n"
        
    tex_str += "\\bottomrule\n"
    tex_str += "\\end{tabular}\n"
    if not is_monthly:
        tex_str += "}\n"
    
    with open(tex_path, 'w') as f:
        f.write(tex_str)
    print(f"Generated {tex_path}")

if __name__ == "__main__":
    csv_to_tex('../../lazarus/funds_statistics.csv', 'table_fund_stats.tex', 'l' + 'r'*12)
    csv_to_tex('../../lazarus/6m_strategy_statistics.csv', 'table_lazarus_stats.tex', 'l' + 'r'*12)
    csv_to_tex('../../lazarus/6m_monthly_returns.csv', 'table_lazarus_monthly.tex', 'l' + 'r'*13, is_monthly=True)
