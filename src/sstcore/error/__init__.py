"""
SstError - Root of all Errors with __cli__ and __log__ Defaults

                                                       DependencyLevel[1]
"""

__all__: list[str] = [
    "SstError",
    # data
    "RegistrySyncError",
    # general
    "NotImplementedDispatchError",
    "NotImplementedMixinError",
    "TuiSelectorError",
    "PropertyNotInitializedError",
    # util
    "PathGuardError",
    "PathGuardReason",
]

from ._base import SstError
from ._data import RegistrySyncError
from ._general import (
    NotImplementedDispatchError,
    NotImplementedMixinError,
    PropertyNotInitializedError,
    TuiSelectorError,
)
from ._util import PathGuardError, PathGuardReason
