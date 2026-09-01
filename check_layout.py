import nbformat
with open('target_pflio.ipynb', 'r') as f:
    nb = nbformat.read(f, as_version=4)

cell22 = nb.cells[22].source

# check monthly
start = cell22.find(r'latex_monthly =')
print("--- latex_monthly ---")
print(cell22[start:start+150])

# check general info
start = cell22.find(r'General Information')
print("\n--- General Info ---")
print(cell22[start-150:start+250])

# check company info
start = cell22.find(r'Company Information')
print("\n--- Company Info ---")
print(cell22[start-100:start+300])

