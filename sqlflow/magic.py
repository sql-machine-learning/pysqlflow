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
        self.client = Client()

    @cell_magic('sqlflow_query')
    def query(self, line, cell):
        """Query

        Example:

            %%sqlflow_query
            SELECT * FROM mytable
        """
        assert len(line) == 0
        return self.client.query(cell)

    @cell_magic('sqlflow_execute')
    def execute(self, line, cell):
        """Execute

        Example:
            %%sqlflow_execute
            DELETE ... FROM ... WHERE ...

            %%sqlflow_execute
            SELECT *
            FROM iris.iris limit 1
            TRAIN DNNClassifier
            WITH
              n_classes = 3,
              hidden_units = [10, 20]
            COLUMN sepal_length, sepal_width, petal_length, petal_width
            LABEL class
            INTO my_dnn_model;
        """
        assert len(line) == 0
        self.client.execute(cell)


def load_ipython_extension(ipython):
    magics = SqlFlowMagic(ipython)
    ipython.register_magics(magics)
