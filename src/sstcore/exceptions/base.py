from typing import Any


class SstError(Exception):
    """Root of all custom Exceptions"""


class RegistrySyncError(FileNotFoundError, SstError):
    """Raised when the FileRegistry state does not match the physical local disk."""


class NotImplementedDispachError(NotImplementedError, SstError):
    """Raised when singledispatchmethod don't provide target type"""

    def __init__(self, *args: Any):
        def _display(target: Any):
            return f"{type(target)=}, {target=}"

        msg: str = "-|-".join(_display(target) for target in args)
        super().__init__(f"Function can't process: {msg}")
