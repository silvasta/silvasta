"""
Funtcions, Callables and Checks

                                                 DependencyLevel[0]
"""

__all__: list[str] = [
    "Stacking",
    "ClassRendering",
    # views
    "Reprable",  # __repr__
    "Stringable",  # __str__
    # adapter
    "RichRendering",  # str or __rich__ or __rich_console__
    "RichCasting",  # __rich__
    "PydanticModel",
]

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ClassRendering(Protocol):
    def __call__(self, cls: type) -> str:
        """Process Classes like if they where Instances (e.g StaticFuncMeta)"""


class Stacking(Protocol):
    def __getattr__(self, name: str) -> Stacking:
        """Stack Attributes on top of each other by attribute calls"""


@runtime_checkable
class Colorizing(Protocol):
    # TODO: at least one of:
    # - Sanitizing:Stringable->str (Formatting)
    # - Sanitizing:Any->Stringable (Sanitizing)
    # - Sanitizing:Any->str (Stringing)
    def __call__(self, text: Stringable) -> str:
        """Forward text-like object after processing and ensuring string"""


@runtime_checkable
class Listening[T](Protocol):
    def __call__(self, target: T) -> T:
        """Forward target after routing and inspection"""


#  LINE: -- views -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class Stringable(Protocol):
    def __str__(self) -> str: ...


@runtime_checkable
class String(Protocol):  # TASK: check dispatch, runtime_checkable or not
    def __str__(self) -> str: ...


@runtime_checkable
class Reprable(Protocol):  # MOVE: to .call?
    def __repr__(self) -> str: ...


#  LINE: -- adapter -- -- - -- -- - -- -- - -- -- - -- -- - -- --

type RichRendering = RichCasting | _RichConsolable | str


@runtime_checkable
class RichCasting(Protocol):
    def __rich__(self) -> RichRendering: ...


class _RichConsolable(Protocol):
    def __rich_console__(self):
        """Just extend the Renderable type"""


@runtime_checkable
class PydanticModel(Protocol):  # MOVE: but where?
    """Find BaseModels without importing them"""

    def __pydantic_validator__(self): ...
    def model_dump(self) -> dict[str, Any]: ...
