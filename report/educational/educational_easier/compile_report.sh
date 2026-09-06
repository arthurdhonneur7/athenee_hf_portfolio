#!/bin/bash

# Ensure the script runs in the directory where it is located
cd "$(dirname "$0")" || exit 1

# Convert CSV files to latex tables
python3 csv2tex.py

# Compile the latex document
pdflatex -interaction=nonstopmode fof_report.tex
pdflatex -interaction=nonstopmode fof_report.tex

# Copy to Google Drive
DRIVE_DIR="/Users/arthurdhonneur/Google Drive/My Drive/Athenee/Presentation_Final_Product"
if [ -d "$DRIVE_DIR" ]; then
    cp fof_report.pdf "$DRIVE_DIR/presentation_simple_explanation.pdf"
    echo "Successfully copied fof_report.pdf to Google Drive as presentation_simple_explanation.pdf!"
else
    echo "Failed to copy to Google Drive: Directory does not exist."
fi

