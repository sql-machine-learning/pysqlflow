import unittest
import threading
import time
import mock

from sqlflow.client import Client
from tests.mock_servicer import _server, MockServicer


class ClientServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # TODO: free port is better
        port = 8765
        cls.event = threading.Event()
        threading.Thread(target=_server, args=[port, cls.event]).start()
        # wait for start
        time.sleep(1)
        cls.client = Client("localhost:%d" % port)

    @classmethod
    def tearDownClass(cls):
        # shutdown server after this test
        cls.event.set()

    def test_execute_stream(self):
        with mock.patch('sqlflow.client._LOGGER') as log_mock:
            self.client.execute("select * from galaxy train ..")
            log_mock.info.assert_called_with("extended sql")

        expected_table = MockServicer.get_test_table()
        rows = self.client.execute("select * from galaxy")
        assert expected_table["column_names"] == rows.column_names()
        assert expected_table["rows"] == rows.rows()
