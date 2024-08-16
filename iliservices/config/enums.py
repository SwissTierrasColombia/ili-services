import functools
from enum import (Enum,
                  IntFlag)


@functools.total_ordering
class OrderedEnum(Enum):
    @classmethod
    @functools.lru_cache(None)
    def _member_list(cls):
        return list(cls)

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            member_list = self.__class__._member_list()
            return member_list.index(self) < member_list.index(other)
        return NotImplemented


class EnumTestLevel(IntFlag):
    _CHECK_DB = 2
    _CHECK_SCHEMA = 4
    _CHECK_INTERLIS = 8

    SERVER_OR_FILE = 1
    DB = _CHECK_DB  # 2
    DB_SCHEMA = _CHECK_DB|_CHECK_SCHEMA  # 6
    DB_FILE = _CHECK_DB|_CHECK_SCHEMA  # 6
    INTERLIS = _CHECK_DB|_CHECK_SCHEMA|_CHECK_INTERLIS  # 14
    SCHEMA_IMPORT = 128


class EnumUserLevel(IntFlag):
    CREATE = 1
    CONNECT = 2


class EnumTestConnectionMsg(IntFlag):
    CONNECTION_TO_SERVER_FAILED = 0
    CONNECTION_COULD_NOT_BE_OPEN = 1
    DATABASE_NOT_FOUND = 2
    SCHEMA_NOT_FOUND = 3
    USER_HAS_NO_PERMISSION = 4
    INTERLIS_META_ATTRIBUTES_NOT_FOUND = 5
    INVALID_ILI2DB_VERSION = 6
    UNKNOWN_CONNECTION_ERROR = 10
    DIR_NOT_FOUND = 11
    GPKG_FILE_NOT_FOUND = 12
    WRONG_FILE_EXTENSION = 13
    BASKET_COLUMN_NOT_FOUND = 14

    CONNECTION_OPENED = 100
    CONNECTION_TO_SERVER_SUCCESSFUL = 101
    CONNECTION_TO_DB_SUCCESSFUL = 102
    CONNECTION_TO_SCHEMA_SUCCESSFUL = 103
    DB_WITH_VALID_INTERLIS_STRUCTURE = 104
    SCHEMA_WITH_VALID_INTERLIS_STRUCTURE = 105
    CONNECTION_TO_DB_SUCCESSFUL_NO_LADM_COL = 106
