"""
Prepare default sets for Filters

- Attach dispatch to port.filter.FilterArgs

                             DependencyLevel.sstcore.util.filter[1]
"""

# TASK: dispatch text-binary file eg: {".pdf"}

__all__: list[str] = [
    "FilterArgs",
]

from ...port.filter import FilterArgs
from ._base import FilterData

_Folder_Exclude = "default undesired"

DIR_CODE: frozenset[str] = frozenset({"env", ".git"})
DIR_PYTHON: frozenset[str] = frozenset({"__pycache__", ".venv", "venv"})
DIR_RUST: frozenset[str] = frozenset({"target"})
DIR_LATEX: frozenset[str] = frozenset({"build", "dist", "_build", "out"})


_File_Include = "default targets"

FILE_PYTHON: frozenset[str] = frozenset({".py", ".pyi", ".toml"})
FILE_RUST: frozenset[str] = frozenset({".rs", ".toml"})
FILE_LATEX: frozenset[str] = frozenset({".tex", ".cls", ".sty", ".bib"})
FILE_DOCS: frozenset[str] = frozenset({".md", ".rst", ".txt"})
FILE_CONFIG: frozenset[str] = frozenset({".json", ".yaml", ".toml", ".lua"})

# LATER: where to apply? or just use -i"___" in cli?
IDEA: frozenset[str] = frozenset({"___"})
EXPERIMENT: frozenset[str] = frozenset({"____"})

### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Shadow Patch
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


def attach_str_to_filter_args(self) -> str:
    return self.name.capitalize()


setattr(FilterArgs, "__str__", attach_str_to_filter_args)  # noqa: B010


def _resolve_preset(enum: FilterArgs) -> FilterData[str]:
    """Create a configured filter. Overrides are applied after defaults."""
    match enum:
        case FilterArgs.PROJECT:
            return FilterData.defrost(
                exclude=DIR_PYTHON | DIR_CODE | DIR_RUST,
                require_any=FILE_PYTHON | FILE_RUST,
            )

        case FilterArgs.PYTHON:
            return FilterData.defrost(
                exclude=DIR_PYTHON | DIR_CODE,
                require_any=FILE_PYTHON,
            )
        case FilterArgs.RUST:
            return FilterData.defrost(
                exclude=DIR_CODE | DIR_RUST,
                require_any=FILE_RUST,
            )
        case FilterArgs.LATEX:
            return FilterData.defrost(
                exclude=DIR_LATEX | DIR_CODE,
                require_any=FILE_LATEX,
            )
        case FilterArgs.CONFIG:
            return FilterData.defrost(
                exclude=DIR_CODE | DIR_PYTHON,
                require_any=FILE_CONFIG,
            )
        case FilterArgs.DOCS:
            return FilterData.defrost(
                exclude=DIR_CODE,
                require_any=FILE_DOCS,
            )
        case FilterArgs.NONE:
            return FilterData()

        case FilterArgs.ALL:
            return FilterData.defrost(
                exclude=DIR_CODE | DIR_PYTHON | DIR_LATEX | DIR_RUST,
                require_any=FILE_PYTHON
                | FILE_RUST
                | FILE_LATEX
                | FILE_DOCS
                | FILE_CONFIG,
            )


def create_filter_args(
    self: FilterArgs,
    *,
    include: list[str] | set[str] | None = None,
    exclude: list[str] | set[str] | None = None,
    require_all: list[str] | set[str] | None = None,
    unexclude: list[str] | set[str] | None = None,
    allow_hidden: bool = False,
    invert: bool = False,
) -> FilterData[str]:
    """Create a configured filter. Overrides are applied after defaults."""
    data: FilterData[str] = _resolve_preset(self)

    if include:
        data.require_any.update(include)
    if exclude:
        data.exclude.update(exclude)
    if require_all:
        data.require_all.update(require_all)
    if unexclude:
        data.exclude.difference_update(unexclude)
    if allow_hidden:
        data.allow_hidden_files = True
    if invert:
        data.return_opposite = True

    return data


setattr(FilterArgs, "__call__", create_filter_args)  # noqa: B010

if __name__ == "__main__":
    print(FilterArgs)
    for f in FilterArgs:
        print(f, f.value, f())
