"""
Create Exceptions for the Domain Layer Data

- ...in progress
                                                       DependencyLevel[1]
"""

from ._base import SstCoreError


# LATER: setup error for FileRegistry
# IDEA: replace by PathGuardError?
# NOTE: was intended for FilesRegistry, before Registry, maybe update?
class RegistrySyncError(SstCoreError):
    """Raise when FileRegistry State mismatches physical local disk"""
