"""Client for interacting with the SQLFlow Server API."""

import os
import logging
import grpc
import google.protobuf.wrappers_pb2 as wrapper

import sqlflow.proto.sqlflow_pb2 as pb
import sqlflow.proto.sqlflow_pb2_grpc as pb_grpc

_LOGGER = logging.getLogger(__name__)


class Client:
    def __init__(self, server_url=None):
        """A minimum client that issues queries to and fetch results/logs from sqlflowserver.

        Args:
            server_url(str):    sqlflowserver url. If None, read value from environment
                                variable SQLFLOW_SERVER

        Raises:
            KeyError:
                Raised if SQLFLOW_SERVER is not specified as environment variable
        """
        if server_url is None:
            try:
                server_url = os.environ["SQLFLOW_SERVER"]
            except KeyError:
                _LOGGER.error("Please set system variable SQLFLOW_SERVER")
                raise

        channel = grpc.insecure_channel(server_url)
        self._stub = pb_grpc.SQLFlowStub(channel)

    def execute(self, operation):
        """Run a SQLFlow operation

        Argument:
            operation(str): SQL query to be executed.

        Returns:
            Generator: generates the response of the server
        """
        for res in self._stub.Run(pb.RunRequest(sql=operation)):
            if res.WhichOneof('response') == 'messages':
                for message in res.messages.messages:
                    yield message
            else:
                yield _decode_protobuf(res)


SUPPORTED_TYPES = (wrapper.BoolValue, wrapper.Int64Value, wrapper.DoubleValue)


def _decode_any(any_message):
    try:
        message = next(t() for t in SUPPORTED_TYPES if any_message.Is(t.DESCRIPTOR))
        any_message.Unpack(message)
        return message.value
    except StopIteration:
        raise TypeError("Unsupported type {}".format(any_message))


def _decode_protobuf(res):
    data_frame = {}
    for key, value in res.columns.columns.items():
        data_frame[key] = [_decode_any(a) for a in value.data]
    return data_frame
