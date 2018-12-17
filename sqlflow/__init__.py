from .sqlflow import *
from .sqlflow_magic import *


def load_ipython_extension(ipython):
    """
    Called when the extension is loaded.
    Args:
        ipython - (NotebookWebApplication): handle to the Notebook interactive shell instance.
    """
    ipython.register_magics(SQLFlowMagics)
