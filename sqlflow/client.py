import sys
import os
import logging
import grpc

import google.protobuf.wrappers_pb2 as wrapper
from google.protobuf.timestamp_pb2 import Timestamp

import sqlflow.proto.sqlflow_pb2 as pb
import sqlflow.proto.sqlflow_pb2_grpc as pb_grpc


_LOGGER = logging.getLogger(__name__)
_OUT_HANDLER = logging.StreamHandler(sys.stdout)
_OUT_HANDLER.setLevel(logging.INFO)
_LOGGER.addHandler(_OUT_HANDLER)
_LOGGER.setLevel(logging.INFO)


class Rows:
    def __init__(self, column_names, rows_gen):
        self._column_names = column_names
        self._rows_gen = rows_gen
        self._rows = None

    def column_names(self):
        return self._column_names

    def rows(self):
        if self._rows is None:
            self._rows = [r for r in self._rows_gen()]
        return self._rows

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        self.rows()

        from prettytable import PrettyTable
        table = PrettyTable(self._column_names)
        for row in self._rows:
            table.add_row(row)
        return table.__str__()

    def to_dataframe(self):
        raise NotImplementedError


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
            if "SQLFLOW_SERVER" not in os.environ:
                raise ValueError("Can't find environment variable SQLFLOW_SERVER")
            server_url = os.environ["SQLFLOW_SERVER"]

        # FIXME(tonyyang-svail): change insecure_channel to secure_channel
        channel = grpc.insecure_channel(server_url)
        self._stub = pb_grpc.SQLFlowStub(channel)

    def execute(self, operation):
        """Run a SQLFlow operation
        """
        stream_response = self._stub.Run(pb.Request(sql=operation))
        first = next(stream_response)
        if first.WhichOneof('response') == 'message':
            _LOGGER.info(first.message.message)
            for res in stream_response:
                _LOGGER.info(res.message.message)
        else:
            column_names = [column_name for column_name in first.head.column_names]

            def rows_gen():
                for res in stream_response:
                    yield [self._decode_any(a) for a in res.row.data]
            return Rows(column_names, rows_gen)

    @classmethod
    def _decode_any(cls, any_message):
        """Decode a google.protobuf.any_pb2
        """
        try:
            message = next(getattr(wrapper, type_name)()
                           for type_name, desc in wrapper.DESCRIPTOR.message_types_by_name.items()
                           if any_message.Is(desc))
            any_message.Unpack(message)
            return message.value
        except StopIteration:
            if any_message.Is(pb.Row.Null.DESCRIPTOR):
                return None
            if any_message.Is(Timestamp.DESCRIPTOR):
                timestamp_message = Timestamp()
                any_message.Unpack(timestamp_message)
                return timestamp_message.ToDatetime()
            raise TypeError("Unsupported type {}".format(any_message))
