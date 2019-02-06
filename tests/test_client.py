import unittest
import threading
import time

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

    def test_decode_protobuf(self):
        rowset = MockServicer.get_test_rowset()
        res = MockServicer.rowset_response(rowset)
        assert Client._decode_protobuf(res) == rowset

    def test_client_query(self):
        response = self.client.query("select * from galaxy")
        for rowset in response._rowsets:
            assert MockServicer.get_test_rowset() == rowset

    def test_client_execute(self):
        from contextlib import redirect_stdout
        import io

        capture_string = io.StringIO()
        with redirect_stdout(capture_string):
            self.client.execute("select * from galaxy train ..")
        contents = capture_string.getvalue()
        capture_string.close()

        assert "start" in contents
        assert "end" in contents
