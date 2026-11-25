"""Execute a notebook in place (keeps outputs). Usage: python tools/run_notebook.py notebooks/NAME.ipynb"""
import sys, nbformat
from nbclient import NotebookClient
p = sys.argv[1]
nb = nbformat.read(p, 4)
NotebookClient(nb, timeout=600, kernel_name='python3', resources={'metadata': {'path': 'notebooks'}}).execute()
nbformat.write(nb, p)
for c in nb.cells:
    if c.cell_type == 'code':
        for o in c.outputs:
            t = o.get('text') or o.get('data', {}).get('text/plain', '')
            if t: print(t[:2500]); print('--')
