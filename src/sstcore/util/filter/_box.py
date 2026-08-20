"""
Prepare default sets for Filters

- Attach dispatch to port.filter.FilterArgs
                                                       DependencyLevel[1]
"""

__all__: list[str] = [
    "FilterArgs",
]

from ...port.filter import FilterArgs
from ._base import FilterData

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
### Shadow Patch
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


def attach_str_to_filter_args(self) -> str:
    return self.name.capitalize()


setattr(FilterArgs, "__str__", attach_str_to_filter_args)  # noqa: B010


def attach_call_to_filter_args(self: FilterArgs) -> FilterData:
    """Create a configured filter. Overrides are applied after defaults."""
    match self:
        case FilterArgs.PROJECT:
            return FilterData(
                exclude=DIR_PYTHON | DIR_CODE | DIR_RUST,
                require_any=FILE_PYTHON | FILE_RUST,
            )

        case FilterArgs.PYTHON:
            return FilterData(
                exclude=DIR_PYTHON | DIR_CODE,
                require_any=FILE_PYTHON,
            )
        case FilterArgs.RUST:
            return FilterData(
                exclude=DIR_CODE | DIR_RUST,
                require_any=FILE_RUST,
            )
        case FilterArgs.LATEX:
            return FilterData(
                exclude=DIR_LATEX | DIR_CODE,
                require_any=FILE_LATEX,
            )
        case FilterArgs.CONFIG:
            return FilterData(
                exclude=DIR_CODE | DIR_PYTHON,
                require_any=FILE_CONFIG,
            )
        case FilterArgs.DOCS:
            return FilterData(
                exclude=DIR_CODE,
                require_any=FILE_DOCS,
            )
        case FilterArgs.NONE:
            return FilterData()

        case FilterArgs.ALL:
            return FilterData(
                exclude=DIR_CODE | DIR_PYTHON | DIR_LATEX | DIR_RUST,
                require_any=FILE_PYTHON
                | FILE_RUST
                | FILE_LATEX
                | FILE_DOCS
                | FILE_CONFIG,
            )


setattr(FilterArgs, "__call__", attach_call_to_filter_args)  # noqa: B010
