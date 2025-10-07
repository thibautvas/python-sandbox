# python-sandbox

## Environment

This repository contains the base skeleton that I use for adhoc python analyses.

In order to isolate the environment, I use `uv` to manage a virtual environment,
via [`./pyproject.toml`](pyproject.toml) and [`./uv.lock`](uv.lock).

As I have started to use `nix` for devshells,
I have also included a [`./flake.nix`](flake.nix)
that utilizes [pyproject-nix/uv2nix](https://github.com/pyproject-nix/uv2nix).

## Workflow

I work almost exclusively with python scripts,
as jupyter notebooks are painful to work with under version control.

However, I still need my python files to be shareable with my team,
and some of them are more comfortable with jupyter notebooks, in that spirit:
- I use a `share` binary (built from [`./src/sandbox/share.py`](src/sandbox/share.py))
to include local functions from [`./src/sandbox/utils.py`](src/sandbox/utils.py)
in the python files directly
- I use `jupytext` to convert python files to jupyter notebooks, if needed
