"""
Inspect arbitrary objects and safely pull out specific attributes

                             DependencyLevel.sstcore.brick.labor[0]
"""

__all__: list[str] = [  # NEXT: module name, scan, detect?
    "data",
    "pydantic",
]


from collections.abc import Callable
from typing import Any

from ...port.represent import PydanticModel
from ._check import AttrFilter


def _old_data(
    target: Any,
    /,
    public: bool = True,
    # LATER: get here flags by ArgCast, show single flags in pyi, maybe dto
    private: bool = False,
    dunder: bool = False,
    *,
    exclude: set[str] | None = None,
) -> dict[str, Any]:
    """Extract public attributes filtered by exclude"""

    flags = AttrFilter(public, private, dunder)
    _filter: Callable[[str], bool] = flags.get_filter()  # ty:ignore
    exclude: set[str] = exclude or set()

    return {
        k: v
        for k, v in vars(target).items()
        # LATER: check dir(target) as well, dispatch
        if _filter(k) and k not in exclude
    }


def data(
    target: Any,
    /,
    filter: AttrFilter | None = None,
    *,
    exclude: set[str] | None = None,
) -> dict[str, Any]:
    """Extract attributes matching filter criteria."""
    active_filter: AttrFilter = filter or AttrFilter.default()

    if exclude:
        active_filter: AttrFilter = active_filter.excluding(*exclude)

    return active_filter.filter_dict(vars(target))


def pydantic(
    target: Any, /, *, exclude: set[str] | None = None
) -> dict[str, Any]:
    """Extract public Pydantic attributes filtered by exclude"""

    exclude: set[str] = exclude or set()

    if isinstance(target, PydanticModel):
        # TODO: extension of data, including FilterFlags?
        return target.model_dump(exclude=exclude)
    else:
        # LATER: raise or: return data(target, exclude) ??
        raise ValueError("Target is not BaseModel!")
