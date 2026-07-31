import json

with open('target_pflio.ipynb') as f:
    nb = json.load(f)

# Update cell 3
cell3_source = ''.join(nb['cells'][3]['source'])
old_def = 'def plot_yearly_returns_interactive(data_df, title_suffix="", start_date=None, figsize=(20, 10), pad=20):'
new_def = 'def plot_yearly_returns_interactive(data_df, title_suffix="", start_date=None, save_path=None, figsize=(20, 10), pad=20):'
cell3_source = cell3_source.replace(old_def, new_def)

old_plt_show = """    plt.tight_layout()
    plt.show()"""
new_plt_show = """    plt.tight_layout()
    
    if save_path:
        import os
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        fig.savefig(save_path, bbox_inches='tight')
        
    plt.show()"""
cell3_source = cell3_source.replace(old_plt_show, new_plt_show)

# Update cell 13
cell13_source = ''.join(nb['cells'][13]['source'])
old_call = 'plot_yearly_returns_interactive(plot_df, "(6-Month Rebalancing vs SP500)", start_date="2022-01-01")'
new_call = 'plot_yearly_returns_interactive(plot_df, "(6-Month Rebalancing vs SP500)", start_date="2022-01-01", save_path="report/yearly_returns_6m_reb.pdf")'
cell13_source = cell13_source.replace(old_call, new_call)

# Update cell 15
cell15_source = ''.join(nb['cells'][15]['source'])

old_latex = r"""\section*{Detailed Fund Statistics}
""" + '""" + latex_funds_stats + r"""' + r"""
\clearpage

\section*{Performance \& Correlation}
The following visuals illustrate the fund-level statistics and the diversification benefits.

\begin{center}
    \includegraphics[width=0.95\textwidth, height=0.5\textheight, keepaspectratio]{correlation.pdf}
    
    \vspace{0.5em}
    
    \includegraphics[width=0.95\textwidth, height=0.4\textheight, keepaspectratio]{worst_sp500_months.pdf}
\end{center}

\clearpage"""

new_latex = r"""\section*{Detailed Fund Statistics}
""" + '""" + latex_funds_stats + r"""' + r"""
\vspace{1em}
\begin{center}
    \includegraphics[width=0.95\textwidth, height=0.4\textheight, keepaspectratio]{correlation.pdf}
\end{center}
\clearpage

\section*{Performance \& Returns}
The following visuals illustrate the fund-level statistics and the diversification benefits.

\begin{center}
    \includegraphics[width=0.95\textwidth, height=0.42\textheight, keepaspectratio]{worst_sp500_months.pdf}
    
    \vspace{0.5em}
    
    \includegraphics[width=0.95\textwidth, height=0.42\textheight, keepaspectratio]{yearly_returns_6m_reb.pdf}
\end{center}

\clearpage"""

cell15_source = cell15_source.replace(old_latex, new_latex)

cell15_source = cell15_source.replace(
r"""\begin{figure}[h]
    \centering
    \includegraphics[width=0.95\textwidth, height=0.25\textheight, keepaspectratio]{4_strategies_growth.pdf}
\end{figure}""", 
r"""\begin{figure}[h]
    \centering
    \includegraphics[width=0.95\textwidth, height=0.4\textheight, keepaspectratio]{4_strategies_growth.pdf}
\end{figure}""")

cell15_source = cell15_source.replace(
r"""\begin{figure}[h]
    \centering
    \includegraphics[width=0.95\textwidth, height=0.25\textheight, keepaspectratio]{scatter_6_month_reb_initial_alloc_vs_sp500.pdf}
\end{figure}""",
r"""\begin{figure}[h]
    \centering
    \includegraphics[width=0.95\textwidth, height=0.4\textheight, keepaspectratio]{scatter_6_month_reb_initial_alloc_vs_sp500.pdf}
\end{figure}""")

# Apply sources
# Since notebook cells are arrays of strings, we should convert them back
def to_list_of_lines(s):
    lines = s.split('\n')
    return [line + '\n' for line in lines[:-1]] + [lines[-1]] if lines[-1] != '' else [line + '\n' for line in lines[:-1]]
    
nb['cells'][3]['source'] = to_list_of_lines(cell3_source)
nb['cells'][13]['source'] = to_list_of_lines(cell13_source)
nb['cells'][15]['source'] = to_list_of_lines(cell15_source)

with open('target_pflio.ipynb', 'w') as f:
    json.dump(nb, f, indent=1)

print("Updates applied successfully.")
