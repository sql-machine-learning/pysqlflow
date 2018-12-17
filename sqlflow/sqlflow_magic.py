from IPython.core.magic import (Magics, magics_class, line_cell_magic)


@magics_class
class SQLFlowMagics(Magics):
    """Implements the SQLFlow magic for ipython notebooks.
    The supported syntax is:
      %%sqlflow <command> [<args>]
      <cell>
    or:
      %sqlflow <command> [<args>]
    Use %sql --help for a list of commands, or %sql <command> --help for help
    on a specific command.
    """
    @line_cell_magic
    def sqlflow(self, line, cell=None):
        raise NotImplementedError()
