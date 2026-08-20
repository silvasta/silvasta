"""
Create Namespace for custom Errors on Level 1 (error package is on Level 2)

- bricks package (Level 1) builds essential parts as well for the Exceptions

"""

__all__: list[str] = [
    "BaseError",
]


class BaseError(Exception):
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


class FailedHackError(BaseError):
    """It was a nice try, but..."""

    def __init__(self, *args) -> None:
        """Forward Args to Exception"""
        super().__init__("...I told you it will fail!", *args)
