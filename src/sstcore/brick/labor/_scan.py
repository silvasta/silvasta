"""
Inspect arbitrary objects and safely pull out specific attributes

                             DependencyLevel.sstcore.brick.labor[0]
"""

__all__: list[str] = [  # NEXT: module name, scan, detect?
    "data",
    "pydantic",
    #
    "is_private",
    "is_dunder",
    "AttrFilter",
]


from collections.abc import Callable
from typing import Any, NamedTuple

from ...port.calling import PydanticModel

# IDEA: scan even deeper:
# scan.data(target) -> vars(target), filtered
# scan.full(target) -> dir(target), filtered
# - maybe with some (guarded) extraction


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


#  LINE: -- Extensions -- -- - -- -- - -- -- - -- -- - -- -- - -- --


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


#  LINE: -- Filter and Flags for Attrs -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def is_private(_attr: str) -> bool:
    # LATER: str|list[str]->bool|list[bool]
    return _attr.startswith("_")


def is_dunder(_attr: str) -> bool:
    # LATER: str|list[str]->bool|list[bool]
    return _attr.startswith("__") and _attr.endswith("__")


class AttrFilter(NamedTuple):
    """Collect Flags and provide corresponding Filter"""

    public: bool = True
    private: bool = False
    dunder: bool = False

    def get_filter(self) -> Callable[[str], bool]:
        """Separate by public/private/dunder with dunder not in private"""
        match self.public, self.private, self.dunder:
            case (False, False, False):
                raise ValueError("All flags set zero! No result!")

            case (False, False, True):
                return lambda attr: is_dunder(attr)

            case (False, True, False):
                return lambda attr: is_private(attr) and not is_dunder(attr)

            case (False, True, True):
                return lambda attr: is_private(attr)

            case (True, False, False):
                return lambda attr: not is_private(attr)

            case (True, False, True):
                return lambda attr: is_dunder(attr) or not is_private(attr)

            case (True, True, False):
                return lambda attr: not is_dunder(attr)

            case (True, True, True):
                return lambda _attr: True
