import os
import unittest
from sqlflow.env_expand import EnvExpander, EnvExpanderError 

class EnvExpanderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["BIZDATE"] = "20190731"
        os.environ["t1"] = "tablename"
        cls.expander = EnvExpander(os.environ)

    def test_expand(self):
        sql = "SELECT * from ${t1} where pt=${yyyyMMdd}"
        new_sql = self.expander.expand(sql)
        expected_sql = "SELECT * from tablename where pt=20190731"
        assert new_sql == expected_sql
    
    def test_bizdate_delta(self):
        sql = "SELECT * from ${t1} where pt=${yyyyMMdd + 1d}"
        new_sql = self.expander.expand(sql)
        expected_sql = "SELECT * from tablename where pt=20190801"
        assert new_sql == expected_sql
    
    def test_bizdate_arbitrary_space(self):
        sql = "SELECT * from ${t1} where pt=${yyyyMMdd+ 1d}"
        new_sql = self.expander.expand(sql)
        expected_sql = "SELECT * from tablename where pt=20190801"
        assert new_sql == expected_sql

    def test_expand_error(self):
        sql = "SELECT * from ${no_exists} where pt=${yyyyMMdd + 1d}"
        with self.assertRaises(EnvExpanderError):
            self.expander.expand(sql)

