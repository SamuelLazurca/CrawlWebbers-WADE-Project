import re
from typing import Any, Dict, Optional, Type, TypeVar

T = TypeVar("T")


def unpack_sparql_row(row: Dict[str, Any], key: str, default: Any = None, cast_to: Type[T] = str) -> Optional[T]:
    """
    Safely extracts a value from a SPARQL binding result.
    Example: row={"size": {"type": "literal", "value": "100"}}
    unpack_sparql_row(row, "size", 0, int) -> 100
    """
    if key not in row:
        return default

    val_str = row[key].get("value")
    if val_str is None:
        return default

    try:
        if cast_to == bool:
            return val_str.lower() == "true"
        return cast_to(val_str)
    except (ValueError, TypeError):
        return default


def is_safe_uri(uri: str) -> bool:
    """
    Prevents SPARQL injection but allows Property Paths.
    Allows: alphanumeric, - : / . # _ | ^ * +
    Rejects: Spaces, semicolons, braces, quotes, parens.
    """
    if not uri:
        return False
    pattern = re.compile(r'^[a-zA-Z0-9_\-:/.#|^*+]+$')
    return bool(pattern.match(uri))
