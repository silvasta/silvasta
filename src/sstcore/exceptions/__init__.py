"""
SstError - Root of all Errors with amazing Cli and Log Defaults

- others mainly stand-alone
- (not implemented) RegistrySyncError maybe as Root for derived Registries

                                                          PackageLevel[1]
"""  # TODO:

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
