import nbformat
import re

with open('target_pflio.ipynb', 'r') as f:
    nb = nbformat.read(f, as_version=4)

old_top_boxes = r"""\vspace{1em}
\noindent
\begin{minipage}[t]{0.48\textwidth}
\begin{tcolorbox}[colback=accent, colframe=primary, boxrule=0pt, arc=6pt, left=8pt, right=8pt, top=10pt, bottom=10pt, coltext=white]
    \centering \Large \textbf{Diversified Basket} \\[6pt]
    \normalsize 10-15 strong performing strategies
\end{tcolorbox}
\end{minipage}\hfill
\begin{minipage}[t]{0.48\textwidth}
\begin{tcolorbox}[colback=accent, colframe=primary, boxrule=0pt, arc=6pt, left=8pt, right=8pt, top=10pt, bottom=10pt, coltext=white]
    \centering \Large \textbf{Target Return} \\[6pt]
    \normalsize 20\% Net Target Return
\end{tcolorbox}
\end{minipage}

\vspace{0.5em}
\noindent
\begin{minipage}[t]{0.48\textwidth}
\begin{tcolorbox}[colback=accent, colframe=primary, boxrule=0pt, arc=6pt, left=8pt, right=8pt, top=10pt, bottom=10pt, coltext=white]
    \centering \Large \textbf{Volatility Target} \\[6pt]
    \normalsize 5\% Target Volatility
\end{tcolorbox}
\end{minipage}\hfill
\begin{minipage}[t]{0.48\textwidth}
\begin{tcolorbox}[colback=accent, colframe=primary, boxrule=0pt, arc=6pt, left=8pt, right=8pt, top=10pt, bottom=10pt, coltext=white]
    \centering \Large \textbf{Risk Control} \\[6pt]
    \normalsize 5\% Max Drawdown
\end{tcolorbox}
\end{minipage}"""

new_top_boxes = r"""\vspace{0.5em}
\noindent
\begin{minipage}[t]{0.24\textwidth}
\begin{tcolorbox}[colback=primary, colframe=primary, boxrule=0pt, arc=4pt, left=2pt, right=2pt, top=6pt, bottom=6pt, coltext=white]
    \centering \large \textbf{Diversified} \\[4pt]
    \footnotesize 10-15 strategies
\end{tcolorbox}
\end{minipage}\hfill
\begin{minipage}[t]{0.24\textwidth}
\begin{tcolorbox}[colback=primary, colframe=primary, boxrule=0pt, arc=4pt, left=2pt, right=2pt, top=6pt, bottom=6pt, coltext=white]
    \centering \large \textbf{Return} \\[4pt]
    \footnotesize 20\% Net Target
\end{tcolorbox}
\end{minipage}\hfill
\begin{minipage}[t]{0.24\textwidth}
\begin{tcolorbox}[colback=primary, colframe=primary, boxrule=0pt, arc=4pt, left=2pt, right=2pt, top=6pt, bottom=6pt, coltext=white]
    \centering \large \textbf{Volatility} \\[4pt]
    \footnotesize 5\% Target
\end{tcolorbox}
\end{minipage}\hfill
\begin{minipage}[t]{0.24\textwidth}
\begin{tcolorbox}[colback=primary, colframe=primary, boxrule=0pt, arc=4pt, left=2pt, right=2pt, top=6pt, bottom=6pt, coltext=white]
    \centering \large \textbf{Risk Control} \\[4pt]
    \footnotesize 5\% Max DD
\end{tcolorbox}
\end{minipage}"""

for i, cell in enumerate(nb.cells):
    if cell.cell_type == 'code':
        if old_top_boxes in cell.source:
            cell.source = cell.source.replace(old_top_boxes, new_top_boxes)
            print(f"Replaced top boxes in cell {i}")
        
        # Also reduce vspace before strategy stats to help ensure everything fits on one page
        # In the previous step I used r"""\vspace{1.5em}
        old_vspace = r"""latex_strat_stats += r\"\"\"\vspace{1.5em}"""
        if old_vspace in cell.source:
            cell.source = cell.source.replace(old_vspace, r"""latex_strat_stats += r\"\"\"\vspace{0.5em}""")
            print(f"Reduced vspace in cell {i}")

with open('target_pflio.ipynb', 'w') as f:
    nbformat.write(nb, f)

print("Notebook updated.")
