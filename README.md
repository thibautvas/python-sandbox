# python-sandbox

## Environment

This repository contains the base skeleton that I use for adhoc python analyses

In order to isolate the environment, I use `uv` to manage a `.venv`,
via [`./pyproject.toml`](pyproject.toml) and [`./uv.lock`](uv.lock) 

## Workflow

I work almost exclusively with python scripts,
as jupyter notebooks are painful to work with under version control

However, I still need my python files to be shareable with my team,
and some of them are more comfortable with jupyter notebooks, in that spirit:
- I use a `share` binary (built from [`./src/tm/share.py`](src/tm/share.py))
to include local functions from [`./src/tm/utils.py`](src/tm/utils.py)
in the python files directly
- I use `jupytext` to convert python files to jupyter notebooks, if needed
