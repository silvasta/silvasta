"""
Define the Shape of Views and what they Represent.

- temporary refactored...
                                    DependencyLevel.sstcore.port[8]
"""

__all__: list[str] = [
    "SstView",
    "SstViewType",
    # the 5 dunders
    "Stringable",
    "LogStringable",
    "LogSerializable",
    "CliSerializable",
    "RichView",
    # checks
    "CliRenderable",
    "is_cli_renderable",
    "Richable",
    "RichConsolable",
    "is_richable",
    "PydanticModel",
    "is_basemodel",
    # meta/cls
    "ClassRendering",
    "CliDtoCreator",
]


import typing as _typing

from ._types import _LogStringable as LogStringable
from ._types import _Richable as Richable
from ._types import _RichConsolable as RichConsolable
from ._types import _RichView as RichView
from ._types import _Stringable as Stringable
from .event.dto import CliDTO as _CliDTO
from .event.dto import LogDTO as _LogDTO
from .event.dto import _CliRenderable as CliRenderable
from .event.dto import _CliSerializable as CliSerializable
from .event.dto import _LogSerializable as LogSerializable
from .link import portlink as _portlink

type SstViewType = CliSerializable | LogSerializable  # LATER: add TuiViewtype


class SstView(_typing.Protocol):
    """Show all essential Views of the Library"""

    # IMPORTANT: before publish, think about:
    # IDEAS:  __sstcli__ and __sstlog__

    def __str__(self) -> str:
        """Provide a representing Name"""

    def __repr__(self) -> str:
        """Concatenate Object Information to String"""

    def __cli__(self) -> _CliDTO:
        """Snapshot the Target for Visualization"""

    def __log__(self) -> _LogDTO:
        """Structure Object Information as DTO"""

    def __rich__(self) -> Richable:
        """Provide a colorized Name for further processing"""


@_portlink(SstView)
class _ViewDummy(
    Stringable,
    LogSerializable,
    CliSerializable,
    LogStringable,
    RichView,
):  # LATER: actually needed? will dunder ever change? maybe hide somehow below
    """Ensure the distributed view types match SstView"""


#  LINE: -- Checks -- -- - -- -- - -- -- - -- -- - -- -- - -- --


def is_cli_renderable(obj: object) -> _typing.TypeIs[CliRenderable]:
    """Static and Dynamic Check that narrows Type to CliRenderable"""
    return isinstance(obj, (CliSerializable, RichView, RichConsolable, str))


def is_richable(obj: object) -> _typing.TypeIs[Richable]:
    """Static and Dynamic Check that narrows Type to Rich Renderable"""
    return isinstance(obj, (RichView, RichConsolable, str))


@_typing.runtime_checkable
class PydanticModel(_typing.Protocol):
    """Find BaseModels without importing them"""

    def __pydantic_validator__(self): ...
    def model_dump(self) -> dict[str, _typing.Any]: ...


def is_basemodel(obj: object) -> _typing.TypeIs[PydanticModel]:
    """Static and Dynamic Check that narrows to minimal pydantic.BaseModel"""
    return isinstance(obj, (PydanticModel))


#  LINE: -- MetaView - Operations on Classes (forge.engine)  -- -- - -- ---


@_typing.runtime_checkable
class ClassRendering(_typing.Protocol):
    def __call__(self, cls: type) -> str:
        """Process Classes like if they where Instances (e.g StaticFuncMeta)"""


@_typing.runtime_checkable
class CliDtoCreator(_typing.Protocol):
    """Annotate the ability to launch CliDTO units"""

    def __call__(self, cls: type) -> _CliDTO:
        """Produce DTO for... only cls? or general? dispatch?"""
