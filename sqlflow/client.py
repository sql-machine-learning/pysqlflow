import sys
import logging

import grpc
import google.protobuf.wrappers_pb2 as wrapper

import sqlflow.proto.sqlflow_pb2 as pb
import sqlflow.proto.sqlflow_pb2_grpc as pb_grpc

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
_LOGGER = logging.getLogger()


class Rows:
    def __init__(self, rows_gen):
        rows = [r for r in rows_gen()]
        if rows:
            self._column_names = rows[0]
            self._rows = rows[1:]
        else:
            self._column_names = None
            self._rows = None

    def column_names(self):
        return self._column_names

    def rows(self):
        return self._rows

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        if self._rows:
            from prettytable import PrettyTable
            table = PrettyTable(self._column_names)
            for row in self._rows:
                table.add_row(row)
            return table.__str__()
        return "[]"

    def to_dataframe(self):
        raise NotImplementedError


class Client:
    def __init__(self, server_url):
        """A minimum client that issues queries to and fetch results/logs from sqlflowserver.

        Args:
            server_url(str):    sqlflowserver url.

        Raises:
            KeyError:
                Raised if SQLFLOW_SERVER is not specified as environment variable
        """
        # FIXME(tonyyang-svail): change insecure_channel to secure_channel
        channel = grpc.insecure_channel(server_url)
        self._stub = pb_grpc.SQLFlowStub(channel)

    def execute(self, operation):
        """Run a SQLFlow operation
        """
        def rows_gen():
            for res in self._stub.Run(pb.Request(sql=operation)):
                if res.WhichOneof('response') == 'message':
                    _LOGGER.info(res.message.message)
                elif res.WhichOneof('response') == 'head':
                    yield [column_name for column_name in res.head.column_names]
                else:
                    yield [self._decode_any(a) for a in res.row.data]
        return Rows(rows_gen)

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
            raise TypeError("Unsupported type {}".format(any_message))
