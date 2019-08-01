import os
import sys
import logging
import grpc
import re

import google.protobuf.wrappers_pb2 as wrapper
from google.protobuf.timestamp_pb2 import Timestamp

import sqlflow.proto.sqlflow_pb2 as pb
import sqlflow.proto.sqlflow_pb2_grpc as pb_grpc

from sqlflow.env_expand import EnvExpander, EnvExpanderError

_LOGGER = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
_LOGGER.setLevel(logging.INFO)
_LOGGER.addHandler(handler)

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
    def __init__(self, server_url=None, ca_crt=None):
        """A minimum client that issues queries to and fetch results/logs from sqlflowserver.

        :param server_url: sqlflowserver url. If None, read value from
                           environment variable SQLFLOW_SERVER.
        :type server_url: str.

        :param ca_crt: Path to CA certificates of SQLFlow client, if None,
                       try to find the file from the environment variable:
                       SQLFLOW_CA_CRT, otherwise using insecure client.
        :type ca_crt: str.

        :raises: ValueError

        Example:
        >>> client = sqlflow.Client(server_url="localhost:50051")

        """
        if server_url is None:
            if "SQLFLOW_SERVER" not in os.environ:
                raise ValueError("Can't find environment variable SQLFLOW_SERVER")
            server_url = os.environ["SQLFLOW_SERVER"]

        self._stub = pb_grpc.SQLFlowStub(self.new_rpc_channel(server_url, ca_crt))
        self._expander = EnvExpander(os.environ)

    def new_rpc_channel(self, server_url, ca_crt):
        if ca_crt is None and "SQLFLOW_CA_CRT" not in os.environ:
            # client would connect SQLFLow gRPC server with insecure mode.
            channel = grpc.insecure_channel(server_url) 
        else:
            if ca_crt is None:
                ca_crt = os.environ["SQLFLOW_CA_CRT"]
            with open(ca_crt, "rb") as f:
                creds = grpc.ssl_channel_credentials(f.read())
            channel = grpc.secure_channel(server_url, creds)
        return channel

    def sql_request(self, sql):
        token = os.getenv("SQLFLOW_USER_TOKEN", "")
        db_conn_str = os.getenv("SQLFLOW_DATASOURCE", "")
        exit_on_submit_env = os.getenv("SQLFLOW_EXIT_ON_SUBMIT", "True")
        user_id = os.getenv("SQLFLOW_USER_ID", "")
        if exit_on_submit_env.isdigit():
            exit_on_submit = bool(int(exit_on_submit_env))
        else:
            exit_on_submit = exit_on_submit_env.lower() == "true"
        se = pb.Session(token=token, db_conn_str=db_conn_str, exit_on_submit=exit_on_submit, user_id=user_id)
        try:
            sql = self._expander.expand(sql)
        except Exception as e:
            _LOGGER.error("")
        return pb.Request(sql=sql, session=se)

    def execute(self, operation):
        """Run a SQL statement

        :param operation: SQL statement to be executed.
        :type operation: str.

        :returns: sqlflow.client.Rows

        Example:

        >>> client.execute("select * from iris limit 1")

        """
        try:
            stream_response = self._stub.Run(self.sql_request(operation))
            return self.display(stream_response)
        except grpc.RpcError as e:
            _LOGGER.error("%s\n%s", e.code(), e.details())
        except EnvExpanderError as e:
            _LOGGER.error(e.message)
            
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

