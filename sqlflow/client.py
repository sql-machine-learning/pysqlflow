import os
import logging
import grpc
import sqlparse

import google.protobuf.wrappers_pb2 as wrapper
from google.protobuf.timestamp_pb2 import Timestamp

import sqlflow.proto.sqlflow_pb2 as pb
import sqlflow.proto.sqlflow_pb2_grpc as pb_grpc


_LOGGER = logging.getLogger(__name__)


class Rows:
    def __init__(self, column_names, rows_gen, rows = None):
        """Query result of sqlflow.client.Client.execute

        :param column_names: column names
        :type column_names: list[str].
        :param rows_gen: rows generator
        :type rows_gen: generator
        :param rows: rows data. if rows is None, rows_gen will be used to gen rows.
        :type rows: list[str]
        """
        self._column_names = column_names
        self._rows_gen = rows_gen
        self._rows = rows

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
        """Run one or several SQL statement

        :param operation: SQL statement to be executed. Split by ";"
        :type operation: str.

        :returns: list of sqlflow.client.Rows. One Rows for each SQL statement.

        Example:

        >>> client.execute("select * from iris limit 1")
        >>> client.execute("select * from iris limit 1; select count(*) from iris")

        """
        return_rows = []
        for one_operation in sqlparse.split(operation):
            if not one_operation.strip():
                continue
            stream_response = self._stub.Run(pb.Request(sql=one_operation))
            last_column_names = None
            column_data = []
            for res in stream_response:
                first = res
                if first.WhichOneof('response') == 'message':
                    _LOGGER.info(first.message.message)
                elif first.WhichOneof('response') == 'head':
                    if last_column_names:
                        raise TypeError("Wrong data. The stream response has two header".format(first))
                    last_column_names = [column_name for column_name in first.head.column_names]
                elif first.WhichOneof('response') == 'row':
                    if not last_column_names:
                        raise TypeError("Wrong data. The row without column name".format(first))
                    column_data.append([self._decode_any(a) for a in res.row.data])
                else :
                    raise TypeError("Unsupported response {}".format(first))

            if last_column_names:
                return_rows.append(Rows(last_column_names, None, column_data))
        if len(return_rows) > 0:
            return return_rows; # TODO huangxi.hx better display on jupyter

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
