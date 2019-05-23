import os
import logging
import grpc

import google.protobuf.wrappers_pb2 as wrapper
from google.protobuf.timestamp_pb2 import Timestamp

import sqlflow.proto.sqlflow_pb2 as pb
import sqlflow.proto.sqlflow_pb2_grpc as pb_grpc


_LOGGER = logging.getLogger(__name__)


class Rows:
    def __init__(self, column_names, rows_gen):
        """Query result of sqlflow.client.Client.execute

        :param column_names: column names
        :type column_names: list[str].
        :param rows_gen: rows generator
        :type rows_gen: generator
        """
        self._column_names = column_names
        self._rows_gen = rows_gen
        self._rows = None

    def column_names(self):
        """Column names

        :return: list[str]
        """
        return self._column_names

    def rows(self):
        """Rows

        Example:

        >>> [r for r in rows.rows()]

        :return: list generator
        """
        if self._rows is None:
            self._rows = []
            for row in self._rows_gen():
                self._rows.append(row)
                yield row
        else:
            for row in self._rows:
                yield row

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        from prettytable import PrettyTable
        table = PrettyTable(self._column_names)
        for row in self.rows():
            table.add_row(row)
        return table.__str__()

    def to_dataframe(self):
        """Convert Rows to pandas.Dataframe

        :return: pandas.Dataframe
        """
        raise NotImplementedError


class Client:
    def __init__(self, server_url=None):
        """A minimum client that issues queries to and fetch results/logs from sqlflowserver.

        :param server_url: sqlflowserver url. If None, read value from
                           environment variable SQLFLOW_SERVER.
        :type server_url: str.
        :raises: ValueError

        Example:

        >>> client = sqlflow.Client(server_url="localhost:50051")

        """
        if server_url is None:
            if "SQLFLOW_SERVER" not in os.environ:
                raise ValueError("Can't find environment variable SQLFLOW_SERVER")
            server_url = os.environ["SQLFLOW_SERVER"]

        # FIXME(tonyyang-svail): change insecure_channel to secure_channel
        channel = grpc.insecure_channel(server_url)
        self._stub = pb_grpc.SQLFlowStub(channel)

    def execute(self, operation):
        """Run a SQL statement

        :param operation: SQL statement to be executed.
        :type operation: str.

        :returns: sqlflow.client.Rows

        Example:

        >>> client.execute("select * from iris limit 1")

        """
        try:
            stream_response = self._stub.Run(pb.Request(sql=operation))
            return self.display(stream_response)
        except grpc.RpcError as e:
            _LOGGER.error("%s\n%s", e.code(), e.details())
            
    @classmethod
    def display(cls, stream_response):
        """Display stream response like log or table.row"""
        first = next(stream_response)
        if first.WhichOneof('response') == 'message':
            _LOGGER.info(first.message.message)
            for res in stream_response:
                _LOGGER.info(res.message.message)
        else:
            column_names = [column_name for column_name in first.head.column_names]

            def rows_gen():
                for res in stream_response:
                    yield [cls._decode_any(a) for a in res.row.data]
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
