"""
IDEAS for basic dispatch of field mounting

- NEXT avoid the required keywords! and string matching!

"""

from collections.abc import Callable
from typing import TYPE_CHECKING, Any, overload

if TYPE_CHECKING:
    from . import Forward, LazyField, RequiredField


# Overload 1: Required
@overload
def mount[T](
    *, required: type[T] | tuple[type, ...], doc: str = ""
) -> Any: ...


# Overload 2: Lazy
@overload
def mount[T](*, lazy: Callable[[Any], T], doc: str = "") -> Any: ...


# Overload 3: Forward
@overload
def mount(*, forward: str, method: str) -> Any: ...


# Implementation
def mount(**kwargs) -> Any:
    if "required" in kwargs:
        return RequiredField(types=kwargs["required"])
    if "lazy" in kwargs:
        return LazyField(loader=kwargs["lazy"])
    if "forward" in kwargs:
        return Forward(
            target_attr=kwargs["forward"], method_name=kwargs["method"]
        )

    raise ValueError("Invalid mount configuration")
