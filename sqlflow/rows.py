

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
