import unittest
import threading
import time

import google.protobuf.wrappers_pb2 as wrapper

from sqlflow.client import Client
import sqlflow.proto.sqlflow_pb2 as pb
from tests.mock_servicer import _server


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

    def wrap_value(self, value):
        if isinstance(value, bool):
            message = wrapper.BoolValue()
            message.value = value
        elif isinstance(value, int):
            message = wrapper.Int64Value()
            message.value = value
        elif isinstance(value, float):
            message = wrapper.DoubleValue()
            message.value = value
        else:
            raise Exception("Unsupported type {}".format(type(value)))
        return message

    def generate_response(self, table):
        res = pb.RunResponse()
        table_message = pb.Table()

        for name in table['column_names']:
            table_message.column_names.append(name)
        for row in table['rows']:
            row_message = table_message.rows.add()
            for data in row:
                row_message.data.add().Pack(self.wrap_value(data))
        res.table.CopyFrom(table_message)
        return res

    def test_decode_protobuf(self):
        table = {"column_names": ['x', 'y'], "rows": [[1, 2], [3, 4]]}
        res = self.generate_response(table)
        assert Client._decode_protobuf(res) == table

    def test_execute_stream(self):
        rsp = self.client.execute(operation="select * from galaxy")
        assert rsp is not None
