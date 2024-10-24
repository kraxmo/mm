#sqldb.py

class SQLDB():
    class BadConnection(Exception):
        pass

    def __init__(self, databasename: str, autocommit=None):
        self.databasename = databasename
        if autocommit is None:
            self.autocommit = True
        else:
            self.autocommit = autocommit
            
        self.__connection = None
