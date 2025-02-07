#sqldb_access

"""
pip install pyodbc
pip install sqlalchemy
pip install sqlalchemy-access
pip list
    greenlet          3.1.1
    pip               24.3.1
    pyodbc            5.1.0
    pywin32           308
    SQLAlchemy        2.0.36
    sqlalchemy-access 2.0.3
    typing_extensions 4.12.2
"""

import pyodbc as py1
from pyodbc import (
    DatabaseError    as pyo_DatabaseError,
    DataError        as pyo_DataError,
    OperationalError as pyo_OperationalError,
    ProgrammingError as pyo_ProgrammingError,
)
from lib.sqldb import SQLDB
from sqlalchemy import (
    and_             as sa_and,
    create_engine    as sa_create_engine, 
    delete           as sa_delete,
    insert           as sa_insert,
    MetaData         as sa_MetaData, 
    select           as sa_select,
    Table            as sa_Table, 
    update           as sa_update,
)
from sqlalchemy.exc import (
    OperationalError as sa_OperationalError,
    ProgrammingError as sa_ProgrammingError,
)
from sqlalchemy.ext.automap import automap_base;
from sqlalchemy.orm import (
    sessionmaker,
)

class SQLDB_Access(SQLDB):
    """A class to represent a class of sqldb for Microsoft Access"""
    
    def __init__(self, databasename: str, uses_orm: bool, echo_sql: bool) -> None:
        """Initialize the access database connector"""
        super().__init__(databasename)
        self.uses_orm = uses_orm
        odbc_conn_str = f"DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={databasename};"
        self.__connection_string = f"access+pyodbc:///?odbc_connect={odbc_conn_str}"
        print(f"\nDatabase: {self.databasename}")

        try:
            # Create SQLAlchemy engine
            self.engine = sa_create_engine(self.__connection_string, echo=echo_sql)
            
            # Create ORM or Core connection
            if self.uses_orm:
                self.metadata = sa_MetaData()
                self.base = automap_base(metadata=self.metadata)
                self.base.prepare(autoload_with=self.engine)
                Session = sessionmaker(bind=self.engine)
                self.session = Session()
            else:
                self.metadata = sa_MetaData()
                self.metadata.reflect(bind=self.engine)
        except sa_OperationalError as e:
            print("Connection error:", e)
        except sa_ProgrammingError as e:
            print("SQL error:", e)
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
        if self.engine:
            self.engine.dispose()
            self.engine = None

    def get_table_definition(self, table_name:str) -> sa_Table:
        """use reflection to get table definition from database engine"""
        if self.uses_orm:
            return getattr(self.base.classes, table_name)
        else:
            return sa_Table(table_name, self.metadata, autoload_with = self.engine)
    