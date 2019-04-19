# sqlflow [![Build Status](https://travis-ci.org/wangkuiyi/pysqlflow.svg?branch=develop)](https://travis-ci.org/wangkuiyi/pysqlflow) [![PyPI Package](https://img.shields.io/pypi/v/sqlflow.svg)](https://pypi.python.org/pypi/sqlflow)

[SQLFlow] (https://github.com/wangkuiyi/sqlflow) client library for Python.

## Installation

This package is available on PyPI as `pysqlflow`:

    pip install sqlflow

## Documentation

You can read the Sphinx generated docs at:
[http://wangkuiyi.github.io/pysqlflow/](http://wangkuiyi.github.io/pysqlflow/)

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

### Generate GRPC client
GRPC client code has been generated when you setup environment. 
If you would like to regenerate it, please run `make protoc`.

