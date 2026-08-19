"""
Create Namespace for custom Errors on Level 1 (error package is on Level 2)

- bricks package (Level 1) builds essential parts as well for the Exceptions

"""

__all__: list[str] = [
    "BaseError",
]


class BaseError(Exception):
    """The root to catch all L1Errors"""

    def __init__(self, *args) -> None:
        """Forward Args to Exception"""
        super().__init__(*args)
