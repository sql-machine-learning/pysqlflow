from IPython.core.magic import Magics, magics_class, cell_magic, line_magic


@magics_class
class SqlFlowMagic(Magics):
    """Runs SQL statement

    Provides the %%sqlflow magic
    """


    # TODO(tony): add config method such as
    # - default server url
    # - default credential
    # - default displaylimit
    def __int__(self):
        pass

    @line_magic('sqlflow')
    def execute(self, line):
        """Runs SQL result against a sqlflow server, specified by server_url

        Example:

            %%sqlflow localhost:50051
            SELECT * FROM mytable
        """
        # TODO(tony): add client logic

        return line


def load_ipython_extension(ip):
    ip.register_magics(SqlFlowMagic)
