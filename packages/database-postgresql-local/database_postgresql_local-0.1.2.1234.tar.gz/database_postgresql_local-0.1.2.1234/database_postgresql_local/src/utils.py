import copy
import inspect
import os
from functools import lru_cache
from typing import Any, Optional, Tuple

from logger_local.LoggerLocal import Logger
from logger_local.MetaLogger import module_wrapper
from python_sdk_remote.utilities import get_environment_name
from python_sdk_remote.utilities import our_get_env
from url_remote.environment_name_enum import EnvironmentName

from .constants_src import LOGGER_CONNECTOR_CODE_OBJECT
from .table_columns import table_columns
from .table_definition import table_definition
# from .to_sql_interface import ToSQLInterface
from database_infrastructure_local.to_sql_interface import ToSQLInterface

logger = Logger.create_logger(object=LOGGER_CONNECTOR_CODE_OBJECT)


# TODO Convert those methods to class with overloading methods
def get_sql_hostname() -> str:
    sql_hostname = our_get_env("POSTGRESQL_HOSTNAME")
    return sql_hostname


def get_sql_username() -> str:
    sql_username = our_get_env("POSTGRESQL_USERNAME")
    return sql_username


def get_sql_password() -> str:
    sql_password = our_get_env("POSTGRESQL_PASSWORD")
    return sql_password


def get_sql_port() -> str:
    sql_port = our_get_env("POSTGRES_PORT", default="5432")
    return sql_port


def get_ssh_hostname() -> str:
    return our_get_env("SSH_HOSTNAME", raise_if_not_found=False)


def get_ssh_username() -> str:
    ssh_username = our_get_env("SSH_USERNAME", raise_if_empty=True)
    return ssh_username


# Placeholder for table_columns and table_definition
# These will be populated from the database schema
table_columns = {}
table_definition = {}


def detect_if_is_test_data() -> bool:
    """Detects if the current environment is a test environment."""
    environment_name = get_environment_name()
    return environment_name != EnvironmentName.PROD1.value


def generate_id_column_name(table_name: str) -> str:
    """Generates the ID column name for a table."""
    if table_name.endswith('_table'):
        table_name = table_name[:-6]
    elif table_name.endswith('_view'):
        table_name = table_name[:-5]
    return f"{table_name}_id"


def generate_table_name(schema_name: str) -> str:
    """Generates the table name for a schema."""
    return f"{schema_name}_table"


def generate_view_name(table_name: str) -> str:
    """Generates the view name for a table."""
    if table_name.endswith('_table'):
        table_name = table_name[:-6]
    return f"{table_name}_view"


def get_entity_type_id_by_table_name(table_name: str) -> int:
    """Gets the entity type ID for a table."""
    # This would be implemented based on your entity type mapping
    return None


def get_where_params(column_name: str, column_value: Any) -> tuple:
    """Generates a WHERE clause and parameters for a column and value."""
    if isinstance(column_value, (list, tuple)):
        placeholders = ', '.join(['%s'] * len(column_value))
        where = f"{column_name} IN ({placeholders})"
        params = tuple(column_value)
    else:
        where = f"{column_name} = %s"
        params = (column_value,)
    return where, params


def process_insert_data_dict(data_dict: dict) -> tuple:
    """Processes a dictionary for an INSERT statement."""
    columns = ", ".join(f"\"{key}\"" for key in data_dict)
    values = ", ".join(["%s"] * len(data_dict))
    params = tuple(data_dict.values())
    return columns, values, params


def process_update_data_dict(data_dict: dict) -> tuple:
    """Processes a dictionary for an UPDATE statement."""
    set_values = ", ".join(f"\"{key}\" = %s" for key in data_dict)
    params = tuple(data_dict.values())
    return set_values, params


def process_upsert_data_dict(data_dict: dict, compare_with_or: bool = False,
                            where_compare: str = None, params_compare: tuple = None) -> tuple:
    """Processes a dictionary for an UPSERT statement."""
    if where_compare:
        where = where_compare
        params = params_compare
    else:
        where_parts = []
        params = []
        for key, value in data_dict.items():
            if value is None:
                where_parts.append(f"\"{key}\" IS NULL")
            else:
                where_parts.append(f"\"{key}\" = %s")
                params.append(value)
        connector = " OR " if compare_with_or else " AND "
        where = connector.join(where_parts)
        params = tuple(params)
    return where, params


def replace_view_with_table(view_table_name: str, select_clause_value: str = None) -> str:
    """Replaces a view name with a table name."""
    if view_table_name.endswith('_view'):
        return view_table_name[:-5] + '_table'
    return view_table_name


def validate_none_select_table_name(table_name: str) -> None:
    """Validates a table name for non-select operations."""
    if not table_name:
        raise ValueError("Table name cannot be empty")


def validate_select_table_name(view_table_name: str, is_ignore_duplicate: bool = False) -> None:
    """Validates a table name for select operations."""
    if not view_table_name:
        raise ValueError("View table name cannot be empty")


def validate_single_clause_value(select_clause_value: str) -> None:
    """Validates that a SELECT clause has only one value."""
    if ',' in select_clause_value:
        raise ValueError(f"Expected a single column, got: {select_clause_value}")


def where_skip_null_values(where: str, select_clause_value: str, skip_null_values: bool) -> str:
    """Adds a condition to skip NULL values in a WHERE clause."""
    if skip_null_values:
        null_condition = f"{select_clause_value} IS NOT NULL"
        if where:
            where = f"({where}) AND {null_condition}"
        else:
            where = null_condition
    return where


def insert_is_undelete(table_name: str) -> bool:
    """Checks if an insert operation should undelete a record."""
    # This would be implemented based on your table configuration
    return False


def is_column_in_table(table_name: str, column_name: str) -> bool:
    """Checks if a column exists in a table."""
    if table_name in table_columns:
        return column_name in table_columns[table_name]
    return False


def is_end_timestamp_in_table(table_name: str) -> bool:
    """Checks if a table has an end_timestamp column."""
    return is_column_in_table(table_name, "end_timestamp")


def get_table_columns(table_name: str) -> list:
    """Gets the columns for a table."""
    if table_name in table_columns:
        return table_columns[table_name]
    return []


def group_list_by_columns(list_of_dicts: list, group_by: str) -> dict:
    """Groups a list of dictionaries by specified columns."""
    result = {}
    group_by_columns = [col.strip() for col in group_by.split(',')]
    
    for item in list_of_dicts:
        key = tuple(item.get(col) for col in group_by_columns)
        if len(group_by_columns) == 1:
            key = key[0]  # If only one column, use the value directly as key
        
        if key not in result:
            result[key] = []
        result[key].append(item)
    
    return result


def process_select_data_dict(data_dict: dict) -> tuple:
    """Processes a dictionary for a SELECT statement."""
    where_parts = []
    params = []
    for key, value in data_dict.items():
        if value is None:
            where_parts.append(f"\"{key}\" IS NULL")
        else:
            where_parts.append(f"\"{key}\" = %s")
            params.append(value)
    where = " AND ".join(where_parts)
    params = tuple(params)
    return where, params


def generate_where_clause_for_ignore_duplicate(data_dict: dict, constraint_columns: list) -> tuple:
    """Generates a WHERE clause for checking duplicates."""
    for columns in constraint_columns:
        where_parts = []
        params = []
        valid = True
        for column in columns:
            if column in data_dict:
                value = data_dict[column]
                if value is None:
                    where_parts.append(f"\"{column}\" IS NULL")
                else:
                    where_parts.append(f"\"{column}\" = %s")
                    params.append(value)
            else:
                valid = False
                break
        if valid and where_parts:
            where = " AND ".join(where_parts)
            params = tuple(params)
            return where, params
    return None, None


def fix_select_clause_value(select_clause_value: str) -> str:
    """Fixes a SELECT clause value."""
    return select_clause_value


def fix_where_clause_value(where_clause_value: str) -> str:
    """Fixes a WHERE clause value."""
    return where_clause_value