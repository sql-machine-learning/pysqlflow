# pysqlflow [![Build Status](https://travis-ci.org/ktong/pysqlflow.svg?branch=master)](https://travis-ci.org/ktong/pysqlflow) [![PyPI Package](https://img.shields.io/pypi/v/pysqlflow.svg)](https://pypi.python.org/pypi/pysqlflow)

[SQLFlow] (https://github.com/wangkuiyi/sqlflow) client library for Python.

## Installation

This package is available on PyPI as `pysqlflow`:

    pip install pysqlflow

## Using in IPython

After sqlflow installation, enable sqlflow's magics in a notebook cell with:

    %load_ext sqlflow

Alternatively add this to your `ipython_config.py` file in your profile:

    c = get_config()
    c.InteractiveShellApp.extensions = [
        'sqlflow'
    ]

You will typically put this under `~/.ipython/profile_default`. See
[the IPython docs](http://ipython.readthedocs.io/en/stable/development/config.html)
for more about IPython profiles.

## Documentation

You can read the Sphinx generated docs at:
[http://ktong.github.io/pysqlflow/](http://ktong.github.io/pysqlflow/)
