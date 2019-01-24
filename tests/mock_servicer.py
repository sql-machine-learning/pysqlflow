import grpc
from concurrent import futures

from google.protobuf.empty_pb2 import Empty
import sqlflow.proto.sqlflow_pb2_grpc as pb_grpc

class MockServicer(pb_grpc.SQLFlowServicer):
    """
    server implementation
    """
    def Run(self, request, context):
        return Empty()


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
