"""
SstError - Root of all Errors with amazing Cli/Log defaults

- others mainly stand-alone
- (not implemented) RegistrySyncError maybe as Root for derived Registries
"""

__all__: list[str] = [
    "SstError",
    "RegistrySyncError",
    "NotImplementedDispatchError",
    "NotImplementedMixinError",
    "TuiSelectorError",
    "PropertyNotInitializedError",
]

from .base import (
    NotImplementedDispatchError,
    NotImplementedMixinError,
    PropertyNotInitializedError,
    RegistrySyncError,
    SstError,
    TuiSelectorError,
)
