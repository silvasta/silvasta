from .base import SstError


# LATER: setup error for FileRegistry
class RegistrySyncError(SstError):
    """Raise when FileRegistry State mismatches physical local disk"""
