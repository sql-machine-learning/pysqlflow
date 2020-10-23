import asyncio
import json
import logging
import os
import ssl
import sys
import threading

import dotenv
import nest_asyncio
from IPython.core.magic import Magics, cell_magic, line_magic, magics_class
# For changing input cell syntax highlighting logic for the entire session
# http://stackoverflow.com/questions/28703626/ipython-change-input-cell-syntax-highlighting-logic-for-entire-session
from IPython.display import display_javascript
from tornado import httpclient

from sqlflow.client import _LOGGER, Client

nest_asyncio.apply()


@magics_class
class SqlFlowMagic(Magics):
    """
    Provides the `%%sqlflow` magic
    """

    def __init__(self, shell):
        super(SqlFlowMagic, self).__init__(shell)
        self.client = None

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
        self.lazy_load()
        return self.client.execute('\n'.join([line, cell]))

    def lazy_load(self):
        self.create_db_on_demaond()
        if not self.client:
            self.client = Client()

    def get_ssl_ctx(self):
        ca_path = os.getenv("SQLFLOW_PLAYGROUND_SERVER_CA")
        client_key = os.getenv("SQLFLOW_PLAYGROUND_CLIENT_KEY")
        client_cert = os.getenv("SQLFLOW_PLAYGROUND_CLIENT_CERT")
        if not (ca_path and client_cert and client_key):
            raise ValueError("Certification files is not configured"
                             "for this client")
        ssl_ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ssl_ctx.load_cert_chain(client_cert, client_key)
        ssl_ctx.load_verify_locations(ca_path)
        ssl_ctx.check_hostname = False

        return ssl_ctx

    def create_db_on_demaond(self):
        """If we are connecting to a Sqlflow Playground Service,
        we need to ask the server to get DB and SQLFlow resource.
        In this case, we do not specify SQLFLOW_DATASOURCE, instead
        we should specify the SQLFLOW_PLAYGROUND_SERVRE
        variable. On first time %%sqlflow command is executed,
        we check if the DB connection is retrived from the server,
        and create a new one if we haven't done it.

        Client should be secured by a certification file. Use
        SQLFLOW_PLAYGROUND_CLIENT_KEY and SQLFLOW_PLAYGROUND_CLIENT_CERT
        and SQLFLOW_PLAYGROUND_SERVER_CA to specify them. These
        files can be got from SQLFlow Playground Server maintainer.
        """

        if os.getenv("SQLFLOW_DATASOURCE"):
            return
        # If no datasource is given, try to connect to
        # our playground server to create one
        user_id_env = os.getenv("SQLFLOW_PLAYGROUND_USER_ID_ENV")
        user_id = os.getenv(user_id_env)
        server = os.getenv("SQLFLOW_PLAYGROUND_SERVRE")
        if not server:
            raise ValueError("Neither a datasource nor a "
                             "playground server is given.")
        if not user_id:
            raise ValueError(
                "Need to specify a SQLFLOW_PLAYGROUND_USER_ID_ENV")
        # give user some hint, this may take a few seconds
        from IPython.core.display import display, HTML
        display(HTML("Loading resource..."))
        # create db pod on playground service
        body = {
            "user_id": user_id,
        }
        ssl_ctx = self.get_ssl_ctx()
        http = httpclient.HTTPClient()
        try:
            req = httpclient.HTTPRequest(
                "%s/api/create_db" % server, method="POST",
                ssl_options=ssl_ctx, body=json.dumps(body))
            resp = http.fetch(req)
            result = json.loads(resp.body)
            os.environ["SQLFLOW_DATASOURCE"] = result["data_source"]

            # server can kill the db resource
            # if no heart beat is coming for a while
            self.setup_heart_beat(server, user_id)
        except Exception as e:
            raise RuntimeError("Can't get SQLFlow resource, because of", e)
        finally:
            http.close()

    def setup_heart_beat(self, server, user_id):
        http = httpclient.HTTPClient()
        ssl_ctx = self.get_ssl_ctx()

        async def report():
            while True:
                try:
                    url = "%s/api/heart_beat?user_id=%s" % (server, user_id)
                    http.fetch(url, ssl_options=ssl_ctx)
                    await asyncio.sleep(10 * 60)
                except:
                    pass
        asyncio.ensure_future(report())


def load_ipython_extension(ipython):
    if os.getenv("SQLFLOW_JUPYTER_ENV_PATH"):
        dotenv.load_dotenv(os.environ["SQLFLOW_JUPYTER_ENV_PATH"])

    # Change input cell syntax highlighting to SQL
    js = "IPython.CodeCell.options_default.highlight_modes['magic_sql'] = {'reg':[/^%%sqlflow/]};"
    display_javascript(js, raw=True)

    magics = SqlFlowMagic(ipython)
    ipython.register_magics(magics)
