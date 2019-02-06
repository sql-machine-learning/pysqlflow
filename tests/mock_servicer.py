import grpc
from concurrent import futures

import google.protobuf.wrappers_pb2 as wrapper

import sqlflow.proto.sqlflow_pb2 as pb
import sqlflow.proto.sqlflow_pb2_grpc as pb_grpc


class MockServicer(pb_grpc.SQLFlowServicer):
    """
    server implementation
    """
    def Execute(self, request, context):
        for i in range(3):
            yield MockServicer.message_response("extended sql", i)

    def Query(self, request, context):
        yield MockServicer.rowset_response(MockServicer.get_test_rowset())

    @staticmethod
    def get_test_rowset():
        return {"column_names": ['x', 'y'], "rows": [[1, 2], [3, 4]]}

    @staticmethod
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

    @staticmethod
    def rowset_response(rowset):
        res = pb.RowSet()

        for name in rowset['column_names']:
            res.column_names.append(name)
        for row in rowset['rows']:
            row_message = res.rows.add()
            for data in row:
                row_message.data.add().Pack(MockServicer.wrap_value(data))

        return res

    @staticmethod
    def message_response(message_name, message_id):
        messages = pb.Messages()
        messages.messages.append("%s:%d, start" % (message_name, message_id))
        messages.messages.append("%s:%d, end" % (message_name, message_id))

        return messages


def _server(port, event):
    svr = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    pb_grpc.add_SQLFlowServicer_to_server(MockServicer(), svr)
    svr.add_insecure_port("[::]:%d" % port)
    svr.start()
    try:
        event.wait()
    except KeyboardInterrupt:
        pass
    svr.stop(0)
