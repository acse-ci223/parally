# parally
A python package to distribute CPU-intensive tasks by sending workload to other connected computers

## Status

[![flake8](https://github.com/acse-ci223/parally/actions/workflows/flake8.yml/badge.svg)](https://github.com/acse-ci223/parally/actions/workflows/flake8.yml)

[![pytest-unit-tests](https://github.com/acse-ci223/parally/actions/workflows/pytest-unit-tests.yml/badge.svg)](https://github.com/acse-ci223/parally/actions/workflows/pytest-unit-tests.yml)

## Documentation

The documentation for this package can be found [here](https://acse-ci223.github.io/parally/).

## Development Installation

To install the package, make sure conda is installed and then run the following commands in the terminal:

```bash
# Clone the repository
git clone https://github.com/acse-ci223/parally.git

# Change directory
cd parally

# Create the 'parally' environment
conda env create -f environment.yml

# Activate the environment
conda activate parally

# Install the package
pip install -e .
```

## Usage

To use the package, run the following command in the terminal:

```bash
pip install parally
```