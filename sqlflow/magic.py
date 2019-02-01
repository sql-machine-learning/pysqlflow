from IPython.core.magic import Magics, magics_class, cell_magic, line_magic
from sqlflow.client import Client


@magics_class
class SqlFlowMagic(Magics):
    """Runs SQL statement

    Provides the %%sqlflow magic
    """

    # TODO(tony): add config method such as
    # - default server url
    # - default credential
    # - default display limit
    def __init__(self, shell):
        super(SqlFlowMagic, self).__init__(shell)
        self.client = Client()

    class Table:
        def __init__(self, tables):
            self._tables = tables

        # This method will be called by ipython to display Job
        def __repr__(self):
            from prettytable import PrettyTable
            t = PrettyTable(self._tables[0]["column_names"])
            for table in self._tables:
                for row in table["rows"]:
                    t.add_row(row)
            return t.__str__()

        @staticmethod
        def print_table(table):
            from prettytable import PrettyTable
            t = PrettyTable(table["column_names"])
            for row in table["rows"]:
                t.add_row(row)
            return t

    @cell_magic('sqlflow')
    def execute(self, line, cell):
        """Runs SQL result against a sqlflow server, specified by server_url

        Example:

            %%sqlflow SELECT * FROM mytable

            %%sqlflow SELECT *
            FROM iris.iris limit 1
            TRAIN DNNClassifier
            WITH
              n_classes = 3,
              hidden_units = [10, 20]
            COLUMN sepal_length, sepal_width, petal_length, petal_width
            LABEL class
            INTO my_dnn_model;
        """
        command = '\n'.join([line, cell])

        tables = []
        # This method will be called by ipython to display Job
        for res in self.client.execute(command):
            if isinstance(res, dict):
                tables.append(res)
            elif isinstance(res, str):
                print(res)
            else:
                raise ValueError("can't print {}:{}".format(type(res), res))

        if tables:
            return SqlFlowMagic.Table(tables=tables)


def load_ipython_extension(ipython):
    magics = SqlFlowMagic(ipython)
    ipython.register_magics(magics)
