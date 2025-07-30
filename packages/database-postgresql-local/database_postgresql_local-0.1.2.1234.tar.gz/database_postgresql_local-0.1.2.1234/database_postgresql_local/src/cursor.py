from typing import Any

from logger_local.MetaLogger import MetaLogger
from psycopg2.extensions import cursor as PostgreSQLCursor
import psycopg2
from .constants_src import LOGGER_CONNECTOR_CODE_OBJECT

# PostgreSQL version
POSTGRESQL_VERSION = psycopg2.__version__


def version_tuple(version):
    return tuple(map(int, version.split(".")))  # Converts "2.9.5" → (2, 9, 5)


class Cursor(metaclass=MetaLogger, object=LOGGER_CONNECTOR_CODE_OBJECT):
    def __init__(self, cursor: PostgreSQLCursor) -> None:
        self.cursor = cursor
        self.__is_closed = False

    def execute(self, sql_statement: str, sql_parameters: tuple | list = None, multi: bool = False) -> None:
        # PostgreSQL doesn't support the multi parameter
        # Convert MySQL-style backtick quotes to PostgreSQL double quotes
        sql_statement = sql_statement.replace('`', '"')
        
        if sql_parameters:
            # PostgreSQL uses %s for all parameter types
            formatted_sql = sql_statement
            sql_parameters_str = ", ".join(str(param) for param in sql_parameters)
        else:
            formatted_sql = sql_statement
            sql_parameters_str = "None"
            
        self.logger.info(object={
            "formatted_sql": formatted_sql.replace("\n", " "),
            "sql_parameters": sql_parameters_str,
            "sql_statement": sql_statement.replace("\n", " ")
        })
        
        try:
            self.cursor.execute(sql_statement, sql_parameters)
        except Exception as e:
            self.logger.error(f"Error executing SQL: {e}")
            raise

    def executemany(self, sql_statement: str, sql_parameters: tuple | list = None) -> None:
        try:
            # Convert MySQL-style backtick quotes to PostgreSQL double quotes
            sql_statement = sql_statement.replace('`', '"')
            
            if sql_parameters:
                sql_parameters_str = str(sql_parameters)
                formatted_sql = sql_statement
            else:
                formatted_sql = sql_statement
                sql_parameters_str = "None"
                
            self.logger.info(object={
                "formatted_sql": formatted_sql.replace("\n", " "),
                "sql_parameters": sql_parameters_str,
                "sql_statement": sql_statement.replace("\n", " ")
            })
            
            self.cursor.executemany(sql_statement, sql_parameters)
        except Exception as e:
            self.logger.warning('Unable to execute statement', object={
                "sql_statement": sql_statement,
                "sql_parameters": sql_parameters,
                "error": str(e)
            })
            raise

    def fetchall(self) -> Any:
        result = self.cursor.fetchall()
        return result

    def fetchmany(self, size: int) -> Any:
        result = self.cursor.fetchmany(size)
        return result

    def fetchone(self) -> Any:
        result = self.cursor.fetchone()
        return result

    def description(self) -> list[tuple]:
        """Returns description of columns in a result

        This property returns a list of tuples describing the columns
        in a result set. A tuple is described as follows::

                (column_name,
                 type,
                 None,
                 None,
                 None,
                 None,
                 null_ok)
        """
        result = self.cursor.description
        return result

    def column_names(self) -> tuple:
        """Returns the column names from the last query"""
        if self.cursor.description:
            return tuple(desc[0] for desc in self.cursor.description)
        return tuple()

    def lastrowid(self) -> int | None:
        """Returns the value generated for an AUTO_INCREMENT column by the previous INSERT or UPDATE statement."""
        # PostgreSQL doesn't have a direct lastrowid property
        # We need to use RETURNING clause in the SQL or currval() function
        # This is a simplified implementation that may need to be adjusted based on actual usage
        try:
            self.cursor.execute("SELECT lastval()")
            result = self.cursor.fetchone()[0]
            return result
        except Exception as e:
            self.logger.warning(f"Error getting lastrowid: {e}")
            return None

    def get_affected_row_count(self) -> int:
        """Returns the number of rows produced or affected"""
        result = self.cursor.rowcount
        return result

    def get_last_executed_statement(self) -> str:
        # PostgreSQL cursor doesn't store the last executed statement
        # We would need to track this ourselves
        return "Statement not available"

    def close(self) -> None:
        if self.__is_closed:
            self.logger.warning('Cursor is already closed')
        try:
            self.cursor.close()
            self.__is_closed = True
        except Exception as exception:
            self.logger.error('Unable to close cursor', object={"exception": exception})

    def is_closed(self) -> bool:
        result = self.__is_closed
        return result