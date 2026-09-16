"""
Store the logic of the initial pathguard grow

- from func to deco to hybrid to just the hybrid logic

"""

import functools
from collections.abc import Callable
from typing import Any, TypedDict, TypeGuard, Unpack

from sstcore.port.error import SstError


class HybridError(TypeError, SstError): ...


class HybridPolicy(TypedDict, total=False): ...


type WriteInStub = Any  # LATER: flag for StubGenerator?


def hybrid_factory[TargeT, **P, R](
    logic: Callable[..., R],
    is_target: Callable[[Any], TypeGuard[TargeT]],
) -> Callable[..., R]:
    """Bind the Hybrid construction"""

    def main(
        target: object = None, **policy: Unpack[HybridPolicy]
    ) -> WriteInStub:
        """Dispatch target to proper execution"""

        # INFO: remove if...:__doc__ before usage

        if is_target(target):
            """# Case 1: Direct Execution (Data provided)"""
            return logic(target, **policy)

        if callable(target):
            """Case 2: Bare Decorator (Function provided)"""

            @functools.wraps(target)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                return logic(target(*args, **kwargs), **policy)

            return wrapper

        if target is None:
            """Case 3: Parameterized Decorator (None provided, kwargs set)"""

            def decorator(fn: Callable[P, TargeT]) -> Callable[P, R]:
                """Recursive call to Case 2"""
                return main(fn, **policy)

            return decorator

        raise HybridError("Dispatch Failed!", target)  # LATER: better error

    return main
