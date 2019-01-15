import unittest
import google.protobuf.wrappers_pb2 as wrapper

import sqlflow.client as client
import sqlflow.proto.sqlflow_pb2 as pb


def wrap_value(value):
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
        

def generate_response(data_frame):
    res = pb.RunResponse()

    col = pb.Columns()
    for key, value in data_frame.items():
        data = col.columns[key].data
        for v in value:
            data.add().Pack(wrap_value(v))
    res.columns.CopyFrom(col)

    return res


class TestDecodeProtobuf(unittest.TestCase):

    def test_decode_protobuf(self):
        data_frame = {"x": [.1, 2, False], "y": [4, 5.0, True]}
        res = generate_response(data_frame)
        self.assertEqual(client._decode_protobuf(res), data_frame)
