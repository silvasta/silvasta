"""
The View Table

-
"""

__all__: list[str] = [
    # "",
]

from datetime import datetime
from string import Template
from typing import Any, Protocol, runtime_checkable

from msgspec import Struct

from ....brick.func import FunctorBase
from ....brick.vault import ListRegistry
from ....brick.vault._extras import RegistryField
from ....port.attach import FieldLoader
from ....port.event.dto import CliDTO, LogDTO
from ....port.register import ListRegister, Registry


@runtime_checkable
class CliRenderable(Protocol):
    def __cli__(self) -> CliDTO: ...


@runtime_checkable
class LogSerializable(Protocol):
    def __log__(self) -> LogDTO: ...


@runtime_checkable
class Reprable(Protocol):
    def __repr__(self) -> str: ...


@runtime_checkable
class Stringable(Protocol):
    def __str__(self) -> str: ...


@runtime_checkable
class RichRenderable(Protocol):
    def __rich__(self) -> Renderable: ...


@runtime_checkable
class FullView(
    CliRenderable,
    LogSerializable,
    Reprable,
    Stringable,
    RichRenderable,
    Protocol,
):
    """Type the view when all bricks are set"""


type Renderable = RichRenderable | _RichConsolable | CliRenderable | str


class _RichConsolable(Protocol):
    def __rich_console__(self):
        """Just extend the Renderable type"""


class Tstring(Struct):
    tstring: str
    normalized: str
    written: str
    final: str
    units: list[Any] = []
    time: datetime = datetime.now()  # NOTE: is this fine on msgspec?


class Render(Protocol): ...


class FullRenderPipeline(Protocol):
    def __call__(self, string: Template) -> Renderable:
        """Input to Output Relation"""


class TstringInternal(Protocol):
    def __call__(self, extracted: object) -> Stringable:
        """Path from extracted bracket object until boarder"""


class ReadyToRender(Struct):
    text: str
    units: list[Any] = []
    colorset: Any = None
    time: datetime = datetime.now()  # NOTE: is this fine on msgspec?


class AdapterRendernig(Protocol):
    def __call__(self, formatted: Stringable) -> Renderable:
        """Final step from internal rendering to the outside execution"""


class TstringHistoryVault(ListRegister, Protocol):
    """The DTO validation, storage and evaluation"""


class RenderMatchTable(Registry, Protocol):
    """Registered objects and functions, which type?"""


x: list[Tstring] = []


def launch_list_reg() -> FieldLoader[Registry[list, Tstring, str]]:
    def loader[Tstring, str]() -> ListRegistry:
        return ListRegistry()

    return loader


class FuncOperator(FunctorBase):
    data = RegistryField(loader=launch_list_reg)


class FrequencyGate:
    def __init__(self, inner: ViewFn, noisy_after: int = 3) -> None:
        self.inner = inner
        self.noisy_after = noisy_after
        self.seen: Counter[str] = Counter()

    def __call__(self, value: Any, interp: Interpolation) -> Piece:
        key = f"{type(value).__qualname__}:{interp.expression}"
        self.seen[key] += 1
        if self.seen[key] > self.noisy_after:
            return Text(
                f"{type(value).__name__}·{self.seen[key]}", style="dim"
            )
        return self.inner(value, interp)
