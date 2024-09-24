#sqldb_access

import pyodbc as py1
from pyodbc import (
    DatabaseError    as pyo_DatabaseError,
    DataError        as pyo_DataError,
    OperationalError as pyo_OperationalError,
    ProgrammingError as pyo_ProgrammingError,
)
from lib.sqldb import SQLDB

class SQLDB_Access(SQLDB):
    """A class to represent a class of sqldb for Microsoft Access"""
    
    def __init__(self, databasename):
        """Initialize the access database connector"""
        super().__init__(databasename)
        self.__connection_string = r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};DBQ='+self.databasename
        print(f"database: {self.databasename}")

        try:
            self.__connection = py1.connect(self.__connection_string)
            self.cursor = self.__connection.cursor()
        except py1.DatabaseError:
            raise pyo_DatabaseError
        except py1.DataError:
            raise pyo_DataError
        except py1.OperationalError:
            raise pyo_OperationalError
        except py1.ProgrammingError:
            raise pyo_ProgrammingError
        except Exception:
            raise Exception

    def close(self) -> None:
        self.__connection.close()
