from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Annotated, Any, Concatenate

from src.sstcore.util.path.guard import PathInput

resolver = Any

_Source = Annotated[Path, resolver]

# AI_FOCUS: this below failed, still the main idea is:
# - parametrize the decorator such that it shows:
#   - inside: source:Path like the annotation _Source above
#   - outside: source:PathInput like it was before or in the stubs
#     (all examples here with Path, that should generalize)
# - one idea is to use like the desired inner signature func(CLEANED)
#   -> then use argcast(EXTENDED) with the desired outer signature
# - worst case is still to write the signatures in a separate stub


def argcast[**P, T: Path, R](
    source: T, **kwargs
) -> Callable[[Callable[Concatenate[Path, P], R]], R]:
    def decorator(
        func: Callable[Concatenate[T, P], R],
    ) -> Callable[Concatenate[Path, P], R]:
        @wraps(func)
        def wrapper(source: Path, *args: P.args, **kwargs: P.kwargs) -> R:
            return func(source, *args, **kwargs)

        return wrapper

    return decorator


@argcast(source=PathInput)
def path_converter(source: _Source) -> int:
    print(source.name)
    return len(source.parts)


path_converter("docs/manual.md")
path_converter(Path("docs/manual.md"))
path_converter(20)
