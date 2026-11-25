"""
brick.call

- Callable Fragments
- Func input ensured
                                                        reflect(+1)
                                 DependencyLevel.sstcore.brick[1:1]
"""

__all__: list[str] = [
    "ArgCast",
    "ArgCaster",
    "ArgCasting",
    "CastInput",
    "castarg",
    #
    "just_return",
]

from collections.abc import Callable as _Callable

from ._argcast import ArgCast, ArgCaster, ArgCasting, CastInput

castarg = ArgCast()  # TARGET: Main Result of ArgCast


def just_return[Target](value: Target, /) -> _Callable[..., Target]:
    """Wrap function that constantly returns value"""

    def constant_function(*_, **__) -> Target:
        return value

    return constant_function
