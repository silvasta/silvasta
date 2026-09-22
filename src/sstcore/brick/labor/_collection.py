"""
Collect Functions and Method-Templates

                             DependencyLevel.sstcore.brick.labor[0]
"""

__all__: list[str] = [
    "just_return",
]

from collections.abc import Callable


def just_return[Target](constant: Target) -> Callable[..., Target]:
    """Wrap function that constantly returns _target as value"""

    def constant_function(*_, **__) -> Target:
        return constant

    return constant_function
