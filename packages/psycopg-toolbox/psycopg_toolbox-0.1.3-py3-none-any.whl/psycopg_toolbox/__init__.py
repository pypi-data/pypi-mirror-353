"""Psycopg Toolbox - Utilities for working with psycopg v3.

This package provides useful utilities and context managers for working with psycopg v3,
including role switching, advisory locks, autocommit management, and custom exceptions.
"""

from .contextmanagers import (
    autocommit,
    obtain_advisory_lock,
    switch_role,
)
from .exceptions import AlreadyExistsError, DatabaseError
from .logging import LoggingConnection, LoggingCursor
from .query_helpers import (
    create_database,
    create_schema,
    database_exists,
    drop_database,
    drop_schema,
    schema_exists,
)
from .role_helpers import (
    create_role,
    create_user,
    drop_user_or_role,
    get_current_user,
    user_or_role_exists,
)

__all__ = [
    "autocommit",
    "switch_role",
    "obtain_advisory_lock",
    "AlreadyExistsError",
    "DatabaseError",
    "LoggingConnection",
    "LoggingCursor",
    "create_database",
    "database_exists",
    "drop_database",
    "create_schema",
    "schema_exists",
    "drop_schema",
    "create_role",
    "create_user",
    "drop_user_or_role",
    "get_current_user",
    "user_or_role_exists",
]
