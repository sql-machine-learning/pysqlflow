import unittest
import time
import os
import threading

from IPython.testing.globalipapp import get_ipython
from IPython.utils import io

from tests.mock_servicer import _server, _MOCK_TABLE, _MOCK_MESSAGES


class SqlFlowMagicTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # TODO(tony): free port is better
        port = 8766
        cls.event = threading.Event()
        threading.Thread(target=_server, args=[port, cls.event]).start()
        # wait for start
        time.sleep(1)
        # SQLFLOW_SERVER will be read by SqlFlowMagic.client.__init__
        os.environ["SQLFLOW_SERVER"] = "localhost:%d" % port

    @classmethod
    def tearDownClass(cls):
        # shutdown server after this test
        cls.event.set()

    def test_whatever(self):
        ip_session = get_ipython()
        ip_session.magic('load_ext sqlflow.magic')

        with io.capture_output() as captured:
            ip_session.run_cell_magic('sqlflow', '', 'select * from galaxy')
        assert str(_MOCK_TABLE["column_names"]) in captured.stdout

        # with io.capture_output() as captured:
        #     ip_session.run_cell_magic('sqlflow', '', 'SELECT TRAIN')
        # assert _MOCK_MESSAGES[0] in captured.stdout

