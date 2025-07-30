#!/bin/bash

check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "$1 is not installed. Installing..."
        pip install "$1"
        # Optional: exit after install to refresh shell path
        exit 1
    fi
}

check_directory() {
    if [ ! -d "$1" ]; then
        echo "Directory '$1' not found."
        exit 1
    fi
}

check_file() {
    if [ ! -f "$1" ]; then
        echo "File '$1' not found."
        exit 1
    fi
}

# ✅ Check required tools
# check_command flake8
# check_command twine
# check_command build

# ✅ Check required project files
check_file pyproject.toml
check_file README.md
check_file LICENSE

# ✅ Clean previous builds
rm -rf dist build *.egg-info
find . -name "*.pyc" -exec rm -f {} \;

# ✅ Run code checks
flake8 .

# ✅ Build package using PEP 517 (pyproject.toml)
python -m build

# ✅ Check build output
check_directory dist

# ✅ Upload to PyPI
python -m twine upload dist/* --verbose

# ✅ Cleanup (optional — or move to temporary folder if needed)
rm -rf dist build *.egg-info
