from typing import Any


class SstError(Exception):
    """Root of all custom Exceptions"""


class RegistrySyncError(FileNotFoundError, SstError):
    """Raised when the FileRegistry state does not match the physical local disk."""


class NotImplementedDispatchError(NotImplementedError, SstError):
    """Raised when singledispatchmethod don't provide target type"""

    def __init__(self, *args: Any):
        self.args: tuple[Any] = args

        def _display(target: Any):
            return f"{type(target)=}, {target=}"

        msg: str = "-|-".join(_display(target) for target in args)
        super().__init__(f"Function can't process: {msg}")


class NotImplementedMixinError(NotImplementedError, SstError):
    """Raised when singledispatchmethod don't provide target type"""

    def __init__(self, base, mixin, func):
        self.base = base
        self.mixin = mixin
        self.func = func
        super().__init__(f"Promblem for {mixin=} of {base=} in {func=}")


class FailedSelectionError(RuntimeError, SstError):
    def __init__(self, message=None):
        if message is None:
            message = "It was an easy Selection... how can you Fail this?"
        super().__init__(message)
