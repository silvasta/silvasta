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


from typing import Protocol as _Protocol

from .govern import Machine
from .shape import Typer


class MetaAnnotator(Typer, _Protocol):
    """Analyze the Meta Construction and Support with Typed Blueprints"""


class ProtoTyper(Typer, _Protocol):
    """Summarize the Builder Pipeline Protocols and Annotate the Mixes"""


class StackAnnotator(Typer, _Protocol):
    """Orchestrate the Combinatorial Stacking Pipeline"""


class StubFileGenerator(Machine):
    """Execute the Mechanical and Rule based part of the pyi writing"""


class LazyTyper(Typer, _Protocol):
    # TASK: identify all location where it makes sense:
    # - sstcore.__init__ already like that
    # - second priority has system
    # - if it works well, just continue on all toplevel packages
    """Render the __init__.pyi to automate the Lazy __getattr__ __init__.py"""
