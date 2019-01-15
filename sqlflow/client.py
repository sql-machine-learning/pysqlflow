"""Client for interacting with the SQLFlow Server API."""

import os
import logging
import grpc
import google.protobuf.wrappers_pb2 as wrapper

import sqlflow.proto.sqlflow_pb2
import sqlflow.proto.sqlflow_pb2_grpc

_LOGGER = logging.getLogger(__name__)

class Client:
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

        channel = grpc.insecure_channel(server_url)
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
        raise Exception("Unsupported type {}".format(any_message))
    return message.value


def _decode_protobuf(res):
    data_frame = {}
    for key, value in res.columns.columns.items():
        data_frame[key] = [_decode_any(a) for a in value.data]
    return data_frame
