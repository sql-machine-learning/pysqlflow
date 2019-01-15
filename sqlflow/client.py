import os
import logging
import grpc
import google.protobuf.wrappers_pb2 as wrapper

import sqlflow.proto.sqlflow_pb2
import sqlflow.proto.sqlflow_pb2_grpc

_LOGGER = logging.getLogger(__name__)

class Client(object):
    def __init__(self, server_url=None):
        """A minimum client that issues queries to and fetch results/logs from sqlflowserver.

        Args:
            server_url(str):
                sqlflowserver url

        Raises:
            KeyError:
                Raised if SQLFLOWSERVER is not specified as environment variable
        """
        if server_url is None:
            try:
                server_url = os.environ["SQLFLOW_SERVER"]
            except KeyError:
                _LOGGER.error("Please set system variable SQLFLOW_SERVER")
                raise

        channel = grpc.secure_channel(server_url)
        self._stub = sqlflow_pb2_grpc.SQLFlowStub(channel)

    def execute(self, operation):
        """Run a SQL query

        Argument:
            operation(str):
                SQL query to be executed.

        Returns:
            Generator: generates the response of the server
        """
        for res in self._stub.Run(sqlflow_pb2.RunRequest(sql=operation)):
            if res.WhichOneof('response') == 'messages':
                for m in res.messages.messages:
                    _LOGGER.info(m)
            else:
                yield _decode_protobuf(res)

def _decode_any(any_message):
    if any_message.Is(wrapper.BoolValue.DESCRIPTOR):
        message = wrapper.BoolValue()
        any_message.Unpack(message)
    elif any_message.Is(wrapper.Int64Value.DESCRIPTOR):
        message = wrapper.Int64Value()
        any_message.Unpack(message)
    elif any_message.Is(wrapper.DoubleValue.DESCRIPTOR):
        message = wrapper.DoubleValue()
        any_message.Unpack(message)
    else:
        #TODO(tonyyang-svail): support more data types
        raise Exception("Unsupported type {}".format(any_message))
    return message.value

def _decode_protobuf(res):
    dataframe = {}
    for key, value in res.columns.columns.items():
        dataframe[key] = [_decode_any(a) for a in value.data]
    return dataframe
