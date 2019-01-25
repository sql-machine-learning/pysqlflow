import unittest
import threading
import time
import logging

from sqlflow.client import Client
from tests.mock_servicer import _server, MockServicer


logging.basicConfig(filename="test.log", level=logging.DEBUG)
logger = logging.getLogger("grpc_client")


class ClientServerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        port = 8765
        cls.port = 8765
        cls.event = threading.Event()
        threading.Thread(target=_server, args=[cls.port, cls.event]).start()
        # wait for start
        time.sleep(1)
        cls.client = Client("localhost:%d" % cls.port)

    @classmethod
    def tearDownClass(cls):
        # shutdown server after this test
        cls.event.set()

    def test_decode_protobuf(self):
        table = {"column_names": ['x', 'y'], "rows": [[1, 2], [3, 4]]}
        res = MockServicer.table_response(table)
        assert Client._decode_protobuf(res) == table

    def test_execute_stream(self):
        table = {"column_names": ['x', 'y'], "rows": [[1, 2], [3, 4]]}
        table_response = self.client.execute(operation="select * from galaxy")
        for message in table_response:
            assert Client._decode_protobuf(message) == table

        message_response = self.client.execute(operation="select * from galaxy train")
        for message in message_response:
            logger.debug(message)
            assert 'mock message' in message

        for _ in Client("localhost:%d" % self.port).execute('select * from galaxy'):
            # The test should fail here
            assert False
