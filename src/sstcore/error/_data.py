"""
Create Exceptions for the Domain Layer Data

- ...in progress
                                                       DependencyLevel[1]
"""

from ._base import SstError


# LATER: setup error for FileRegistry
# IDEA: replace by PathGuardError?
class RegistrySyncError(SstError):
    """Raise when FileRegistry State mismatches physical local disk"""
