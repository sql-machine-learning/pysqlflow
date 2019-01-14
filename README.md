# pysqlflow [![Build Status](https://travis-ci.org/ktong/pysqlflow.svg?branch=master)](https://travis-ci.org/ktong/pysqlflow) [![PyPI Package](https://img.shields.io/pypi/v/pysqlflow.svg)](https://pypi.python.org/pypi/pysqlflow)

[SQLFlow] (https://github.com/wangkuiyi/sqlflow) client library for Python.

## Installation

This package is available on PyPI as `pysqlflow`:

    pip install pysqlflow

## Documentation

You can read the Sphinx generated docs at:
[http://ktong.github.io/pysqlflow/](http://ktong.github.io/pysqlflow/)

## Development

## Prerequisite
### Python 3
`brew install python`

### Setup Environment
`make setup`

### Generate GRPC client
GRPC client code has been generated when you setup environment. 
If you would like to regenerate it, please run `make protoc`.
