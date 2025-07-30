from enum import Enum

from logger_local.LoggerComponentEnum import LoggerComponentEnum


# TODO Move everything related to sync to separate directory called
#  sync_data_source (preferable with it's own src and tests directories)
class UpdateStatus(Enum):
    UPDATE_DATA_SOURCE = -1
    DONT_UPDATE = 0
    UPDATE_CIRCLEZ = 1  # TODO Don't use CIRCLEZ


# connector / cursor
DATABASE_POSTGRESQL_PYTHON_PACKAGE_COMPONENT_ID = 113
DATABASE_POSTGRESQL_PYTHON_PACKAGE_COMPONENT_NAME = 'database_postgresql_local\\connector'
CONNECTOR_DEVELOPER_EMAIL = 'idan.a@circ.zone'
LOGGER_CONNECTOR_CODE_OBJECT = {
    'component_id': DATABASE_POSTGRESQL_PYTHON_PACKAGE_COMPONENT_ID,
    'component_name': DATABASE_POSTGRESQL_PYTHON_PACKAGE_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': CONNECTOR_DEVELOPER_EMAIL
}

# generic_crud
DATABASE_POSTGRESQL_PYTHON_GENERIC_CRUD_COMPONENT_ID = 207
DATABASE_POSTGRESQL_PYTHON_GENERIC_CRUD_COMPONENT_NAME = 'database_postgresql_local\\generic_crud_postgresql'
GENERIC_CRUD_DEVELOPER_EMAIL = 'akiva.s@circ.zone'
CRUD_POSTGRESQL_CODE_LOGGER_OBJECT = {
    'component_id': DATABASE_POSTGRESQL_PYTHON_GENERIC_CRUD_COMPONENT_ID,
    'component_name': DATABASE_POSTGRESQL_PYTHON_GENERIC_CRUD_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': GENERIC_CRUD_DEVELOPER_EMAIL
}
CRUD_POSTGRESQL_TEST_LOGGER_OBJECT = CRUD_POSTGRESQL_CODE_LOGGER_OBJECT.copy()
CRUD_POSTGRESQL_TEST_LOGGER_OBJECT['component_category'] = LoggerComponentEnum.ComponentCategory.Unit_Test.value