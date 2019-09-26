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
        return self.to_dataframe().__repr__()

    def _repr_html_(self):
        return self.to_dataframe()._repr_html_()

    def to_dataframe(self):
        """Convert Rows to pandas.Dataframe

        :return: pandas.Dataframe
        """
        # Fetch all the rows to self._rows
        for r in self.rows():
            pass
        import pandas as pd
        return pd.DataFrame(self._rows, columns=self._column_names)

