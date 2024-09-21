#sqldb.py

class SQLDB():
    class BadConnection(Exception):
        pass

    def __init__(self, databasename, autocommit=True):
        self.databasename = databasename
        self.autocommit   = autocommit
