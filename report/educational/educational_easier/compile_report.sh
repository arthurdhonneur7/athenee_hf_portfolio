#!/bin/bash
# Convert CSV files to latex tables
python3 csv2tex.py

# Compile the latex document
pdflatex -interaction=nonstopmode fof_report.tex
pdflatex -interaction=nonstopmode fof_report.tex
