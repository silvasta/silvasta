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

from ...port.calling import PydanticModel
from ._check import AttrFilter


def data(
    _target: Any,
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
    _filter: Callable[[str], bool] = flags.get_filter()
    exclude: set[str] = exclude or set()

    return {
        k: v
        for k, v in vars(_target).items()
        # LATER: check dir(_target) as well, dispatch
        if not _filter(k) and k not in exclude
    }


# IDEA: scan even deeper:
# scan.data(target) -> vars(target), filtered
# scan.full(target) -> dir(target), filtered
# - maybe with some (guarded) extraction


def pydantic(
    _target: Any, /, *, exclude: set[str] | None = None
) -> dict[str, Any]:
    """Extract public Pydantic attributes filtered by exclude"""

    exclude: set[str] = exclude or set()

    if isinstance(_target, PydanticModel):
        # TODO: extension of data, including FilterFlags?
        return _target.model_dump(exclude=exclude)
    else:
        # LATER: raise or: return data(_target, exclude) ??
        raise ValueError("Target is not BaseModel!")
