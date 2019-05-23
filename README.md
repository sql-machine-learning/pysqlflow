# sqlflow [![Build Status](https://travis-ci.org/sql-machine-learning/pysqlflow.svg?branch=develop)](https://travis-ci.org/sql-machine-learning/pysqlflow) [![PyPI Package](https://img.shields.io/pypi/v/sqlflow.svg)](https://pypi.python.org/pypi/sqlflow)

[SQLFlow](https://github.com/sql-machine-learning/sqlflow) client library for Python.

## Installation

This package is available on PyPI as `pysqlflow`. So you can install it by running the following command:

    pip install sqlflow

## Documentation

You can read the Sphinx generated docs at:
[http://sql-machine-learning.github.io/pysqlflow/](http://sql-machine-learning.github.io/pysqlflow/)

## Development

## Prerequisite
### Python 3
`brew install python`

### Setup Environment
`make setup`

### Test
`make test`

### Release
`make release`

### Generate Documentation
`make doc`

### Generate GRPC client
GRPC client code has been generated when you setup environment. 
If you would like to regenerate it, please run `make protoc`.
