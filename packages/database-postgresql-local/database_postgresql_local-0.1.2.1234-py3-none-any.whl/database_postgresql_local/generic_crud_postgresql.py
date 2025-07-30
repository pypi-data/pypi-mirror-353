from datetime import datetime, timezone
from functools import lru_cache
from typing import Any, Optional

import psycopg2
from database_infrastructure_local.number_generator import NumberGenerator
from database_infrastructure_local.generic_crud_abstract import GenericCrudAbstract
from database_infrastructure_local.constants import DEFAULT_SQL_SELECT_LIMIT
from logger_local.MetaLogger import ABCMetaLogger
from user_context_remote.user_context import UserContext
from python_sdk_remote.our_object import OurObject

from .connector import Connector
from .constants_src import CRUD_POSTGRESQL_CODE_LOGGER_OBJECT
from .cursor import Cursor
from .table_definition import table_definition
from .utils import (detect_if_is_test_data, generate_id_column_name,
                    generate_table_name, generate_view_name,
                    get_entity_type_id_by_table_name, get_where_params,
                    process_insert_data_dict, process_update_data_dict,
                    process_upsert_data_dict,
                    replace_view_with_table, validate_none_select_table_name,
                    validate_select_table_name, validate_single_clause_value,
                    where_skip_null_values, insert_is_undelete,
                    is_column_in_table,
                    is_end_timestamp_in_table, get_table_columns,
                    group_list_by_columns,
                    process_select_data_dict,
                    generate_where_clause_for_ignore_duplicate,
                    fix_select_clause_value, fix_where_clause_value)


class GenericCrudPostgresql(GenericCrudAbstract, metaclass=ABCMetaLogger,
                            object=CRUD_POSTGRESQL_CODE_LOGGER_OBJECT):
    """A class that provides generic CRUD functionality for PostgreSQL databases.
    There are 4 main functions to create, read, update, and delete data from the database.
    The rest of the functions are helper functions or wrappers around the main functions."""

    def __init__(self, *, default_schema_name: str,
                 default_table_name: str = None,
                 default_view_table_name: str = None,
                 default_view_with_deleted_and_test_data: str = None,
                 default_column_name: str = None,
                 default_select_clause_value: str = "*",
                 default_where: str = None,
                 is_test_data: bool = False) -> None:
        """Initializes the GenericCrudPostgresql class. If a connection is not provided, a new connection will be created."""
        self.default_schema_name = default_schema_name
        # We do not need a connection per schema, and it makes terrible performance.
        # In special cases, you can always use set_schema.
        self.connection = Connector.connect(schema_name=default_schema_name)
        self._cursor = self.connection.cursor()
        self.default_table_name = default_table_name or generate_table_name(default_schema_name)
        self.default_view_table_name = default_view_table_name \
            or generate_view_name(
                self.default_table_name)
        self.default_column_name = default_column_name \
            or generate_id_column_name(self.default_table_name)
        self.default_view_with_deleted_and_test_data = \
            default_view_with_deleted_and_test_data
        self.default_select_clause_value = default_select_clause_value
        self.default_where = default_where
        self.is_test_data = is_test_data or detect_if_is_test_data()
        self.is_ignore_duplicate = False
        self.user_context = UserContext()

    def insert(self, *, schema_name: str = None, table_name: str = None, data_dict: dict = None,
               ignore_duplicate: bool = False, commit_changes: bool = True) -> int:
        """Inserts a new row into the table and returns the id of the new row or -1 if an error occurred.
        ignore_duplicate should be False as default, because for example if a user register with existing name,
            he should get an error and not existing id
        """
        table_name = table_name or self.default_table_name
        schema_name = schema_name or self.default_schema_name
        self._validate_args(args=locals())
        if ignore_duplicate:
            self.logger.info(f"GenericCrudPostgresql.insert({schema_name}.{table_name}) using ignore_duplicate, is it needed? - Not recommended",
                             object={"data_dict": data_dict})

        data_dict = self.__add_create_updated_user_profile_ids(
            data_dict=data_dict, add_created_user_id=True,
            schema_name=schema_name, table_name=table_name)

        columns, values, params = process_insert_data_dict(data_dict=data_dict)
        
        # PostgreSQL uses RETURNING for getting the inserted ID
        id_column = generate_id_column_name(table_name)
        insert_query = f'INSERT INTO "{schema_name}"."{table_name}" ({columns}) VALUES ({values}) RETURNING {id_column};'
        
        try:
            self.logger.info("insert_query=" + insert_query)
            self.cursor.execute(insert_query, params)
            result = self.cursor.fetchone()
            inserted_id = result[0] if result else None
            
            if commit_changes:
                self.connection.commit()
                
        except psycopg2.errors.UniqueViolation as exception:
            if ignore_duplicate:
                self.logger.warning(f"GenericCrudPostgresql.insert({schema_name}.{table_name}) using ignore_duplicate - Trying to insert a duplicate value",
                                    object={"data_dict": data_dict})
                self.is_ignore_duplicate = True
                self.connection.rollback()  # Need to rollback the failed transaction
                inserted_id = self._get_existing_duplicate_id(schema_name, table_name, exception, data_dict=data_dict)
            else:
                self.connection.rollback()
                raise exception
        finally:
            self.is_ignore_duplicate = False
            self.logger.debug(object=locals())
        return inserted_id
        
    def _get_existing_duplicate_id(self, schema_name: str, table_name: str, error: Exception,
                                   data_dict: dict) -> int | None:
        if is_end_timestamp_in_table(table_name=table_name) and insert_is_undelete(table_name=table_name):
            existing_duplicate_id = self.__get_existing_duplicate_id_with_undelete(
                schema_name=schema_name, table_name=table_name, data_dict=data_dict)
        else:
            existing_duplicate_id = self.__get_existing_duplicate_id_without_undelete(
                schema_name=schema_name, table_name=table_name, data_dict=data_dict)
        if existing_duplicate_id is None:
            self.logger.error(
                f"GenericCrudPostgresql._get_existing_duplicate_id: no existing row found for {schema_name}.{table_name}.{data_dict}",
                object={"data_dict": data_dict, "error": error}
            )
            raise error
        self.logger.debug(object=locals())
        return existing_duplicate_id
        
    def __get_existing_duplicate_id_with_undelete(
            self, schema_name: str, table_name: str, data_dict: dict) -> int | None:
        column_name = generate_id_column_name(table_name)
        where, params = self.get_constraint_where_clause(
            schema_name=schema_name, table_name=table_name,
            data_dict=data_dict)
        row = self.select_one_tuple_by_where(
            schema_name=schema_name, view_table_name=table_name,
            select_clause_value=f"{column_name}, end_timestamp",
            where=where, params=params
        )
        if not row:
            existing_duplicate_id = None
            return existing_duplicate_id
        else:
            existing_duplicate_id, end_timestamp = row
        if end_timestamp and datetime.now(timezone.utc) > end_timestamp.replace(tzinfo=timezone.utc):
            self.undelete_by_column_and_value(
                schema_name=schema_name, table_name=table_name,
                column_name=column_name, column_value=existing_duplicate_id)
        return existing_duplicate_id
        
    def __get_existing_duplicate_id_without_undelete(
            self, *, schema_name: str, table_name: str, data_dict: dict) -> int | None:
        column_name = generate_id_column_name(table_name)
        where, params = self.get_constraint_where_clause(schema_name=schema_name, table_name=table_name,
                                                         data_dict=data_dict)
        if is_end_timestamp_in_table(table_name=table_name):
            row = self.select_one_tuple_by_where(
                schema_name=schema_name, view_table_name=table_name,
                select_clause_value=f"{column_name}, end_timestamp",
                where=where, params=params)
            if not row:
                existing_duplicate_id = None
                return existing_duplicate_id
            else:
                existing_duplicate_id, end_timestamp = row
                if end_timestamp is not None:
                    self.logger.error(
                        f"GenericCrudPostgresql.__get_existing_duplicate_id_without_undelete: existing row found for "
                        f"{schema_name}.{table_name}.{data_dict} but it is deleted",
                        object={"data_dict": data_dict, "existing_duplicate_id": existing_duplicate_id,
                                "end_timestamp": end_timestamp}
                    )
                    existing_duplicate_id = None
        else:
            existing_duplicate_id = self.select_one_value_by_where(
                schema_name=schema_name, view_table_name=table_name,
                select_clause_value=column_name,
                where=where, params=params)
        return existing_duplicate_id

    def update_by_column_and_value(
            self, *, schema_name: str = None, table_name: str = None,
            column_name: str = None, column_value: Any,
            data_dict: dict = None,
            limit: int = DEFAULT_SQL_SELECT_LIMIT, order_by: str = None,
            commit_changes: bool = True) -> int:
        """Updates data in the table by ID."""

        table_name = table_name or self.default_table_name
        column_name = column_name or self.default_column_name

        if column_name:
            where, params = get_where_params(column_name, column_value)
            updated_rows = self.update_by_where(
                schema_name=schema_name, table_name=table_name, where=where, data_dict=data_dict,
                params=params, limit=limit, order_by=order_by, commit_changes=commit_changes)
            return updated_rows

        else:
            raise Exception("Update by id requires an column_name")

    def update_by_where(self, *, schema_name: str = None,
                        table_name: str = None, where: str = None,
                        params: tuple = None, data_dict: dict = None,
                        limit: int = DEFAULT_SQL_SELECT_LIMIT,
                        order_by: str = None,
                        commit_changes: bool = True) -> int:
        """Updates data in the table by WHERE.
        Example:
        "UPDATE table_name SET A=A_val, B=B_val WHERE C=C_val AND D=D_val"
        translates into:
        update_by_where(table_name="table_name",
                        data_dict={"A": A_val, "B": B_val},
                        where="C=%s AND D=%s",
                        params=(C_val, D_val)"
        """

        table_name = table_name or self.default_table_name
        schema_name = schema_name or self.default_schema_name
        self._validate_args(args=locals())

        data_dict = self.__add_create_updated_user_profile_ids(data_dict=data_dict, add_created_user_id=False,
                                                               schema_name=schema_name, table_name=table_name)

        set_values, data_dict_params = process_update_data_dict(data_dict)
        if not where:
            raise Exception("update_by_where requires a 'where'")

        # PostgreSQL doesn't support LIMIT in UPDATE without a subquery
        # We'll handle this differently based on whether limit and order_by are provided
        if limit != DEFAULT_SQL_SELECT_LIMIT or order_by:
            # For PostgreSQL, we need to use a subquery with LIMIT and ORDER BY
            id_column = generate_id_column_name(table_name)
            
            # First, get the IDs of rows to update
            select_query = f'SELECT "{id_column}" FROM "{schema_name}"."{table_name}" WHERE {where}'
            if order_by:
                select_query += f' ORDER BY {order_by}'
            if limit != DEFAULT_SQL_SELECT_LIMIT:
                select_query += f' LIMIT {limit}'
                
            # Then update only those rows
            if 'mapping' in self.default_table_name:
                update_query = f'UPDATE "{schema_name}"."{table_name}" SET {set_values} ' \
                              f'WHERE "{id_column}" IN ({select_query});'
            else:
                update_query = f'UPDATE "{schema_name}"."{table_name}" SET {set_values}, ' \
                              f'updated_timestamp=CURRENT_TIMESTAMP ' \
                              f'WHERE "{id_column}" IN ({select_query});'
        else:
            # Simple update without LIMIT or ORDER BY
            if 'mapping' in self.default_table_name:
                update_query = f'UPDATE "{schema_name}"."{table_name}" SET {set_values} WHERE {where};'
            else:
                update_query = f'UPDATE "{schema_name}"."{table_name}" SET {set_values}, ' \
                              f'updated_timestamp=CURRENT_TIMESTAMP WHERE {where};'

        where_params = params or tuple()

        self.cursor.execute(update_query, data_dict_params + where_params)
        if commit_changes:
            self.connection.commit()
        updated_rows = self.cursor.get_affected_row_count()
        return updated_rows

    def update_by_column_and_value(
            self, *, schema_name: str = None, table_name: str = None,
            column_name: str = None, column_value: Any,
            data_dict: dict = None,
            limit: int = DEFAULT_SQL_SELECT_LIMIT, order_by: str = None,
            commit_changes: bool = True) -> int:
        """Updates data in the table by ID."""

        table_name = table_name or self.default_table_name
        column_name = column_name or self.default_column_name

        if column_name:
            where, params = get_where_params(column_name, column_value)
            updated_rows = self.update_by_where(
                schema_name=schema_name, table_name=table_name, where=where, data_dict=data_dict,
                params=params, limit=limit, order_by=order_by, commit_changes=commit_changes)
            return updated_rows

        else:
            raise Exception("Update by id requires an column_name")

    def update_by_where(self, *, schema_name: str = None,
                        table_name: str = None, where: str = None,
                        params: tuple = None, data_dict: dict = None,
                        limit: int = DEFAULT_SQL_SELECT_LIMIT,
                        order_by: str = None,
                        commit_changes: bool = True) -> int:
        """Updates data in the table by WHERE.
        Example:
        "UPDATE table_name SET A=A_val, B=B_val WHERE C=C_val AND D=D_val"
        translates into:
        update_by_where(table_name="table_name",
                        data_dict={"A": A_val, "B": B_val},
                        where="C=%s AND D=%s",
                        params=(C_val, D_val)"
        """

        table_name = table_name or self.default_table_name
        schema_name = schema_name or self.default_schema_name
        self._validate_args(args=locals())

        data_dict = self.__add_create_updated_user_profile_ids(data_dict=data_dict, add_created_user_id=False,
                                                               schema_name=schema_name, table_name=table_name)

        set_values, data_dict_params = process_update_data_dict(data_dict)
        if not where:
            raise Exception("update_by_where requires a 'where'")

        # PostgreSQL doesn't support LIMIT in UPDATE without a subquery
        # We'll handle this differently based on whether limit and order_by are provided
        if limit != DEFAULT_SQL_SELECT_LIMIT or order_by:
            # For PostgreSQL, we need to use a subquery with LIMIT and ORDER BY
            id_column = generate_id_column_name(table_name)
            
            # First, get the IDs of rows to update
            select_query = f'SELECT "{id_column}" FROM "{schema_name}"."{table_name}" WHERE {where}'
            if order_by:
                select_query += f' ORDER BY {order_by}'
            if limit != DEFAULT_SQL_SELECT_LIMIT:
                select_query += f' LIMIT {limit}'
                
            # Then update only those rows
            if 'mapping' in self.default_table_name:
                update_query = f'UPDATE "{schema_name}"."{table_name}" SET {set_values} ' \
                              f'WHERE "{id_column}" IN ({select_query});'
            else:
                update_query = f'UPDATE "{schema_name}"."{table_name}" SET {set_values}, ' \
                              f'updated_timestamp=CURRENT_TIMESTAMP ' \
                              f'WHERE "{id_column}" IN ({select_query});'
        else:
            # Simple update without LIMIT or ORDER BY
            if 'mapping' in self.default_table_name:
                update_query = f'UPDATE "{schema_name}"."{table_name}" SET {set_values} WHERE {where};'
            else:
                update_query = f'UPDATE "{schema_name}"."{table_name}" SET {set_values}, ' \
                              f'updated_timestamp=CURRENT_TIMESTAMP WHERE {where};'

        where_params = params or tuple()

        self.cursor.execute(update_query, data_dict_params + where_params)
        if commit_changes:
            self.connection.commit()
        updated_rows = self.cursor.get_affected_row_count()
        return updated_rows
        
    def delete_by_column_and_value(self, *, schema_name: str = None, table_name: str = None,
                                   column_name: str = None, column_value: Any) -> int:
        """Deletes data from the table by id.
        Returns the number of deleted rows."""
        # checks are done inside delete_by_where
        column_name = column_name or self.default_column_name

        if column_name:  # column_value can be empty
            where, params = get_where_params(column_name, column_value)
            deleted_rows = self.delete_by_where(schema_name=schema_name, table_name=table_name, where=where,
                                                params=params)
            return deleted_rows
        else:
            raise Exception("Delete by id requires an column_name and column_value.")

    def delete_by_where(self, *, schema_name: str = None, table_name: str = None, where: str = None,
                        params: tuple = None) -> int:
        """Deletes data from the table by WHERE.
        Returns the number of deleted rows."""

        table_name = table_name or self.default_table_name
        schema_name = schema_name or self.default_schema_name
        self._validate_args(args=locals())
        if not where:
            raise Exception("delete_by_where requires a 'where'")
        if "end_timestamp" not in where and is_end_timestamp_in_table(table_name):
            where += " AND end_timestamp IS NULL "

        # In PostgreSQL, we use the same approach as MySQL for soft deletes
        update_query = f'UPDATE "{schema_name}"."{table_name}" ' \
                       f'SET end_timestamp=CURRENT_TIMESTAMP ' \
                       f'WHERE {where};'

        self.cursor.execute(update_query, params)
        self.connection.commit()
        deleted_rows = self.cursor.get_affected_row_count()
        return deleted_rows
        
    def undelete_by_column_and_value(self, *, schema_name: str = None, table_name: str = None,
                                     column_name: str = None, column_value: Any) -> None:
        """Undeletes a row by setting the end_timestamp to NULL."""
        schema_name = schema_name or self.default_schema_name
        table_name = table_name or self.default_table_name
        column_name = column_name or self.default_column_name
        self._validate_args(args=locals())
        self.update_by_column_and_value(
            schema_name=schema_name, table_name=table_name,
            column_name=column_name, column_value=column_value,
            data_dict={"end_timestamp": None})
    # Main select function
    def select_multi_tuple_by_where(
            self, *, schema_name: str = None, view_table_name: str = None, select_clause_value: str = None,
            where: str = None, params: tuple = None, distinct: bool = False, limit: int = DEFAULT_SQL_SELECT_LIMIT,
            order_by: str = None) -> list:
        """Selects multiple rows from the table based on a WHERE clause and returns them as a list of tuples."""

        schema_name = schema_name or self.default_schema_name
        view_table_name = view_table_name or self.default_view_table_name
        select_clause_value = select_clause_value or self.default_select_clause_value
        select_clause_value = fix_select_clause_value(select_clause_value=select_clause_value)
        where = where or self.default_where
        where = fix_where_clause_value(where_clause_value=where)
        where = self.__where_security(where=where, view_name=view_table_name)
        self._validate_args(args=locals())

        if self.is_test_data and not self.is_ignore_duplicate:
            if self.default_view_with_deleted_and_test_data:
                view_table_name = self.default_view_with_deleted_and_test_data
            else:
                view_table_name = replace_view_with_table(view_table_name=view_table_name,
                                                          select_clause_value=select_clause_value)
        elif is_column_in_table(table_name=view_table_name, column_name="is_test_data"):
            if not where:
                where = "(is_test_data <> 1 OR is_test_data IS NULL)"
            elif not self.is_test_data and "is_test_data" not in where:
                where += " AND (is_test_data <> 1 OR is_test_data IS NULL)"  # hide test data from real users.

        if where and "end_timestamp" not in where and is_end_timestamp_in_table(
                view_table_name) and not self.is_ignore_duplicate:
            # The () around the where is important, because we might have a where with AND and OR
            where = f"({where}) AND end_timestamp IS NULL "  # not deleted
            
        select_query = f'SELECT {("DISTINCT " if distinct else "")} {select_clause_value} ' \
                       f'FROM "{schema_name}"."{view_table_name}" ' + \
                       (f'WHERE {where} ' if where else '') + \
                       (f'ORDER BY {order_by} ' if order_by else '') + \
                       f'LIMIT {limit};'

        self.connection.commit()  # Ensure we're working with the latest data
        if isinstance(params, int):
            params = [params]
        self.cursor.execute(select_query, params)
        result = self.cursor.fetchall()

        self.logger.debug(object=locals())
        return result

    def select_multi_dict_by_where(
            self, *, schema_name: str = None, view_table_name: str = None, select_clause_value: str = None,
            where: str = None, params: tuple = None, distinct: bool = False, group_by: str = None,
            limit: int = DEFAULT_SQL_SELECT_LIMIT, order_by: str = None) -> list | dict[tuple | str, list]:
        """Selects multiple rows from the table based on a WHERE clause and returns them as a list of dictionaries."""
        result = self.select_multi_tuple_by_where(
            schema_name=schema_name, view_table_name=view_table_name, select_clause_value=select_clause_value,
            where=where, params=params, distinct=distinct, limit=limit, order_by=order_by)
        result_as_dicts = self.convert_multi_to_dict(result, select_clause_value)
        if group_by:
            result_as_dicts = group_list_by_columns(list_of_dicts=result_as_dicts, group_by=group_by)
        return result_as_dicts

    def select_one_tuple_by_where(
            self, *, schema_name: str = None, view_table_name: str = None, select_clause_value: str = None,
            where: str = None, params: tuple = None, distinct: bool = False, order_by: str = None) -> tuple:
        """Selects one row from the table based on a WHERE clause and returns it as a tuple."""
        result = self.select_multi_tuple_by_where(
            schema_name=schema_name, view_table_name=view_table_name, select_clause_value=select_clause_value,
            where=where, params=params, distinct=distinct, limit=1, order_by=order_by)
        if result:
            tuple_result = result[0]
        else:
            tuple_result = tuple()
        return tuple_result

    def select_one_dict_by_where(
            self, *, schema_name: str = None, view_table_name: str = None, select_clause_value: str = None,
            where: str = None, params: tuple = None, distinct: bool = False, order_by: str = None) -> dict:
        """Selects one row from the table based on a WHERE clause and returns it as a dictionary."""
        result = self.select_one_tuple_by_where(
            schema_name=schema_name, view_table_name=view_table_name, select_clause_value=select_clause_value,
            where=where, params=params, distinct=distinct, order_by=order_by)
        result = self.convert_to_dict(row=result, select_clause_value=select_clause_value)
        return result

    def select_one_value_by_where(
            self, *, select_clause_value: str, schema_name: str = None, view_table_name: str = None,
            where: str = None, params: tuple = None, distinct: bool = False, order_by: str = None,
            skip_null_values: bool = True) -> Any:
        """Selects one value from the table based on a WHERE clause and returns it."""
        select_clause_value = select_clause_value or self.default_select_clause_value
        validate_single_clause_value(select_clause_value)
        where = where_skip_null_values(where, select_clause_value, skip_null_values)
        result = self.select_one_tuple_by_where(
            schema_name=schema_name, view_table_name=view_table_name, select_clause_value=select_clause_value,
            where=where, params=params, distinct=distinct, order_by=order_by)
        if result:
            value = result[0]
        else:
            value = None
        return value
    def select_one_tuple_by_column_and_value(
            self, *, schema_name: str = None, view_table_name: str = None, select_clause_value: str = None,
            column_name: str = None, column_value: Any,
            distinct: bool = False, order_by: str = None) -> tuple:
        """Selects one row from the table by ID and returns it as a tuple."""
        result = self.select_multi_tuple_by_column_and_value(
            schema_name=schema_name, view_table_name=view_table_name, select_clause_value=select_clause_value,
            column_name=column_name, column_value=column_value, distinct=distinct, limit=1, order_by=order_by)
        if result:
            one_tuple_result = result[0]
        else:
            one_tuple_result = tuple()  # or None?
        return one_tuple_result

    def select_one_dict_by_column_and_value(
            self, *, schema_name: str = None, view_table_name: str = None, select_clause_value: str = None,
            column_name: str = None, column_value: Any,
            distinct: bool = False, order_by: str = None) -> dict:
        """Selects one row from the table by ID and returns it as a dictionary (column_name: value)"""
        result = self.select_one_tuple_by_column_and_value(
            schema_name=schema_name, view_table_name=view_table_name, select_clause_value=select_clause_value,
            column_name=column_name, column_value=column_value, distinct=distinct, order_by=order_by)
        result = self.convert_to_dict(row=result, select_clause_value=select_clause_value)
        return result

    def select_one_value_by_column_and_value(
            self, *, select_clause_value: str = None, schema_name: str = None, view_table_name: str = None,
            column_name: str = None, column_value: Any,
            distinct: bool = False, order_by: str = None, skip_null_values: bool = True) -> Any:
        """Selects one value from the table by ID and returns it."""

        column_name = column_name or self.default_column_name
        select_clause_value = select_clause_value or self.default_select_clause_value
        validate_single_clause_value(select_clause_value)
        where, params = get_where_params(column_name, column_value)
        where = where_skip_null_values(where, select_clause_value, skip_null_values)
        result = self.select_one_tuple_by_where(
            schema_name=schema_name, view_table_name=view_table_name, select_clause_value=select_clause_value,
            where=where, params=params, distinct=distinct, order_by=order_by)
        if result:  # TODO: the caller can't tell if not found, or found null
            value = result[0]
        else:
            value = None
        return value

    def select_multi_tuple_by_column_and_value(
            self, *, schema_name: str = None, view_table_name: str = None, select_clause_value: str = None,
            column_name: str = None, column_value: Any,
            distinct: bool = False, limit: int = DEFAULT_SQL_SELECT_LIMIT, order_by: str = None) -> list:
        """Selects multiple rows from the table by ID and returns them as a list of tuples.
        If column_value is list / tuple, it will be used as multiple values for the column_name (SQL IN)."""

        column_name = column_name or self.default_column_name

        where, params = get_where_params(column_name, column_value)
        result = self.select_multi_tuple_by_where(
            schema_name=schema_name, view_table_name=view_table_name, select_clause_value=select_clause_value,
            where=where, params=params, distinct=distinct, limit=limit, order_by=order_by)
        return result

    def select_multi_dict_by_column_and_value(
            self, *, schema_name: str = None, view_table_name: str = None, select_clause_value: str = None,
            column_name: str = None, column_value: Any,
            distinct: bool = False, limit: int = DEFAULT_SQL_SELECT_LIMIT, order_by: str = None,
            group_by: str = None) -> list | dict[tuple | str, list]:
        """Selects multiple rows from the table by ID and returns them as a list of dictionaries."""
        result = self.select_multi_tuple_by_column_and_value(
            schema_name=schema_name, view_table_name=view_table_name, select_clause_value=select_clause_value,
            column_name=column_name, column_value=column_value, distinct=distinct, limit=limit, order_by=order_by)
        result_as_dicts = self.convert_multi_to_dict(result, select_clause_value)
        if group_by:
            result_as_dicts = group_list_by_columns(list_of_dicts=result_as_dicts, group_by=group_by)
        return result_as_dicts
    def insert_if_not_exists(self, *, schema_name: str = None, table_name: str = None, data_dict: dict = None,
                             data_dict_compare: dict = None, view_table_name: str = None,
                             commit_changes: bool = True, compare_with_or: bool = False) -> int:
        """Inserts a new row into the table if a row with the same values does not exist,
        and returns the id of the new row | None if an error occurred."""
        schema_name = schema_name or self.default_schema_name
        table_name = table_name or self.default_table_name
        view_table_name = view_table_name or self.default_view_table_name
        data_dict_compare = data_dict_compare or data_dict
        self._validate_args(args=locals())

        # Try to select
        where_clause, params = process_upsert_data_dict(data_dict=data_dict_compare, compare_with_or=compare_with_or)
        row_tuple = self.select_one_tuple_by_where(
            schema_name=schema_name, view_table_name=view_table_name, select_clause_value="*",
            where=where_clause, params=params)
        if row_tuple:
            entity_id = row_tuple[0]
            self.logger.info(f"GenericCrudPostgresql.insert_if_not_exists: row already exists, returning id {entity_id}",
                             object={"id": entity_id})
        else:
            entity_id = self.insert(schema_name=schema_name, table_name=table_name, data_dict=data_dict,
                                   commit_changes=commit_changes, ignore_duplicate=True)
            self.logger.info(f"GenericCrudPostgresql.insert_if_not_exists: row inserted with id {entity_id}",
                             object={"id": entity_id})
        return entity_id

    def insert_many_dicts(self, *, schema_name: str = None, table_name: str = None, data_dicts: list[dict],
                          commit_changes: bool = True) -> int:
        """Inserts multiple rows into the table.
        data_dicts should be in the following format: [{col1: val1, col2: val2}, {col1: val3, col2: val4}, ...]
        Returns the number of inserted rows.
        """
        if not data_dicts:
            self.logger.warning("GenericCrudPostgresql.insert_many_dicts: data_dicts is empty")
            inserted_rows = 0
        else:
            converted_data_dicts = {col: [row[col] for row in data_dicts] for col in data_dicts[0]}
            inserted_rows = self.insert_many(schema_name=schema_name, table_name=table_name,
                                             data_dict=converted_data_dicts, commit_changes=commit_changes)

        return inserted_rows

    def insert_many(self, *, schema_name: str = None, table_name: str = None, data_dict: dict[str, list | tuple],
                    commit_changes: bool = True) -> int:
        """Inserts multiple rows into the table.
        data_dict should be in the following format: {col1: [val1, val2], col2: [val3, val4], ...}
        Returns the number of inserted rows.
        """
        if not data_dict:
            self.logger.warning("GenericCrudPostgresql.insert_many: data_dict is empty")
            inserted_rows = 0
            return inserted_rows
        schema_name = schema_name or self.default_schema_name
        table_name = table_name or self.default_table_name

        self._validate_args(args=locals())

        len_rows = len(next(v for v in data_dict.values()))
        data_dict = self.__add_create_updated_user_profile_ids(
            data_dict=data_dict, add_created_user_id=True, schema_name=schema_name, table_name=table_name)
        # Fix values from __add_create_updated_user_profile_ids
        for k, v in data_dict.items():
            if not isinstance(v, list) and not isinstance(v, tuple):
                data_dict[k] = [v] * len_rows

        columns = ", ".join(f'"{key}"' for key in data_dict)
        values = ", ".join(["%s"] * len(data_dict))
        sql_statement = f'INSERT INTO "{schema_name}"."{table_name}" ({columns}) VALUES ({values});'
        sql_parameters = list(zip(*data_dict.values()))
        
        self.cursor.executemany(sql_statement=sql_statement, sql_parameters=sql_parameters)
        if commit_changes:
            self.connection.commit()
        inserted_rows = self.cursor.get_affected_row_count()
        return inserted_rows
    def upsert_with_select_clause(self, *, schema_name: str = None, table_name: str = None, view_table_name: str = None,
                                  data_dict: dict = None, where_compare: str = None, params_compare: tuple = None,
                                  data_dict_compare: dict = None, order_by: str = None, compare_with_or: bool = False,
                                  select_clause_value: str = "*") -> dict:
        """
        Inserts a new row into the table if a row with the same values does not exist,
        the logic:
        1. If data_dict_compare is empty, insert the row and return the id.
        2. If data_dict_compare is not empty, select the row with the same values as data_dict_compare.

            a. If the row exists, update it with data_dict and return the id.

            b. If the row does not exist, insert it with data_dict and return the id.
        """
        schema_name = schema_name or self.default_schema_name
        table_name = table_name or self.default_table_name
        view_table_name = view_table_name or self.default_view_table_name
        column_name = generate_id_column_name(table_name)
        self._validate_args(args=locals())
        result_dict = {}
        if not data_dict:
            self.logger.warning(log_message="GenericCrudPostgresql.upsert_with_select_clause: data_dict is empty")
            return result_dict
        if not data_dict_compare:
            inserted_id = self.insert(schema_name=schema_name,
                                     table_name=table_name, data_dict=data_dict)
            data_dict[column_name] = inserted_id
            result_dict = data_dict
            return result_dict

        where_clause, params = process_upsert_data_dict(data_dict=data_dict_compare, compare_with_or=compare_with_or,
                                                        where_compare=where_compare, params_compare=params_compare)
        # Add table_id if it's not in select_clause_value
        if select_clause_value != "*" and column_name not in select_clause_value:
            select_clause_value += f", {column_name}"
        row_dict = self.select_one_dict_by_where(
            schema_name=schema_name, view_table_name=view_table_name, select_clause_value=select_clause_value,
            where=where_clause, params=params, order_by=order_by)
        if row_dict:
            table_id = row_dict[column_name]
            try:
                self.update_by_column_and_value(
                    schema_name=schema_name, table_name=table_name, column_name=column_name, column_value=table_id,
                    data_dict=data_dict)
            except Exception as exception:
                self.logger.error(
                    "GenericCrudPostgresql.upsert_with_select_clause: error updating row",
                    object={"data_dict": data_dict, "row_dict": row_dict, "exception": exception}
                )
                raise exception
        else:
            try:
                table_id = self.insert(schema_name=schema_name, table_name=table_name, data_dict=data_dict)
            except Exception as exception:
                self.logger.error(
                    "GenericCrudPostgresql.upsert_with_select_clause: error inserting row",
                    object={"data_dict": data_dict, "exception": exception}
                )
                raise exception
        result_dict = data_dict
        result_dict.update({k: v for k, v in row_dict.items() if k not in result_dict}) if row_dict else None
        result_dict[column_name] = table_id
        self.logger.debug(object=locals())
        return result_dict

    # We want upsert to call upsert_with_select_clause, and return only the id
    def upsert(self, *, schema_name: str = None, table_name: str = None, view_table_name: str = None,
               data_dict: dict = None, where_compare: str = None,
               params_compare: tuple = None, data_dict_compare: dict = None,
               order_by: str = None, compare_with_or: bool = False) -> Optional[int]:
        """
        Inserts a new row into the table if a row with the same values does not exist,
        the "same values" are extracted from data_dict_compare.
        data_dict_compare is a dictionary with the same keys as data_dict, but with the values to compare.

        **you don't need to have the full fields in data_dict_compare, only the fields you want to compare.**
        """
        table_name = table_name or self.default_table_name
        column_name = generate_id_column_name(table_name)
        inserted_id_per_column_dict = self.upsert_with_select_clause(
            schema_name=schema_name, table_name=table_name,
            view_table_name=view_table_name, data_dict=data_dict,
            where_compare=where_compare, params_compare=params_compare,
            data_dict_compare=data_dict_compare, order_by=order_by,
            compare_with_or=compare_with_or, select_clause_value=column_name)
        inserted_id = inserted_id_per_column_dict[column_name]
        return inserted_id
    # Helper methods
    def convert_to_dict(self, row: tuple, select_clause_value: str = None) -> dict:
        """Returns a dictionary of the column names and their values."""
        select_clause_value = select_clause_value or self.default_select_clause_value
        if select_clause_value == "*":
            column_names = self.cursor.column_names()
        else:
            column_names = [x.strip() for x in select_clause_value.split(",")]
        dict_result = dict(zip(column_names, row or tuple()))
        self.logger.debug(object=locals())
        return dict_result

    def convert_multi_to_dict(self, rows: list[tuple], select_clause_value: str = None) -> list[dict]:
        """Converts multiple rows to dictionaries."""
        multiple_dict_result = [self.convert_to_dict(row=row, select_clause_value=select_clause_value)
                                for row in rows]
        return multiple_dict_result

    def _validate_args(self, args: dict) -> None:
        # args = locals() of the calling function
        required_args = ("table_name", "view_table_name", "schema_name",
                         "select_clause_value", "data_dict")
        for arg_name, arg_value in args.items():
            message = ""
            if arg_name in ("self", "__class__"):
                continue
            elif arg_name in required_args and not arg_value:
                message = f"Invalid value for {arg_name}: {arg_value}"
            elif arg_name == "table_name":
                validate_none_select_table_name(arg_value)
            elif arg_name == "view_table_name":
                validate_select_table_name(view_table_name=arg_value, is_ignore_duplicate=self.is_ignore_duplicate)

            # data_dict values are allowed to contain ';', as we use them with %s
            if ((arg_name.startswith("data_") and arg_value and any(
                    ";" in str(x) for x in arg_value.keys())) or  # check columns
                    (not arg_name == "data_dict" and arg_name != "params" and ";" in str(arg_value))):
                message = f"Invalid value for {arg_name}: {arg_value} (contains ';')"

            if message:
                raise Exception(message)

    def __where_security(self, where: str, view_name: str) -> str:
        """Adds security to the where clause."""
        if view_name in table_definition:
            if table_definition[view_name].get("is_visibility"):
                effective_profile_id = self.user_context.get_effective_profile_id()
                where_security = f'(visibility_id > 1 OR created_effective_profile_id = {effective_profile_id})'
                if where:
                    where_security += f" AND ({where})"
                return where_security
        return where

    def __add_create_updated_user_profile_ids(self, data_dict: dict, add_created_user_id: bool = False,
                                              schema_name: str = None, table_name: str = None) -> dict:
        """Adds created_user_id and updated_user_id to data_dict."""
        data_dict = data_dict or {}
        schema_name = schema_name or self.default_schema_name
        table_name = table_name or self.default_table_name
        table_columns = get_table_columns(table_name=table_name)
        if len(table_columns) == 0:
            self.logger.warning(f"Table {schema_name}.{table_name} was not generated by the generate_table_columns.py script.")
            return data_dict
        if add_created_user_id:
            if "created_user_id" in table_columns:
                data_dict["created_user_id"] = self.user_context.get_effective_user_id()
            else:
                self.__log_warning("created_user_id", schema_name, table_name)
            if "created_real_user_id" in table_columns:
                data_dict["created_real_user_id"] = self.user_context.get_real_user_id()
            else:
                self.__log_warning("created_real_user_id", schema_name, table_name)
            if "created_effective_user_id" in table_columns:
                data_dict["created_effective_user_id"] = self.user_context.get_effective_user_id()
            else:
                self.__log_warning("created_effective_user_id", schema_name, table_name)
            if "created_effective_profile_id" in table_columns:
                data_dict["created_effective_profile_id"] = self.user_context.get_effective_profile_id()
            else:
                self.__log_warning("created_effective_profile_id", schema_name, table_name)
            if "is_test_data" in table_columns:
                data_dict["is_test_data"] = self.is_test_data
            else:
                self.__log_warning("is_test_data", schema_name, table_name)

            if "number" in table_columns:
                view_name = table_name
                number = NumberGenerator.get_random_number(
                    schema_name=schema_name, view_name=view_name)
                data_dict["number"] = number
            else:
                self.__log_warning("number", schema_name, table_name)

            if "identifier" in table_columns:
                self.__add_identifier(data_dict=data_dict, table_name=table_name)
            else:
                self.__log_warning("identifier", schema_name, table_name)
        if "updated_user_id" in table_columns:
            data_dict["updated_user_id"] = self.user_context.get_effective_user_id()
        else:
            self.__log_warning("updated_user_id", schema_name, table_name)
        if "updated_real_user_id" in table_columns:
            data_dict["updated_real_user_id"] = self.user_context.get_real_user_id()
        else:
            self.__log_warning("updated_real_user_id", schema_name, table_name)
        if "updated_effective_user_id" in table_columns:
            data_dict["updated_effective_user_id"] = self.user_context.get_effective_user_id()
        else:
            self.__log_warning("updated_effective_user_id", schema_name, table_name)
        if "updated_effective_profile_id" in table_columns:
            data_dict["updated_effective_profile_id"] = self.user_context.get_effective_profile_id()
        else:
            self.__log_warning("updated_effective_profile_id", schema_name, table_name)

        self.logger.debug(object=locals())
        return data_dict

    @lru_cache(maxsize=64)  # Don't show the same warning twice
    def __log_warning(self, column_name: str, schema_name: str, table_name: str):
        """Generates a warning log message and logs it."""
        self.logger.warning(f"{schema_name}.{table_name}.{column_name} not found in table_columns.")

    def __add_identifier(self, data_dict: dict, table_name: str) -> None:
        # If there's an "identifier" column in the table, we want to insert a random identifier
        identifier_entity_type_id = get_entity_type_id_by_table_name(table_name)
        if not identifier_entity_type_id:
            return
        identifier = NumberGenerator.get_random_identifier(
            schema_name="identifier", view_name="identifier_view", identifier_column_name="identifier")
        data_dict["identifier"] = identifier
        # Insert into identifier table
        insert_query = 'INSERT INTO "identifier"."identifier_table" (identifier, entity_type_id) VALUES (%s, %s);'
        self.cursor.execute(insert_query, (identifier, identifier_entity_type_id))
        self.connection.commit()

    @lru_cache
    def get_primary_key(self, schema_name: str = None, table_name: str = None) -> str | None:
        schema_name = schema_name or self.default_schema_name
        table_name = table_name or self.default_table_name
        query = """
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = %s::regclass
            AND i.indisprimary;
        """
        
        self.connection.commit()
        try:
            self.cursor.execute(query, (f'"{schema_name}"."{table_name}"',))
            column_name = (self.cursor.fetchone() or [None])[0]
            return column_name
        except Exception as e:
            self.logger.error(f"Error getting primary key: {e}")
            return None

    @lru_cache
    def get_constraint_columns(self, schema_name: str, table_name: str) -> list[list[str]]:
        schema_name = schema_name or self.default_schema_name
        table_name = table_name or self.default_table_name
        query = """
        SELECT con.conname as constraint_name, 
               array_agg(att.attname) as column_names
        FROM pg_constraint con
        JOIN pg_class rel ON rel.oid = con.conrelid
        JOIN pg_namespace nsp ON nsp.oid = rel.relnamespace
        JOIN pg_attribute att ON att.attrelid = rel.oid AND att.attnum = ANY(con.conkey)
        WHERE nsp.nspname = %s
        AND rel.relname = %s
        AND con.contype IN ('p', 'u')
        GROUP BY con.conname;
        """
        self.connection.commit()
        try:
            self.cursor.execute(query, (schema_name, table_name))
            results = self.cursor.fetchall()
            constraints = []
            for _, column_names in results:
                constraints.append(list(column_names))
            return constraints
        except Exception as e:
            self.logger.error(f"Error getting constraint columns: {e}")
            return []

    def get_constraint_where_clause(self, schema_name: str, table_name: str, data_dict: dict):
        constraint_columns = self.get_constraint_columns(schema_name, table_name)
        if constraint_columns:
            where, params = generate_where_clause_for_ignore_duplicate(
                data_dict=data_dict, constraint_columns=constraint_columns)
        else:
            where, params = None, None
        return where, params

    @property
    def cursor(self) -> Cursor:
        """Get a new cursor"""
        if self._cursor.is_closed():
            self._cursor = self.connection.cursor()
        cursor = self._cursor
        return cursor

    @cursor.setter
    def cursor(self, value: Cursor) -> None:
        """Set the cursor"""
        self._cursor = value

    def set_schema(self, schema_name: Optional[str]):
        """Sets the given schema to be the default schema."""
        if schema_name and self.default_schema_name != schema_name:
            self.connection.set_schema(schema_name)
            self.default_schema_name = schema_name

    def close(self) -> None:
        """Closes the connection to the database (we usually do not have to call this)"""
        try:
            self.connection.close()
        except Exception as e:
            self.logger.error(f"Error while closing the connection: {e}")

    def create_view(self, schema_name=None, table_name=None, view_name=None):
        if table_name is not None and '_view' in table_name:
            return
        if schema_name is None:
            schema_name = self.default_schema_name

        if table_name is None:
            table_name = self.default_table_name

        if view_name is None:
            view_name = self.default_view_table_name

        print(f"Creating view {view_name} from {table_name}")
        create_view_query = f"""
        CREATE OR REPLACE VIEW "{schema_name}"."{view_name}" AS
        SELECT * FROM "{schema_name}"."{table_name}";
        """

        self.cursor.execute(create_view_query)