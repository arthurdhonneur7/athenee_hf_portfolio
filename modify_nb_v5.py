import json
import re

with open("target_pflio.ipynb") as f:
    nb = json.load(f)

for cell in nb["cells"]:
    if cell["cell_type"] == "code":
        source = "".join(cell["source"])
        
        if "section*{Performance \\& Correlation}" in source:
            # We will use regex to replace the entire Performance & Correlation block 
            # up to the \clearpage
            
            pattern = r'\\section\*\{Performance \\& Correlation\}.*?\\clearpage'
            
            match = re.search(pattern, source, flags=re.DOTALL)
            if match:
                old_string = match.group(0)
                new_string = r"""\section*{Performance \& Correlation}
The following visuals illustrate the fund-level statistics and the diversification benefits.

\begin{center}
    \includegraphics[width=0.95\textwidth, height=0.45\textheight, keepaspectratio]{correlation.pdf}
    
    \vspace{0.5em}
    
    \includegraphics[width=0.95\textwidth, height=0.4\textheight, keepaspectratio]{worst_sp500_months.pdf}
\end{center}

\clearpage"""
                source = source.replace(old_string, new_string)
            
            if cell["source"] != source:
                cell["source"] = [line + ("\n" if not line.endswith("\n") else "") for line in source.split("\n")][:-1]
                if not cell["source"]:
                    cell["source"] = [""]

with open("target_pflio.ipynb", "w") as f:
    json.dump(nb, f, indent=1)
