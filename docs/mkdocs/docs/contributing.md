# Contributing to FlowerPower

First off, thank you for considering contributing to FlowerPower! It's people like you that make open source such a great community.

We welcome contributions in various forms, from reporting bugs and suggesting enhancements to submitting pull requests with new features or bug fixes.

## Reporting Issues

If you encounter a bug or have a suggestion for a new feature, please open an issue on our [GitHub Issue Tracker](https://github.com/legout/flowerpower/issues).

When reporting a bug, please include the following to help us resolve it quickly:
- A clear and descriptive title.
- A detailed description of the problem, including steps to reproduce it.
- Your operating system, Python version, and FlowerPower version.
- Any relevant logs or tracebacks.

## Submitting Pull Requests

We love pull requests! To ensure a smooth process, please follow these guidelines:

1.  **Fork the repository** and create a new branch for your feature or bug fix.
2.  **Set up your development environment** (see "Development Setup" below).
3.  **Make your changes** and ensure the code is well-tested.
4.  **Update the documentation** if your changes affect it.
5.  **Ensure your code passes all tests** before submitting.
6.  **Submit a pull request** with a clear description of your changes.

## Development Setup

We use `uv` for managing dependencies and running our development environment.

1.  **Install `uv`**:
    Follow the official instructions to [install `uv`](https://github.com/astral-sh/uv).

2.  **Create a virtual environment**:
    ```bash
    uv venv
    ```

3.  **Activate the environment**:
    ```bash
    source .venv/bin/activate
    ```

4.  **Install dependencies**:
    To install the base dependencies along with the development and test dependencies, run:
    ```bash
    uv pip install -e ".[dev,test]"
    ```
    
    !!! note
        If you need to install optional dependencies for specific features (e.g., `mqtt`, `redis`), you can add them to the install command: `uv pip install -e ".[dev,test,mqtt,redis]"`.

5.  **Run tests**:
    To ensure everything is working correctly, run the test suite:
    ```bash
    uv run pytest
    ```

## Code of Conduct

We are committed to providing a welcoming and inclusive environment for everyone. Please read and follow our [Code of Conduct](https://github.com/legout/flowerpower/blob/main/CODE_OF_CONDUCT.md) (assuming one exists or will be created).

Thank you for your contribution!