"""
Provide Namespace for Exceptions before SstError is ready

- sstcore.error[L2] Avaliable for most of the Library
- sstcore.brick[L1] Build essential parts of the Errors
- sstcore. port[L0] Generally No Errors needed...

                                                 DependencyLevel[0]
"""

__all__: list[str] = [
    "SstCoreError",
    "FailedHackError",
]

# IMPORTANT::
# STRATEGY: prepare system that evolves from and after here
# - subclass detection
# - ghost color box
# ...


class SstCoreError(Exception):
    """Match and Catch all Errors on Global DependencyLevel[2]"""

    def __init__(self, *args) -> None:
        """Forward Args to Exception"""
        super().__init__(*args)

    def __repr__(self) -> str:
        """Show Everything"""
        _vars = [f"{k}={v!r}" for k, v in vars(self).items()]
        return f"{type(self).__name__}[{', '.join(_vars)}]"

    @classmethod
    def panic(cls, reason): ...


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### As there is enough space here left...
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class FailedHackError(SstCoreError):
    """
    It was a nice try, but...

    (I hope I don't have to  explain that this is mostly for internal tests...)
    """

    def __init__(self, *args) -> None:
        """Forward Args to Exception"""
        super().__init__("...I told you it will fail!", *args)
