# Installation

Welcome to the FlowerPower installation guide. This page will walk you through the steps to get FlowerPower up and running on your system.

## Prerequisites

Before you begin, ensure you have the following installed:

*   **Python 3.8 or higher:** FlowerPower requires a modern version of Python. You can check your Python version by running:

    ```bash
    python --version
    ```

*   **A package manager:** We recommend using a modern package manager like `uv` or `pip` for a smooth installation experience.

!!! note "Project and Environment Management"

    For robust project management, we highly recommend using tools like [**`uv`**](https://github.com/astral-sh/uv) or [**`pixi`**](https://github.com/prefix-dev/pixi). These tools help you manage dependencies and ensure your projects are reproducible.

## Standard Installation

The recommended way to install FlowerPower is with `uv pip`:

```bash
uv pip install flowerpower
```

Alternatively, you can use `pip`:

```bash
pip install flowerpower
```

This will install the core FlowerPower library with all the essential features to get you started.

## Optional Dependencies

FlowerPower offers optional dependencies that you can install to enable additional functionality.

*   **RQ Job Queue Support:** To use FlowerPower with the Redis Queue (RQ) job queue, install the `[rq]` extra:

    ```bash
    uv pip install 'flowerpower[rq]'
    ```

*   **I/O Plugins:** For additional I/O capabilities, install the `[io]` extra:

    ```bash
    uv pip install 'flowerpower[io]'
    ```

*   **Hamilton UI:** To use the Hamilton UI for interactive dataflow visualization, install the `[ui]` extra:

    ```bash
    uv pip install 'flowerpower[ui]'
    ```

*   **All Extras:** To install all optional dependencies at once, use the `[all]` extra:

    ```bash
    uv pip install 'flowerpower[all]'
    ```

## Troubleshooting

If you encounter issues during installation, here are a few tips:

*   **Use a Virtual Environment:** It is highly recommended to install FlowerPower in a virtual environment to avoid conflicts with other packages. You can create one with `uv`:

    ```bash
    uv venv
    source .venv/bin/activate
    ```

*   **Check Your PATH:** Ensure that your Python and script installation directories are in your system's `PATH`. If you can't run `flowerpower` from your terminal, this might be the issue.

*   **Permissions:** If you get a permission error, you might be trying to install the package globally without the necessary privileges. Using a virtual environment is the best way to avoid this.

If you continue to have problems, please [open an issue](https://github.com/your-repo/flowerpower/issues) on our GitHub repository.