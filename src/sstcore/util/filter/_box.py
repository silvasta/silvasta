"""
Prepare Box with different predefinded Filters (for Projects)

- FilterSet as Base for different purposes
                                                       DependencyLevel[1]
"""

__all__: list[str] = [
    "FilterBox",
]

from enum import IntEnum, auto

from ._set import FilterArgs

# LATER: dispatch text-binary file eg: {".pdf"}


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### For Folder exclude
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

DIR_CODE: set[str] = {"env", ".git"}
DIR_PYTHON: set[str] = {"__pycache__", ".venv", "venv"}
DIR_RUST: set[str] = {"target"}
DIR_LATEX: set[str] = {"build", "dist", "_build", "out"}


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### For File include
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

FILE_PYTHON: set[str] = {".py", ".pyi", ".toml"}
FILE_RUST: set[str] = {".rs", ".toml"}
FILE_LATEX: set[str] = {".tex", ".cls", ".sty", ".bib"}
FILE_DOCS: set[str] = {".md", ".rst", ".txt"}
FILE_CONFIG: set[str] = {".json", ".yaml", ".toml", ".lua"}


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### BOX
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class FilterBox(IntEnum):
    """Predefined, selectable filter configurations."""

    PROJECT = auto()
    PYTHON = auto()
    RUST = auto()
    LATEX = auto()
    CONFIG = auto()
    DOCS = auto()
    NONE = auto()
    ALL = auto()

    def __str__(self):
        return self.name.capitalize()

    @property
    def args(self) -> FilterArgs:
        """Create a configured filter. Overrides are applied after defaults."""
        match self:
            case FilterBox.PROJECT:
                return FilterArgs(
                    exclude=DIR_PYTHON | DIR_CODE | DIR_RUST,
                    require_any=FILE_PYTHON | FILE_RUST,
                )

            case FilterBox.PYTHON:
                return FilterArgs(
                    exclude=DIR_PYTHON | DIR_CODE,
                    require_any=FILE_PYTHON,
                )
            case FilterBox.RUST:
                return FilterArgs(
                    exclude=DIR_CODE | DIR_RUST,
                    require_any=FILE_RUST,
                )
            case FilterBox.LATEX:
                return FilterArgs(
                    exclude=DIR_LATEX | DIR_CODE,
                    require_any=FILE_LATEX,
                )
            case FilterBox.CONFIG:
                return FilterArgs(
                    exclude=DIR_CODE | DIR_PYTHON,
                    require_any=FILE_CONFIG,
                )
            case FilterBox.DOCS:
                return FilterArgs(
                    exclude=DIR_CODE,
                    require_any=FILE_DOCS,
                )
            case FilterBox.NONE:
                return FilterArgs()

            case FilterBox.ALL:
                return FilterArgs(
                    exclude=DIR_CODE | DIR_PYTHON | DIR_LATEX | DIR_RUST,
                    require_any=FILE_PYTHON
                    | FILE_RUST
                    | FILE_LATEX
                    | FILE_DOCS
                    | FILE_CONFIG,
                )
