"""
Assemble default ErrorHandlers for SstErrors (and maybe builtins)

- PathGuardError
- ...
                                                       DependencyLevel[1]
"""

__all__: list[str] = [
    "PATHGUARD"  # NOTE: maybe provide other container
]


from ...port.event._emit import EventEmit
from .._util import PathGuardError
from ._handler import ErrorHandler

# TODO: default registry for SstError implementations
# IDEA: preset registry?


# TODO: and others
def handle_pathguard(error: PathGuardError, emit: EventEmit | None = None): ...


PATHGUARD: ErrorHandler[PathGuardError] = ErrorHandler.from_func(
    func=handle_pathguard, name="PathGuard Error Handler"
)
