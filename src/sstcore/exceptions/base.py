from typing import Any


class SstError(Exception):
    """Root of all custom Exceptions"""


class RegistrySyncError(FileNotFoundError, SstError):
    """Raise when FileRegistry State mismatches physical local disk"""


class NotImplementedDispatchError(NotImplementedError, SstError):
    """Raise when singledispatchmethod has missing TargetType"""

    # LATER: make first argument more visible, it is the failing one
    def __init__(self, first: Any, *args: Any, kwargs=None):
        self.args: tuple[Any] = args

        def _render(target: Any):
            return f"{type(target).__name__}: {target}"

        _first = f"MissingTargetType={_render(first)}"
        _args = f"args=({', '.join([_render(target) for target in args])})"
        _kwargs = f"kwargs=({_render(kwargs) if kwargs else ''}"

        super().__init__(", ".join([_first, _args, _kwargs]))


class NotImplementedMixinError(NotImplementedError, SstError):
    """Raised when singledispatchmethod don't provide target type"""

    def __init__(self, base, mixin, func):
        self.base = base
        self.mixin = mixin
        self.func = func
        super().__init__(f"Problem for {mixin=} of {base=} in {func=}")


class TuiSelectorError(RuntimeError, SstError):
    def __init__(self, message=None):
        if message is None:
            message = "It was an easy Selection... how can you Fail this?"
        super().__init__(message)
