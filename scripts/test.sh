#!/bin/bash

# Ensure we're in the project root directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR/.."

# Create a .coverage-reports directory if it doesn't exist
mkdir -p .coverage-reports

# Run pytest with coverage
pytest tests/ \
    --cov=src/flowerpower \
    --cov-report=term-missing \
    --cov-report=html:.coverage-reports/htmlcov \
    --cov-report=xml:.coverage-reports/coverage.xml \
    "$@"

# If tests passed and we're on macOS, open the HTML coverage report
if [ $? -eq 0 ] && [ "$(uname)" == "Darwin" ]; then
    open .coverage-reports/htmlcov/index.html
fi
