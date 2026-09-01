import nbformat
with open('target_pflio.ipynb', 'r') as f:
    nb = nbformat.read(f, as_version=4)

cell22 = nb.cells[22].source

# check company info end
start = cell22.find(r'AMC Issuer')
if start != -1:
    print(cell22[start:start+200])

