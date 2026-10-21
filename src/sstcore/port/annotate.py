"""
Write and Expose the Shape of the Dynamically created Classes

- Analyze Mixins and Combinatorials and Draw the Result
- Provide the Type Checker with best Information (UX++)

                                    DependencyLevel.sstcore.port[4]
"""

import inspect

__all__: list[str] = [
    "StackAnnotator",
    "ProtoTyper",
    #
    "stub_types",
]


from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any
from typing import Protocol as _Protocol

from ._types import stub_types
from .shape import Typer  # 0
from .solid import EnumMode  # 1

_stub = stub_types


class MetaAnnotator(Typer, _Protocol):
    """Analyze the Meta Construction and Support with Typed Blueprints"""


class ProtoTyper(Typer, _Protocol):
    """Summarize the Builder Pipeline Protocols and Annotate the Mixes"""


class StackAnnotator(Typer, _Protocol):
    """Orchestrate the Combinatorial Stacking Pipeline"""


class LazyTyper(Typer, _Protocol):
    # TASK: identify all location where it makes sense:
    # - sstcore.__init__ already like that
    # - second priority has system
    # - if it works well, just continue on all toplevel packages
    """Render the __init__.pyi to automate the Lazy __getattr__ __init__.py"""


#  LINE: -- _forge_typer -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@dataclass(slots=True, frozen=True)
class MethodSpec:
    name: str
    signatures: list[inspect.Signature]
    is_overloaded: bool = False


@dataclass(slots=True, frozen=True)
class ProtocolSpec:
    name: str
    attributes: dict[str, type] = field(default_factory=dict)
    properties: dict[str, type] = field(default_factory=dict)
    methods: dict[str, MethodSpec] = field(default_factory=dict)


#  LINE: -- write.engine1 -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@dataclass(frozen=True)
class ParamDTO:
    name: str
    annotation: str
    default: str | None = None


@dataclass(frozen=True)
class MethodDTO:
    name: str
    params: list[ParamDTO]
    return_type: str
    is_property: bool = False
    is_overload: bool = False


@dataclass(frozen=True)
class StubJobDTO:
    """The Universal Blueprint for the Writer EnumMachine"""

    target_module: str  # e.g., "sstcore.brick.stack"
    class_name: str  # e.g., "StackCore"
    methods: list[MethodDTO] = field(default_factory=list)
    attributes: dict[str, str] = field(default_factory=dict)
    bases: list[str] = field(default_factory=lambda: ["Protocol"])


#  LINE: -- write.jobs -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class JobKind(EnumMode):
    STACK = "stack"
    PROTOCOL = "protocol"
    MIXIN = "mixin"


@dataclass(frozen=True, slots=True)
class StubJob3:
    """Work order for StubFileEnumMachine. No callables, no paths as objects."""

    kind: JobKind
    public: str  # DTO_STACK
    class_name: str  # GreeterEmpty
    package: str  # sstcore.brick.stack
    stub_file: str  # _stubs/_greeter.pyi
    payload: Mapping[str, Any]  # INFO: bus
    overlay: bool = True


#  LINE: -- write.engine2 -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@dataclass(slots=True, frozen=True)
class StubJobDTO4:  # INFO: write.engine2
    """Transport contract defining a single stub generation and write task."""

    public_symbol: str  # e.g., 'DTO_STACK'
    class_prefix: str  # e.g., 'Greeter'
    source_target: Any  # Runtime object or Core supplying schema
    target_module: str  # Dotted target e.g., 'sstcore.brick.stack'
    renderer: Callable[[Any, str], str]  # (source, class_name) -> stub_str
    sub_dir: str = "_stubs"
