"""
Write and Expose the Shape of the Dynamically created Classes

- Analyze Mixins and Combinatorials and Draw the Result
- Provide the Type Checker with best Information (UX++)

                                    DependencyLevel.sstcore.port[1]
"""

from pathlib import Path

__all__: list[str] = [
    "StubFileGenerator",
    "StackAnnotator",
    "ProtoTyper",
]


from dataclasses import dataclass as _dataclass
from typing import ClassVar
from typing import Protocol as _Protocol

from .attach import ConfigDescriptor
from .govern import Machine
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


class StubFileGenerator(Machine):
    """Execute the Mechanical and Rule based part of the pyi writing"""

    def report(self):  # TODO: think about invisible logging
        """Precisely record any single step into a structured table"""


#  LINE: -- DTO -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@_dataclass(frozen=True)
class _StubJob:
    public: str
    prefix: str
    package: str | None = None


class _JobDTO:
    _registry: ClassVar[dict[str, type[_JobDTO]]] = {}

    public: ConfigDescriptor[str]  # read/write с валидацией
    prefix: ConfigDescriptor[str]
    package: ConfigDescriptor[str | None]
    content: ConfigDescriptor[str]  # готовый stub-текст
    target: ConfigDescriptor[Path]


@_dataclass(frozen=True, slots=True)
class _StubJob:
    public: str  # binding name in __init__.py, e.g. "DTO_STACK"
    prefix: str  # e.g. "Greeter", "Printer"
    package: str | None = None  # override; else inferred at write time
    content: str = ""  # rendered stub text (filled by Typer)
    target_file: str = ""  # relative path: "_stubs/_random.pyi"

    def __post_init__(self) -> None:
        if not self.public:
            raise ValueError("public must not be empty")
        if not self.prefix:
            raise ValueError("prefix must not be empty")


@_dataclass(frozen=True, slots=True)
class StubJob:
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
