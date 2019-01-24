import grpc
from concurrent import futures

import google.protobuf.wrappers_pb2 as wrapper

import sqlflow.proto.sqlflow_pb2 as pb
import sqlflow.proto.sqlflow_pb2_grpc as pb_grpc


class MockServicer(pb_grpc.SQLFlowServicer):
    """
    server implementation
    """
    def Run(self, request, context):
        SQL = request.sql.upper()
        if "SELECT" in SQL:
            if "TRAIN" in SQL or "PREDICT" in SQL:
                for i in range(3):
                    yield MockServicer.message_response(i)
        else:
            table = {"column_names": ['x', 'y'], "rows": [[1, 2], [3, 4]]}
            yield MockServicer.table_response(table)

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
    def table_response(table):
        res = pb.RunResponse()
        table_message = pb.Table()

        for name in table['column_names']:
            table_message.column_names.append(name)
        for row in table['rows']:
            row_message = table_message.rows.add()
            for data in row:
                row_message.data.add().Pack(MockServicer.wrap_value(data))
        res.table.CopyFrom(table_message)
        return res

    @staticmethod
    def message_response(messageName):
        pb_msg = pb.Messages()
        pb_msg.messages.append("mock message:%d, start" % messageName)
        pb_msg.messages.append("mock message:%d, end" % messageName)

        res = pb.RunResponse()
        res.messages.CopyFrom(pb_msg)
        return res

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
