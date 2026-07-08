# Installation

This guide covers how to install FlowerPower and its optional extras.

## Requirements

FlowerPower requires **Python 3.11 or higher**. Verify your version with:

```bash
python --version
```

A modern package manager such as [`uv`](https://github.com/astral-sh/uv) or `pip` is recommended.

## Standard installation

Install the core package with `uv`:

```bash
uv pip install flowerpower
```

Or with `pip`:

```bash
pip install flowerpower
```

## Optional dependencies

FlowerPower provides optional extras for I/O plugins, distributed execution, the Hamilton UI, and lineage tracking.

| Extra | Enables | Install |
|-------|---------|---------|
| `io` | CSV, JSON, Parquet, Delta, DuckDB, Postgres, MySQL, MSSQL, Oracle, SQLite | `uv pip install 'flowerpower[io]'` |
| `io-legacy` | Legacy I/O backends | `uv pip install 'flowerpower[io-legacy]'` |
| `ray` | Distributed execution with Ray | `uv pip install 'flowerpower[ray]'` |
| `ui` | Hamilton web UI | `uv pip install 'flowerpower[ui]'` |
| `openlineage` | OpenLineage lineage integration | `uv pip install 'flowerpower[openlineage]'` |

There is no `all` extra. Install several extras together by listing them in square brackets:

```bash
uv pip install 'flowerpower[io,ray,ui]'
```

## Virtual environment setup

It is strongly recommended to install FlowerPower in a dedicated virtual environment:

```bash
uv venv
source .venv/bin/activate
uv pip install flowerpower
```

On Windows, activate the environment with `.venv\Scripts\activate`.

## Troubleshooting

- **Use a virtual environment.** Installing directly into your system Python can cause dependency conflicts. Create and activate a venv with `uv venv` and `source .venv/bin/activate` before installing.
- **Check your PATH.** If the `flowerpower` command is not found, make sure your virtual environment's `bin` (or `Scripts`) directory is on your PATH.
- **Check permissions.** If you see a permission error, avoid installing globally; use a virtual environment instead.

If you still have problems, please [open an issue](https://github.com/legout/flowerpower/issues).
