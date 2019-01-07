class Connection(object):
    """DB-API Connection to SQLFlow Server."""

    def __init__(self):
        raise NotImplementedError

    def close(self):
        """Close the connection."""
        raise NotImplementedError

    def commit(self):
        """Commit any pending transaction to the database."""
        raise NotImplementedError

    def cursor(self):
        """Return a new Cursor Object using the connection."""
        raise NotImplementedError

