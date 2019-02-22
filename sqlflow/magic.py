from IPython.core.magic import Magics, magics_class, cell_magic, line_magic
from sqlflow.client import Client

@magics_class
class SqlFlowMagic(Magics):
    """Runs SQL statement

    Provides the %%sqlflow magic
    """
    def __init__(self, shell, server_url):
        super(SqlFlowMagic, self).__init__(shell)
        self.client = Client(server_url)

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
        return self.client.execute('\n'.join([line, cell]))

def load_ipython_extension(ipython):
    # FIXME(tony): remove hard code server url
    magics = SqlFlowMagic(ipython, server_url="localhost:50051")
    ipython.register_magics(magics)
