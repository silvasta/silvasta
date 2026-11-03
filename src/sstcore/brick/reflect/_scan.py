"""
Inspect arbitrary objects and safely pull out specific attributes

                             DependencyLevel.sstcore.brick.labor[0]
"""

__all__: list[str] = [
    "data",
    "pydantic",
]


from collections.abc import Iterable
from typing import Any

from ...port.empty import VOID, MayBeNo
from ...port.represent import PydanticModel, is_basemodel
from ._check import AttrFilter

_IGNORE = (classmethod, staticmethod, property)


def _prepare_filter(
    filter: MayBeNo[AttrFilter] = VOID, exclude: Iterable[str] = ()
) -> AttrFilter:
    # IDEA:[1] make this Annotated and resolve by @castarg
    # IDEA:[2] make this classmethod of AttrFilter
    return (
        AttrFilter.default(exclude=exclude)
        if filter is VOID
        else AttrFilter.pass_all(exclude=exclude)
        if filter is None
        else filter.excluding(*exclude)
    )


def data(
    target: Any,
    /,
    filter: MayBeNo[AttrFilter] = VOID,
    *,
    exclude: Iterable[str] = (),
) -> dict[str, Any]:
    """Extract and Filter Object Attributes with Excludes"""

    if is_basemodel(target):
        # IDEA: extracted = _scan_pydantic(target)
        return pydantic(target, filter, exclude=exclude)

    extracted: dict[str, Any] = _scan_object(target)

    return _prepare_filter(filter, exclude).filter_dict(extracted)


def pydantic(
    # AI: is this even worth to keep?
    # - every caller can directly check if it is a BaseModel and directly apply model_dump
    # - the filter needs to be created there as well, otherwise the default can be used there
    # still 3 steps directly combined in 1 call, cheap or very cheap to keep
    target: PydanticModel,
    /,
    filter: MayBeNo[AttrFilter] = VOID,
    *,
    exclude: Iterable[str] = (),
) -> dict[str, Any]:
    """
    Extract and Filter pydantic.BaseModel Attributes with Excludes

    - crash if BaseModel Protocol is missed (nearby confirm BaseModel)
    """

    if is_basemodel(target):
        dumped: dict[str, Any] = target.model_dump(exclude=set(exclude))
        # IDEA: AttrFilter.maybeno(filter,exclude).mapped(dumped)
        return _prepare_filter(filter, exclude).filter_dict(dumped)

    raise ValueError(f"Invalid 'PydanticModel' {type(target)}::{target}")


def _scan_object(target: Any) -> dict[str, Any]:  # LATER: expose?
    """Extract and Filter Instance and relevant Class Attributes"""

    result: dict[str, Any] = {}
    cls: type = target if isinstance(target, type) else type(target)

    # LATER: design this in Filter
    # LATER: use ._collect or port.link._operate.Collector

    for base in reversed(cls.__mro__):
        if base is object:
            continue
        for k, v in vars(base).items():
            if not callable(v) and not isinstance(v, _IGNORE):
                result[k] = v

    if hasattr(target, "__dict__"):
        result.update(vars(target))

    return result
