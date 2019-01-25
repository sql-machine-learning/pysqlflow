import unittest
import threading
import time
import logging

from sqlflow.client import Client
from tests.mock_servicer import _server, MockServicer, _MOCK_TABLE


logging.basicConfig(filename="test.log", level=logging.DEBUG)
logger = logging.getLogger("grpc_client")


class ClientServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # TODO(tony): free port is better
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
        table = {"column_names": ['x', 'y'], "rows": [[1, 2], [3, 4]]}
        res = MockServicer.table_response(table)
        assert Client._decode_protobuf(res) == table

    def test_execute_stream(self):
        table_response = self.client.execute(operation="select * from galaxy")
        for message in table_response:
            assert Client._decode_protobuf(message) == _MOCK_TABLE

        message_response = self.client.execute(operation="select * from galaxy train")
        for message in message_response:
            logger.debug(message)
            assert 'mock message' in message

