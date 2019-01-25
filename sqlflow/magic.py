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
    # - default displaylimit
    def __init__(self, shell):
        super(SqlFlowMagic, self).__init__(shell)
        self.client = Client(server_url='localhost:50051')

    @cell_magic('sqlflow')
    def execute(self, line, cell):
        """Runs SQL result against a sqlflow server, specified by server_url

        Example:

            %%sqlflow  SELECT * FROM mytable

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

        for res in self.client.execute('\n'.join([line, cell])):
            if isinstance(res, dict):
                self.print_table(res)
            elif isinstance(res, str):
                print(res)
            else:
                raise ValueError("can't print {}:{}".format(type(res), res))

    @staticmethod
    def print_table(table):
        print(table["column_names"])
        for row in table["rows"]:
            print(row)


def load_ipython_extension(ipython):
    magics = SqlFlowMagic(ipython)
    ipython.register_magics(magics)
