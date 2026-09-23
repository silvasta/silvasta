"""
Write and Expose the Shape of the Dynamically created Classes

- Analyze Mixins and Combinatorials and Draw the Result
- Provide the Type Checker with best Information (UX++)

                                    DependencyLevel.sstcore.port[1]
"""

__all__: list[str] = [
    "StubFileGenerator",
    "StackAnnotator",
    "ProtoTyper",
]


from collections.abc import Callable, Mapping
from dataclasses import dataclass as _dataclass
from dataclasses import field
from pathlib import Path
from typing import Any, ClassVar, Self
from typing import Protocol as _Protocol

from .attach import ConfigDescriptor
from .govern import Machine, Mode
from .shape import Typer


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


#  LINE: -- Automat -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class JobKind(Mode):
    STACK = "stack"
    PROTOCOL = "protocol"
    MIXIN = "mixin"


class StubFileGenerator(Machine):
    """Execute the Mechanical and Rule based part of the pyi writing"""

    def report(self):  # TODO: think about invisible logging
        """Precisely record any single step into a structured table"""


#  LINE: -- TaskDTO -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@_dataclass(frozen=True)
class ParamDTO:
    name: str
    annotation: str
    default: str | None = None


@_dataclass(frozen=True)
class MethodDTO:
    name: str
    params: list[ParamDTO]
    return_type: str
    is_property: bool = False
    is_overload: bool = False


#  LINE: -- JobDTO -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class JobDTO1:
    _registry: ClassVar[dict[str, type[Self]]] = {}

    public: ConfigDescriptor[str]  # read/write с валидацией
    prefix: ConfigDescriptor[str]
    package: ConfigDescriptor[str | None]
    content: ConfigDescriptor[str]  # готовый stub-текст
    target: ConfigDescriptor[Path]


@_dataclass(frozen=True)
class StubJobDTO:
    """The Universal Blueprint for the Writer Machine"""

    target_module: str  # e.g., "sstcore.brick.stack"
    class_name: str  # e.g., "StackCore"
    methods: list[MethodDTO] = field(default_factory=list)
    attributes: dict[str, str] = field(default_factory=dict)
    bases: list[str] = field(default_factory=lambda: ["Protocol"])


#  LINE: -- StubJob -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@_dataclass(frozen=True)
class StubJob1:
    public: str
    prefix: str
    package: str | None = None


@_dataclass(frozen=True, slots=True)
class StubJob2:
    """Transport container for a single stub-writing task."""

    public: str  # binding name in __init__.py, e.g. "DTO_STACK"
    prefix: str  # e.g. "Greeter", "Printer"
    package: str | None = None  # override; else inferred at write time
    content: str = ""  # rendered stub text (filled by Typer)
    target_file: str = ""  # relative path: "_stubs/_random.pyi"
    overlay: str = ""  # __init__.pyi overlay line, if needed

    def __post_init__(self) -> None:
        if not self.public:
            raise ValueError("public must not be empty")
        if not self.prefix:
            raise ValueError("prefix must not be empty")


@_dataclass(frozen=True, slots=True)
class StubJob3:
    """Work order for StubFileMachine. No callables, no paths as objects."""

    kind: JobKind
    public: str  # DTO_STACK
    class_name: str  # GreeterEmpty
    package: str  # sstcore.brick.stack
    stub_file: str  # _stubs/_greeter.pyi
    payload: Mapping[str, Any]
    overlay: bool = True


@_dataclass(slots=True, frozen=True)
class StubJobDTO4:
    """Transport contract defining a single stub generation and write task."""

    public_symbol: str  # e.g., 'DTO_STACK'
    class_prefix: str  # e.g., 'Greeter'
    source_target: Any  # Runtime object or Core supplying schema
    target_module: str  # Dotted target e.g., 'sstcore.brick.stack'
    renderer: Callable[[Any, str], str]  # (source, class_name) -> stub_str
    sub_dir: str = "_stubs"
