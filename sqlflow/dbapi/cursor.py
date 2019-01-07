class Cursor(object):
    """DB-API Cursor to SQLFlow."""

    def __init__(self):
        self.description = None
        self.rowcount = None
        raise NotImplementedError

    def close(self):
        """Close the curosr now."""
        raise NotImplementedError

    def execute(self, operation):
        """Prepare and execute a database operation."""
        raise NotImplementedError

    def executemany(self, operation, seq_of_parameters):
        """Prepare a database operation and then execute it
        against all parameter sequences or mappings found in
        the sequence seq_of_parameters."""
        raise NotImplementedError

    def fetchone(self):
        """Fetch the next row of a query result set, returning
        a single sequence, or None when no more data is available."""
        raise NotImplementedError

    def fetchmany(self):
        """Fetch the next set of rows of a query result, returning
        a sequence of sequences (e.g. a list of tuples). An empty
        sequence is returned when no more rows are available."""
        raise NotImplementedError

    def fetchall(self):
        """Fetch all (remaining) rows of a query result, returning
        them as a sequence of sequences (e.g. a list of tuples).
        Note that the cursor's arraysize attribute can affect the
        performance of this operation."""
        raise NotImplementedError

    def arraysize(self):
        """This read/write attribute specifies the number of rows
        to fetch at a time with .fetchmany(). It defaults to 1 meaning
        to fetch a single row at a time."""
        raise NotImplementedError

    def setinputsizes(self, sizes):
        """This can be used before a call to .execute*() to predefine
        memory areas for the operation's parameters."""
        raise NotImplementedError

    def setoutputsize(size):
        """Set a column buffer size for fetches of large columns
        (e.g. `LONG`s, `BLOB`s, etc.). The column is specified as an
        index into the result sequence. Not specifying the column will
        set the default size for all large columns in the cursor."""
        raise NotImplementedError

