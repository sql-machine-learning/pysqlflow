import grpc
from cursor import Cursor

class Connection(object):
    """DB-API Connection to SQLFlow Server."""

    def __init__(self, host):
        #TODO(tonyyang-svail): add credentials
        self._channel = grpc.insecure_channel(host)

    def close(self):
        """Close the connection."""
        self._channel = None

    def commit(self):
        """No-op."""

    def cursor(self):
        """Return a new Cursor Object using the connection."""
        return Cursor(self._channel)

