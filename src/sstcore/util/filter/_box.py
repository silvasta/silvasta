"""
Provide prepared Filter

                                                       DependencyLevel[1]
"""

__all__: list[str] = [
    "FilterBox",
]

from enum import EnumMeta, IntEnum, auto

from ...port.filter import FilterBoxForInject, FilterBoxForMeta
from ._arg import FilterData

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
    def args(self) -> FilterData:
        """Create a configured filter. Overrides are applied after defaults."""
        match self:
            case FilterBox.PROJECT:
                return FilterData(
                    exclude=DIR_PYTHON | DIR_CODE | DIR_RUST,
                    require_any=FILE_PYTHON | FILE_RUST,
                )

            case FilterBox.PYTHON:
                return FilterData(
                    exclude=DIR_PYTHON | DIR_CODE,
                    require_any=FILE_PYTHON,
                )
            case FilterBox.RUST:
                return FilterData(
                    exclude=DIR_CODE | DIR_RUST,
                    require_any=FILE_RUST,
                )
            case FilterBox.LATEX:
                return FilterData(
                    exclude=DIR_LATEX | DIR_CODE,
                    require_any=FILE_LATEX,
                )
            case FilterBox.CONFIG:
                return FilterData(
                    exclude=DIR_CODE | DIR_PYTHON,
                    require_any=FILE_CONFIG,
                )
            case FilterBox.DOCS:
                return FilterData(
                    exclude=DIR_CODE,
                    require_any=FILE_DOCS,
                )
            case FilterBox.NONE:
                return FilterData()

            case FilterBox.ALL:
                return FilterData(
                    exclude=DIR_CODE | DIR_PYTHON | DIR_LATEX | DIR_RUST,
                    require_any=FILE_PYTHON
                    | FILE_RUST
                    | FILE_LATEX
                    | FILE_DOCS
                    | FILE_CONFIG,
                )


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### EXPERIMENTS
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Monkey Patch
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


def filter_args(self: FilterBoxForInject) -> FilterData:
    """Create a configured filter. Overrides are applied after defaults."""
    match self:
        case FilterBox.PROJECT:
            return FilterData(
                exclude=DIR_PYTHON | DIR_CODE | DIR_RUST,
                require_any=FILE_PYTHON | FILE_RUST,
            )

        case FilterBox.PYTHON:
            return FilterData(
                exclude=DIR_PYTHON | DIR_CODE,
                require_any=FILE_PYTHON,
            )
        case FilterBox.RUST:
            return FilterData(
                exclude=DIR_CODE | DIR_RUST,
                require_any=FILE_RUST,
            )
        case FilterBox.LATEX:
            return FilterData(
                exclude=DIR_LATEX | DIR_CODE,
                require_any=FILE_LATEX,
            )
        case FilterBox.CONFIG:
            return FilterData(
                exclude=DIR_CODE | DIR_PYTHON,
                require_any=FILE_CONFIG,
            )
        case FilterBox.DOCS:
            return FilterData(
                exclude=DIR_CODE,
                require_any=FILE_DOCS,
            )
        case FilterBox.NONE:
            return FilterData()

        case FilterBox.ALL:
            return FilterData(
                exclude=DIR_CODE | DIR_PYTHON | DIR_LATEX | DIR_RUST,
                require_any=FILE_PYTHON
                | FILE_RUST
                | FILE_LATEX
                | FILE_DOCS
                | FILE_CONFIG,
            )


FilterBoxForInject.args = property(filter_args)

FilterBoxInject = FilterBoxForInject

x = FilterBoxInject.CONFIG.args
x = FilterBox.CONFIG.args

### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Meta Hack
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class _FilterBoxMeta(EnumMeta):
    def __new__(mcs, name, bases, ns):
        if FilterBoxForMeta._member_map_:
            # Copy member map -> new class gets identical members
            for member_name, member in FilterBoxForMeta._member_map_.items():
                ns[member_name] = member.value

        def __str__(self):
            return self.name.capitalize()

        def args(self) -> FilterData:
            match self:
                case mcs.PROJECT:
                    return FilterData(
                        exclude=DIR_PYTHON | DIR_CODE | DIR_RUST,
                        require_any=FILE_PYTHON | FILE_RUST,
                    )

                case mcs.PYTHON:
                    return FilterData(
                        exclude=DIR_PYTHON | DIR_CODE,
                        require_any=FILE_PYTHON,
                    )
                case mcs.RUST:
                    return FilterData(
                        exclude=DIR_CODE | DIR_RUST,
                        require_any=FILE_RUST,
                    )
                case mcs.LATEX:
                    return FilterData(
                        exclude=DIR_LATEX | DIR_CODE,
                        require_any=FILE_LATEX,
                    )
                case mcs.CONFIG:
                    return FilterData(
                        exclude=DIR_CODE | DIR_PYTHON,
                        require_any=FILE_CONFIG,
                    )
                case mcs.DOCS:
                    return FilterData(
                        exclude=DIR_CODE,
                        require_any=FILE_DOCS,
                    )
                case mcs.NONE:
                    return FilterData()

                case mcs.ALL:
                    return FilterData(
                        exclude=DIR_CODE | DIR_PYTHON | DIR_LATEX | DIR_RUST,
                        require_any=FILE_PYTHON
                        | FILE_RUST
                        | FILE_LATEX
                        | FILE_DOCS
                        | FILE_CONFIG,
                    )
                # ... all cases
                case _:
                    raise ValueError(...)

        ns["__str__"] = __str__
        ns["args"] = property(args)

        cls = super().__new__(mcs, name, (IntEnum,), ns)
        return cls


class FilterBoxWithMeta(metaclass=_FilterBoxMeta):
    """Rich filter box that re-uses the central member definitions."""


x = FilterBoxWithMeta.CONFIG.args
