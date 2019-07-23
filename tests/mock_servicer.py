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
                    yield MockServicer.message_response("extended sql")
            else:
                for res in MockServicer.table_response(MockServicer.get_test_table()):
                    yield res
        elif SQL == "TEST VERIFY SESSION":
            # TODO(Yancey1989): using a elegant way to test the session instead of the trick.
            yield MockServicer.message_response("|".join([request.session.token, request.session.db_conn_str, str(request.session.exit_on_submit), request.session.user_id]))
        else:
            yield MockServicer.message_response('bad request', 0)

    @staticmethod
    def get_test_table():
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
    def table_response(table):
        res = pb.Response()
        head = pb.Head()
        for name in table['column_names']:
            head.column_names.append(name)
        res.head.CopyFrom(head)
        yield res

        for row in table['rows']:
            res = pb.Response()
            row_message = pb.Row()
            for data in row:
                row_message.data.add().Pack(MockServicer.wrap_value(data))
            res.row.CopyFrom(row_message)
            yield res

    @staticmethod
    def message_response(message):
        pb_msg = pb.Message()
        pb_msg.message = message

        res = pb.Response()
        res.message.CopyFrom(pb_msg)
        return res


def _server(port, event, ca_crt, ca_key):
    svr = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    with open(ca_key, "rb") as f:
        private_key = f.read()
    with open(ca_crt, "rb") as f:
        certification_chain = f.read()
    server_credentials = grpc.ssl_server_credentials( ( (private_key, certification_chain), ) )
    pb_grpc.add_SQLFlowServicer_to_server(MockServicer(), svr)
    svr.add_secure_port('[::]:%d' % port, server_credentials)
    svr.start()
    try:
        event.wait()
    except KeyboardInterrupt:
        pass
    svr.stop(0)
