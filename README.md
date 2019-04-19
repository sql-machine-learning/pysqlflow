# pysqlflow [![Build Status](https://travis-ci.org/sql-machine-learning/pysqlflow.svg?branch=develop)](https://travis-ci.org/sql-machine-learning/pypysqlflow) [![PyPI Package](https://img.shields.io/pypi/v/pysqlflow.svg)](https://pypi.python.org/pypi/pysqlflow)

The Python client of[SQLFlow](https://github.com/sql-machine-learning/sqlflow).

## Installation

This package is available on PyPI as `pysqlflow`. So you can install it by running the following command:

    pip install pysqlflow

## Documentation

You can read the Sphinx generated docs at:
[http://sql-machine-learning.github.io/pysqlflow/](http://sql-machine-learning.github.io/pysqlflow/)

## Development

## Prerequisite

- Python 3

  On macOS, you can install Python 3 by running `brew install python`.

### Setup Environment

`make setup`

### Test

`make test`

### Release

`make release`

### Generate gRPC client

gRPC client code has been generated when you setup environment. 
If you would like to regenerate it, please run `make protoc`.
