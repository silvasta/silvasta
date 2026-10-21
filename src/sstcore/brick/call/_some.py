"""
Collect Functions and Method-Templates

                             DependencyLevel.sstcore.brick.labor[0]
"""

__all__: list[str] = [
    "just_return",
]

from collections.abc import Callable


def just_return[Target](value: Target, /) -> Callable[..., Target]:
    """Wrap function that constantly returns value"""

    def constant_function(*_, **__) -> Target:
        return value

    return constant_function
