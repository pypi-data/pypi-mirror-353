from __future__ import annotations  # Required for type hinting in class methods

from collections import defaultdict
from os.path import expanduser
from typing import Optional

import psycopg2
from psycopg2 import pool
from logger_local.MetaLogger import MetaLogger

from .constants_src import LOGGER_CONNECTOR_CODE_OBJECT
from .cursor import Cursor
from .utils import (get_sql_hostname, get_sql_password, get_sql_username, get_sql_port)

connections_pool = defaultdict(dict)
home = expanduser('~')


class Connector(metaclass=MetaLogger, object=LOGGER_CONNECTOR_CODE_OBJECT):
    @staticmethod
    def connect(schema_name: str, *, user: str = get_sql_username(), ignore_cache: bool = False) -> Connector:
        if ignore_cache and schema_name in connections_pool[user]:
            connections_pool[user].pop(schema_name)

        if connections_pool[user].get(schema_name):
            # Check if connection is still valid
            connector = None
            try:
                # Test if connection is still alive
                connections_pool[user][schema_name].connection.cursor().execute("SELECT 1")
                connector = connections_pool[user][schema_name]
            except (Exception, psycopg2.DatabaseError):
                # Reconnect if connection is closed
                try:
                    connections_pool[user][schema_name].connection.close()
                except:
                    pass
                connections_pool[user].pop(schema_name, None)
                connector = Connector(schema_name)
                connections_pool[user][schema_name] = connector
        else:
            connector = Connector(schema_name)
            connections_pool[user][schema_name] = connector

        return connector

    def __init__(self, schema_name: str, *,
                 host: str = get_sql_hostname(),
                 user: str = get_sql_username(),
                 password: str = get_sql_password(),
                 port: str = get_sql_port()) -> None:
        self.host = host
        self.schema = schema_name
        self.user = user
        self.password = password
        self.port = port
        
        # Checking host suffix
        if not (self.host.endswith("circ.zone") or self.host.endswith("circlez.ai")):
            self.logger.warning(
                f"Your POSTGRESQL_HOSTNAME={self.host} which is not what is expected")
        self.connection = None
        self._cursor = None
        self._connect_to_db()
        connections_pool[user][schema_name] = self

    def reconnect(self) -> None:
        # Called when the connection is lost
        self._connect_to_db()
        self._cursor = self.cursor(close_previous=True)
        self.set_schema(self.schema)

    def _connect_to_db(self):
        try:
            # PostgreSQL uses a database parameter instead of schema
            # We'll connect to the default database (usually 'postgres') and then set the schema
            self.connection = psycopg2.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port,
                dbname='postgres'  # Connect to default database
            )
            self.connection.autocommit = False  # Explicit transaction control
            self.logger.info(f"Connected to the database: {self.database_info()}")
            self._cursor = self.connection.cursor()
            self.set_schema(self.schema)
        except Exception as e:
            self.logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise

    def database_info(self) -> str:
        database_info_str = f"host={self.host}, user={self.user}, schema={self.schema}, port={self.port}"
        return database_info_str

    def close(self) -> None:
        try:
            if self._cursor:
                self._cursor.close()
                self.logger.info(f"Cursor closed successfully for schema: {self.schema}")
        except Exception as exception:
            self.logger.error(object={"exception": exception})
        connections_pool[self.user].pop(self.schema, None)
        if self.connection:
            try:
                self.connection.close()
                self.logger.info("Connection closed successfully.")
            except:
                pass

    def cursor(self, *, close_previous: bool = True, cache_previous: bool = False, dictionary: bool = None,
               buffered: bool = None, raw: bool = None,
               prepared: bool = None, named_tuple: bool = None, cursor_class=None) -> Cursor:
        # PostgreSQL doesn't support all the same cursor options as MySQL
        # We'll create a basic cursor and wrap it in our Cursor class
        cursor_instance = Cursor(self.connection.cursor())
        return cursor_instance

    def commit(self) -> None:
        self.connection.commit()

    def set_schema(self, new_schema: Optional[str]) -> None:
        if not new_schema:
            return
        if self.schema == new_schema:
            return

        if self._cursor and self.connection:
            try:
                # First check if schema exists
                self._cursor.execute(f"SELECT schema_name FROM information_schema.schemata WHERE schema_name = %s", (new_schema,))
                if not self._cursor.fetchone():
                    # Create schema if it doesn't exist
                    self._cursor.execute(f'CREATE SCHEMA IF NOT EXISTS "{new_schema}"')
                    self.connection.commit()
                
                # Set search path to use the schema
                self._cursor.execute(f'SET search_path TO "{new_schema}", public')
                connections_pool[self.user][new_schema] = self
                connections_pool[self.user].pop(self.schema, None)
                self.schema = new_schema
                self.logger.info(f"Switched to schema: {new_schema}")
            except Exception as e:
                self.logger.error(f"Error setting schema: {e}")
                raise
        else:
            raise Exception(
                "Connection is not established. The database will be used on the next connect.")

    def rollback(self):
        self.connection.rollback()

    def start_transaction(self):
        # PostgreSQL doesn't have an explicit start_transaction method
        # Transactions begin automatically when you execute a query
        pass