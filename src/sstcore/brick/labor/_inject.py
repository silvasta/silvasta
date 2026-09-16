"""
Reflect and Modify

- not like a mixin injector but like changing attributes

"""

__all__: list[str] = [
    "just_return",
]

from collections.abc import Callable


# MOVE: to single box (if it ever exists)
# INFO: badly placed in reflect
def just_return[Target](constant: Target) -> Callable[..., Target]:
    """Wrap _target in function that returns constant value"""

    def constant_function(*_, **__) -> Target:
        return constant

    return constant_function  # MOVE: to sstcore.brick.format|func
