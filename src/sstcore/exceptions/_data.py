"""
Create Exceptions for the Domain Layer Data

- ...in progress
                                                           ModuleLevel[1]
"""

from ._base import SstError


# LATER: setup error for FileRegistry
class RegistrySyncError(SstError):
    """Raise when FileRegistry State mismatches physical local disk"""
