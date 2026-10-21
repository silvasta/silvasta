"""
Show the Full Stack of the Hybrid Decorator Pipeline

- Case 1: is_target -> Direct Function Execution: logic(*args,*kwargs)
- Case 2: callable(target) -> Bare Decorator: @logic on top of any function
- Case 3: None -> Parametrized Decorator: @logic(**kwargs) bind param in-place

- hybrid_factory: binds all together with injectable logic and target detection

"""

__all__: list[str] = [
    "hybrid_factory",
]


import functools
from collections.abc import Callable
from typing import Any, TypedDict, TypeGuard, Unpack

from ...port.raising import SstCoreError


class HybridError(TypeError, SstCoreError): ...


class HybridPolicy(TypedDict, total=False): ...


# TASK: Parameterization!


def hybrid_factory[TargeT, **P, R](
    logic: Callable[..., R],
    is_target: Callable[[Any], TypeGuard[TargeT]],
) -> Callable[..., R]:
    """Bind the Hybrid construction"""

    def main(target: object = None, **policy: Unpack[HybridPolicy]):
        """Dispatch target to corresponding Execution pattern"""

        if is_target(target):
            return logic(target, **policy)

        if callable(target):

            @functools.wraps(target)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                return logic(target(*args, **kwargs), **policy)

            return wrapper

        if target is None:
            """Case 3: Parameterized Decorator"""

            def decorator(fn: Callable[P, TargeT]) -> Callable[P, R]:
                """Recursive call to Case 2"""
                return main(fn, **policy)

            return decorator

        raise HybridError("Dispatch Failed!", target)  # LATER: better error

    return main
