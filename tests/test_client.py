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
        table = MockServicer.get_test_table()
        res = MockServicer.table_response(table)
        assert Client._decode_protobuf(res) == table

    def test_execute_stream(self):
        message_response = self.client.execute("select * from galaxy train ..")
        for message in message_response:
            logger.debug(message)
            assert 'extended sql' in message

        expected_table = MockServicer.get_test_table()
        table_response = self.client.execute("select * from galaxy")
        for table in table_response:
            res = MockServicer.table_response(table)
            assert Client._decode_protobuf(res) == expected_table
