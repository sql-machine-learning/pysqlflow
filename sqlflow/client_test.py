import unittest
from unittest.mock import patch

import sqlflow.client as client

import sqlflow.proto.sqlflow_pb2 as pb
import google.protobuf.wrappers_pb2 as wrapper


def wrap_value(v):
    if isinstance(v, bool):
        m = wrapper.BoolValue()
        m.value = v
    elif isinstance(v, int):
        m = wrapper.Int64Value()
        m.value = v
    elif isinstance(v, float):
        m = wrapper.DoubleValue()
        m.value = v
    else:
        raise Exception("Unsupported type {}".format(type(v)))

    return m
        

def generate_response(dataframe):
    res = pb.RunResponse()

    col = pb.Columns()
    for key, value in dataframe.items():
        c = col.columns[key]
        for v in value:
            c.data.add().Pack(wrap_value(v))
    res.columns.CopyFrom(col)

    return res


class TestDecodeProtobuf(unittest.TestCase):

    def test_decode_protobuf(self):
        dataframe = {"x": [.1, 2, False], "y": [4, 5.0, True]}
        res = generate_response(dataframe)
        self.assertEqual(client._decode_protobuf(res), dataframe)


if __name__ == '__main__':
    unittest.main()

