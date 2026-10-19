"""
IS_ACTIVE?

IS_ACTIVE
IS_ACTIVE
IS_ACTIVE
IS_ACTIVE
IS_ACTIVE
"""

import os
from typing import Any

ACTIVE_SCOPES: set[str] = set(
    filter(None, os.getenv("SST_DEBUG", "color,vault").split(","))
)


def is_active(module_or_name: str = "*") -> bool:
    if not ACTIVE_SCOPES:
        return False
    if "*" in ACTIVE_SCOPES:
        return True
    return any(scope in module_or_name.lower() for scope in ACTIVE_SCOPES)


def _noop(*_args: Any, **_kwargs: Any) -> None:
    pass
