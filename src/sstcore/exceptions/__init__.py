"""
SstError - Root of all Errors with amazing Cli and Log Defaults

- others mainly stand-alone
- (not implemented) RegistrySyncError maybe as Root for derived Registries

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

from .base import SstError
from .data import RegistrySyncError
from .general import (
    NotImplementedDispatchError,
    NotImplementedMixinError,
    PropertyNotInitializedError,
    TuiSelectorError,
)
from .util import PathGuardError, PathGuardReason
