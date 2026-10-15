"""
Define the Shape of Views and what they Represent.

- temporary refactored...
                                    DependencyLevel.sstcore.port[8]
"""

__all__: list[str] = [
    "SstFullView",
    # the 5 dunders
    "CliSerializable",
    "LogSerializable",
    "LogStringable",
    "Stringable",
    "RichView",
    # checks
    "SstView",
    "CliRenderable",
    "is_serializable",
    "is_renderable",
    "is_richable",
    "is_basemodel",
    "Richable",
    "RichConsolable",
    "PydanticModel",
    # meta/cls
    "ClsRendering",
    "CliDtoCreator",
]


import typing as _typing

from ._types import _LogStringable as LogStringable
from ._types import _RichConsolable as RichConsolable
from ._types import _RichView as RichView
from ._types import _Stringable as Stringable
from .event.dto import CliDTO as _CliDTO
from .event.dto import LogDTO as _LogDTO
from .event.dto import _CliSerializable as CliSerializable
from .event.dto import _LogSerializable as LogSerializable
from .link import portlink as _portlink


class SstFullView(_typing.Protocol):
    """Show all essential Views of the Library"""

    def __cli__(self) -> _CliDTO:
        """Snapshot Target for Visualization"""

    def __log__(self) -> _LogDTO:
        """Structure Object Information as DTO"""

    def __repr__(self) -> str:
        """Concatenate Object Information to String"""

    def __str__(self) -> str:
        """Provide a representing Name"""

    def __rich__(self) -> Richable:
        """Provide a Colorized Name"""


class _SstTestView(_typing.Protocol):
    """Show all essential Views of the Library"""

    def __sstcli__(self) -> _CliDTO:
        """Snapshot Target for Visualization"""

    def __sstlog__(self) -> _LogDTO:
        """Structure Object Information as DTO"""

    def __repr__(self) -> str:
        """Concatenate Object Information to String"""

    def __str__(self) -> str:
        """Provide a representing Name"""

    def __rich__(self) -> Richable:
        """Provide a Colorized Name"""


# IMPORTANT: before publish, think about __


class _SstTestView(_typing.Protocol):
    """Show all essential Views of the Library"""

    def __sst_cli__(self) -> _CliDTO:
        """Snapshot Target for Visualization"""

    def __sst_log__(self) -> _LogDTO:
        """Structure Object Information as DTO"""

    def __repr__(self) -> str:
        """Concatenate Object Information to String"""

    def __str__(self) -> str:
        """Provide a representing Name"""

    def __rich__(self) -> Richable:
        """Provide a Colorized Name"""


type SstView = CliSerializable | LogSerializable  # LATER: TuiSerializable
type CliRenderable = CliSerializable | Richable
type Richable = RichView | RichConsolable | str


def is_serializable(target: _typing.Any, /) -> _typing.TypeIs[SstView]:
    """Static and Dynamic Check that narrows to Serializable SstView Type"""
    return isinstance(target, (CliSerializable, LogSerializable))


def is_renderable(target: _typing.Any, /) -> _typing.TypeIs[CliRenderable]:
    """Static and Dynamic Check that narrows Type to CliRenderable"""
    return isinstance(target, (CliSerializable, RichView, RichConsolable, str))


def is_richable(target: _typing.Any, /) -> _typing.TypeIs[Richable]:
    """Static and Dynamic Check that narrows Type to Rich Renderable"""
    return isinstance(target, (RichView, RichConsolable, str))


def is_basemodel(target: _typing.Any, /) -> _typing.TypeIs[PydanticModel]:
    """Static and Dynamic Check that narrows to minimal pydantic.BaseModel"""
    return isinstance(target, (PydanticModel))


@_typing.runtime_checkable
class PydanticModel(_typing.Protocol):
    """Find BaseModels without importing them"""

    def __pydantic_validator__(self): ...
    def model_dump(self) -> dict[str, _typing.Any]: ...


class _Richable(_typing.Protocol):
    def __rich__(self): ...
    def __rich_console__(self):
        """Just extend the Renderable type"""


@_portlink(_Richable)
class _RichDummy(
    RichView,
    RichConsolable,
):  # LATER: actually needed? will dunder ever change? maybe hide somehow below
    """Ensure the distributed view types match Richable"""


@_portlink(SstFullView)
class _ViewDummy(
    CliSerializable,
    LogStringable,
    LogSerializable,
    Stringable,
    RichView,
):  # LATER: actually needed? will dunder ever change? maybe hide somehow below
    """Ensure the distributed view types match SstView"""


#  LINE: -- MetaView - Operations on Classes (forge.engine)  -- -- - -- ---


@_typing.runtime_checkable
class ClsRendering(_typing.Protocol):
    def __call__(self, cls: type) -> str:
        """Process Classes like if they where Instances (e.g StaticFuncMeta)"""


@_typing.runtime_checkable
class CliDtoCreator(_typing.Protocol):
    """Annotate the ability to launch CliDTO units"""

    def __call__(self, cls: type) -> _CliDTO:
        """Produce DTO for... only cls? or general? dispatch?"""
