"""
Provide Namespace for Exceptions before SstError is ready

- sstcore.error[L2] Avaliable for most of the Library
- sstcore.brick[L1] Build essential parts the Errors
- sstcore. port[L0] Generally No Errors needed, ...

"""

__all__: list[str] = [
    "Error",
    "FailedHackError",
]


class Error(Exception):  # IMPORTANT: MOST LIKELY: this as SstError
    """Match and Catch all Level < 2 Errors"""

    def __init__(self, *args) -> None:
        """Forward Args to Exception"""
        super().__init__(*args)

    def __repr__(self) -> str:
        """Show Everything"""
        _vars = [f"{k}={v!r}" for k, v in vars(self).items()]
        return f"{type(self).__name__}[{', '.join(_vars)}]"


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### As there is enough space here left...
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class FailedHackError(Error):
    """It was a nice try, but..."""

    def __init__(self, *args) -> None:
        """Forward Args to Exception"""
        super().__init__("...I told you it will fail!", *args)
