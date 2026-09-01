import nbformat
import re

with open('target_pflio.ipynb', 'r') as f:
    nb = nbformat.read(f, as_version=4)

# Look for \vspace{1em} followed by \noindent and \begin{minipage}[t]{0.48\textwidth}
for i, cell in enumerate(nb.cells):
    if cell.cell_type == 'code':
        if r'\Large \textbf{Diversified Basket}' in cell.source:
            print(f"Cell {i} has the old top boxes pattern.")
            # Let's see the exact text
            start = cell.source.find(r'\vspace{1em}')
            end = cell.source.find(r'\subsection*{Historical net monthly')
            if start != -1 and end != -1:
                old_text = cell.source[start:end]
                print(f"Replacing in cell {i}...")
                new_text = r"""\vspace{0.5em}
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
\end{minipage}

\vspace{1em}

"""
                cell.source = cell.source.replace(old_text, new_text)

with open('target_pflio.ipynb', 'w') as f:
    nbformat.write(nb, f)

print("Notebook updated.")
