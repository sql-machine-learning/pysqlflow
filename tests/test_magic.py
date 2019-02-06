import unittest
import time
import os
import threading

from IPython.testing.globalipapp import get_ipython
from IPython.utils import io

from tests.mock_servicer import MockServicer, _server


class SqlFlowMagicTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # TODO: free port is better
        port = 8766
        cls.event = threading.Event()
        threading.Thread(target=_server, args=[port, cls.event]).start()
        # wait for start
        time.sleep(1)
        # SQLFLOW_SERVER will be loaded by SqlFlowMagic.client.__init__
        os.environ["SQLFLOW_SERVER"] = "localhost:%d" % port

    @classmethod
    def tearDownClass(cls):
        # shutdown server after this test
        cls.event.set()

    def test_sql(self):
        ip_session = get_ipython()
        ip_session.magic('load_ext sqlflow.magic')

        response = ip_session.run_cell_magic('sqlflow_query', '',
                                             'select * from ...')
        for rowset in response._rowsets:
            assert MockServicer.get_test_rowset() == rowset

        with io.capture_output() as captured:
            ip_session.run_cell_magic('sqlflow_execute', '', 'SELECT TRAIN')
        assert "extended sql" in captured.stdout

