import sqlflow


def test_answer():
    assert sqlflow.__version__ == sqlflow._version.__version__
