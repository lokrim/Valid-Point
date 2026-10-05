# Scripts

`execute_notebooks.py` runs only S00 tests and `00_bootstrap.ipynb` in a fresh
kernel, then seals a local evidence bundle. It does not install packages,
download data, or launch later stages. Later scripts should call importable
package functions.
