import pytest
from IPython.testing.globalipapp import get_ipython


@pytest.fixture
def ip():
    ip_session = get_ipython()
    ip_session.magic('load_ext sqlflow.magic')
    yield ip_session


def test_return(ip):
    assert ip.run_line_magic('sqlflow', 'this is a sentence') == 'this is a sentence'
