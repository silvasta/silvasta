"""
Assemble default ErrorHandlers for SstErrors (and maybe builtins)

- PathGuardError
- ...
                                                       DependencyLevel[1]
"""

__all__: list[str] = [
    #
    "pathguard_handler"  # NOTE: maybe provide other container
]

# IDEA: from ._registry import ErrorRegistry
# - fill here or in new ._handlers?

from ...port.event import EmitFunc
from .._util import PathGuardError
from ._handler import ErrorHandler

# TASK: default registry with some SstError implementations


def handle_error(error: PathGuardError, emit: EmitFunc | None = None):
    pass


# IDEA: build ErrorHandlerLoader, builds just when Bus arrives
pathguard_handler = ErrorHandler.from_func(handle_error)
