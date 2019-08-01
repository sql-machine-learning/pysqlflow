import os
import re
from datetime import datetime, timedelta


class EnvExpanderError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)

class EnvExpander(object):
    def __init__(self, environ=os.environ):
        self.environ = environ
        self.pattern_env = re.compile(r'\$\{(.*?)\}')
        # TODO(Yancey1989): support more date expression
        self.pattern_date_expr = re.compile(r"(yyyyMMdd)\Z|(yyyyMMdd)\s(\+|\-)\s(\d+)d")
        
    def _match_date_expr(self, expr):
        return re.match(self.pattern_date_expr, expr)

    def parse_bizdate(self, expr):
        bizdate = self.environ["BIZDATE"][:8]
        if not bizdate:
            raise EnvExpanderError("The date format ${yyyyMMdd +/- 1d} need set the OS environment variable ${BIZDATE}")
        dt = datetime.strptime(bizdate, "%Y%m%d")
        m = self._match_date_expr(expr)
        if m.groups()[0]:
            return dt.strftime("%Y%m%d") 
        else:
            if m.groups()[2] == "+":
                dt += timedelta(days=int(m.groups()[3]))
            elif m.groups()[2] == "-":
                dt -= timedelta(days=int(m.groups()[3]))
            else:
                raise EnvExpanderError("date format failed: {}".format(expr))
            return dt.strftime("%Y%m%d")

    def expand(self, sql):
        new_sql = sql
        for m in re.finditer(self.pattern_env, sql):
            if m.group(1) in self.environ:
                val = self.environ[m.group(1)]
                new_sql = new_sql.replace(m.group(0), val, 1)
            elif self._match_date_expr(m.group(1)):
                val = self.parse_bizdate(m.group(1))
                new_sql = new_sql.replace(m.group(0), val, 1)
            else:
                raise EnvExpanderError("Can not find the environment: {} in the runtime envionrment.".format(m.group(1)))
        return new_sql