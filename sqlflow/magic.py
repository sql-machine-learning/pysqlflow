import sys
import logging

from IPython.core.magic import Magics, magics_class, cell_magic, line_magic
from sqlflow.client import Client, _LOGGER

# For changing input cell syntax highlighting logic for the entire session
# http://stackoverflow.com/questions/28703626/ipython-change-input-cell-syntax-highlighting-logic-for-entire-session
from IPython.display import display_javascript

@magics_class
class SqlFlowMagic(Magics):
    """
    Provides the `%%sqlflow` magic
    """
    def __init__(self, shell):
        super(SqlFlowMagic, self).__init__(shell)
        self.client = Client()

    @cell_magic('sqlflow')
    def execute(self, line, cell):
        """Runs SQL statement

        :param line: The line magic
        :type line: str.
        :param cell: The cell magic
        :type cell: str.

        Example:

        >>> %%sqlflow SELECT *
        ... FROM mytable

        >>> %%sqlflow SELECT *
        ... FROM iris.iris limit 1
        ... TRAIN DNNClassifier
        ... WITH
        ...   n_classes = 3,
        ...   hidden_units = [10, 10]
        ... COLUMN sepal_length, sepal_width, petal_length, petal_width
        ... LABEL class
        ... INTO my_dnn_model;

        """
        return self.client.execute('\n'.join([line, cell]))

def load_ipython_extension(ipython):
    # Change input cell syntax highlighting to SQL
    js = "IPython.CodeCell.options_default.highlight_modes['magic_sql'] = {'reg':[/^%%sqlflow/]};"
    display_javascript(js, raw=True)

    magics = SqlFlowMagic(ipython)
    ipython.register_magics(magics)
