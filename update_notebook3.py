import json

with open('target_pflio.ipynb') as f:
    nb = json.load(f)

cell15_source = ''.join(nb['cells'][15]['source'])

old_block = r"""\begin{figure}[h]
    \centering
    \includegraphics[width=0.95\textwidth, height=0.4\textheight, keepaspectratio]{4_strategies_growth.pdf}
\end{figure}

\begin{figure}[h]
    \centering
    \includegraphics[width=0.95\textwidth, height=0.4\textheight, keepaspectratio]{scatter_6_month_reb_initial_alloc_vs_sp500.pdf}
\end{figure}"""

new_block = r"""\begin{center}
    \includegraphics[width=0.95\textwidth, height=0.4\textheight, keepaspectratio]{4_strategies_growth.pdf}
    
    \vspace{0.5em}
    
    \includegraphics[width=0.95\textwidth, height=0.4\textheight, keepaspectratio]{scatter_6_month_reb_initial_alloc_vs_sp500.pdf}
\end{center}"""

cell15_source = cell15_source.replace(old_block, new_block)

def to_list_of_lines(s):
    lines = s.split('\n')
    return [line + '\n' for line in lines[:-1]] + [lines[-1]] if lines[-1] != '' else [line + '\n' for line in lines[:-1]]
    
nb['cells'][15]['source'] = to_list_of_lines(cell15_source)

with open('target_pflio.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)

print("Updates applied successfully.")
