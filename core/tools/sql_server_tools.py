"""Compat shims for sql_server_tools used by legacy tests.

This module provides small, safe stand-ins for a subset of the
functionality tests expect. The real implementation talks to SQL Server
and is not needed during fast unit test collection.

Keep this file minimal and avoid side-effects at import time.
"""
from typing import Dict, Any


def db_schema_info(connection_string: str | None = None) -> Dict[str, Any]:
    """Return a minimal schema description placeholder.

    Tests expect to import this function; returning an empty schema
    is sufficient for collection and many unit tests that don't hit SQL.
    """
    return {"tables": [], "connection_string": connection_string}


def sql_server_tools() -> Dict[str, Any]:
    """Return a tiny shim object/dict representing available tools.

    Real code may expect callables inside; tests typically only import
    the symbol, so a dict is a safe placeholder.
    """
    return {
        "info": db_schema_info,
    }


__all__ = ["db_schema_info", "sql_server_tools"]
