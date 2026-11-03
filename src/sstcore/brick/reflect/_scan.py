"""
Inspect arbitrary objects and safely pull out specific attributes

                             DependencyLevel.sstcore.brick.labor[0]
"""

__all__: list[str] = [
    "data",
    "pydantic",
]


from collections.abc import Callable, Iterable
from typing import Any

from ...port.empty import VOID, MayBeNo
from ...port.represent import PydanticModel, is_basemodel
from ._check import AttrFilter

_IGNORE = (classmethod, staticmethod, property)


def data(
    target: Any,
    /,
    filter: MayBeNo[AttrFilter] = VOID,
    *,
    exclude: Iterable[str] = (),
) -> dict[str, Any]:
    """
    Extract and Filter Object Attributes with Excludes

    - Use filter=None for no filtering, default for no change filter=VOID
    """

    if is_basemodel(target):
        return pydantic(target, filter, exclude=exclude)

    active = AttrFilter.resolve(filter, exclude=exclude)
    return _scan_object(target, active)


def pydantic(
    target: PydanticModel,
    /,
    filter: MayBeNo[AttrFilter] = VOID,
    *,
    exclude: Iterable[str] = (),
) -> dict[str, Any]:
    """
    Extract and Filter pydantic.BaseModel Attributes with Excludes

    - Use filter=None for no filtering, default for no change filter=VOID
    """

    if not is_basemodel(target):
        raise TypeError(f"Invalid 'PydanticModel' {type(target)}::{target}")

    active_filter: AttrFilter = AttrFilter.resolve(filter, exclude=exclude)
    dump_exclude: set[str] = {
        name  #
        for name in target.model_fields.keys()
        if not active_filter(name)
    }
    dumped: dict[str, Any] = target.model_dump(exclude=dump_exclude)

    return active_filter.mapped(dumped)


def _scan_object(  # LATER: expose?
    target: Any, /, accept: Callable[[str], bool] | None = None
) -> dict[str, Any]:
    """Extract and Filter Instance and relevant Class Attributes"""

    accept: Callable[[str], bool] = accept or AttrFilter.default()
    is_cls: bool = isinstance(target, type)
    cls: type = target if is_cls else type(target)

    # LATER: compare with port.link.Detector or ._detect and forge._labor

    result: dict[str, Any] = {}

    for base in reversed(cls.__mro__):
        if base is object:
            continue
        for k, v in vars(base).items():
            if not accept(k):
                continue
            if not callable(v) and not isinstance(v, _IGNORE):
                result[k] = v
            else:
                # If a subclass overrides a class data attribute with a
                # property or method, ensure the shadowed data isn't kept.
                result.pop(k, None)

    if not is_cls and hasattr(target, "__dict__"):
        for k, v in vars(target).items():
            if accept(k):
                result[k] = v

    return result
