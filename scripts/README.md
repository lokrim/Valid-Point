# Scripts

`execute_notebooks.py` runs only S00 tests and `00_bootstrap.ipynb` in a fresh
kernel, then seals a local evidence bundle. It does not install packages,
download data, or launch later stages. Later scripts should call importable
package functions.

S02: `.venv/bin/python scripts/measure_synthetic.py` runs the complete local test
suite and all three `02_*` notebooks, each in a fresh kernel. Jupyter needs local
socket access. It creates a unique immutable run with a source snapshot,
config/seeds, inputs, checks, execution log, manifest and linked gate; it exports
tables and figures without replacing prior runs. It stops before S03.
