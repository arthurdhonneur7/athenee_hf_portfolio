import subprocess
import os

REPORT_DIR = 'report'

print("Compiling LaTeX to PDF...")
result = subprocess.run(['pdflatex', '-interaction=nonstopmode', 'presentation.tex'], capture_output=True, text=True, cwd=REPORT_DIR)
if result.returncode != 0:
    print(result.stdout)
    print("Errors occurred!")
else:
    print("Compilation successful!")
