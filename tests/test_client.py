import google.protobuf.wrappers_pb2 as wrapper

from sqlflow.client import Client
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
        

def generate_response(table):
    res = pb.RunResponse()

    table_message = pb.Table()
    for name in table['column_names']:
        table_message.column_names.append(name)
    for row in table['rows']:
        row_message = table_message.rows.add()
        for data in row:
            row_message.data.add().Pack(wrap_value(data))

    res.table.CopyFrom(table_message)

    return res


def test_decode_protobuf():
    table = {"column_names":['x','y'], "rows": [[1,2],[3,4]]}
    res = generate_response(table)
    assert Client._decode_protobuf(res) == table
