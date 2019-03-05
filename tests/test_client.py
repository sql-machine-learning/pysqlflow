import unittest
import threading
import time
from unittest import mock

from sqlflow.client import Client
from tests.mock_servicer import _server, MockServicer

from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.any_pb2 import Any
import sqlflow.proto.sqlflow_pb2 as pb


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
        rows = self.client.execute("select * from galaxy")[0]
        assert expected_table["column_names"] == rows.column_names()
        assert expected_table["rows"] == [r for r in rows.rows()]


    def test_execute_stream(self):
        with mock.patch('sqlflow.client._LOGGER') as log_mock:
            self.client.execute("select * from galaxy train ..")
            log_mock.info.assert_called_with("extended sql")

        expected_table = MockServicer.get_test_table()
        rows_list = self.client.execute("select * from galaxy; select * from galaxy;")
        assert len(rows_list) == 2
        for rows in rows_list:
            assert expected_table["column_names"] == rows.column_names()
            assert expected_table["rows"] == [r for r in rows.rows()]

    def test_decode_time(self):
        any_message = Any()
        timestamp_message = Timestamp()
        timestamp_message.GetCurrentTime()
        any_message.Pack(timestamp_message)
        assert timestamp_message.ToDatetime() == Client._decode_any(any_message)

    def test_decode_null(self):
        any_message = Any()
        null_message = pb.Row.Null()
        any_message.Pack(null_message)
        assert Client._decode_any(any_message) is None
