"""
TODO: Validate PathGuard args before even funcion entry

-
"""

import inspect
from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Annotated, get_args, get_origin

from sstcore.error import PathGuardError

from ._input import PathInput, PathSpec
from ._operate import SyncMode


@dataclass(frozen=True, slots=True)
class PathRules:
    """Stores the validation rules to apply to a PathInput."""

    resolve: bool = False
    must_exists: bool = False
    # parent_exists: bool = False ...


# Create clean aliases for your function signatures
_SourcePath = Annotated[PathInput, PathRules(must_exists=True, resolve=True)]
_TargetPath = Annotated[PathInput, PathRules()]


def validate_paths(func):
    """Typer-style dependency injection for PathGuard."""
    sig = inspect.signature(func)

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Bind the provided arguments to the function signature
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()

        for name, value in bound.arguments.items():
            annotation = sig.parameters[name].annotation

            # Check if the argument is wrapped in Annotated
            if get_origin(annotation) is Annotated:
                metadata = get_args(annotation)

                # Find the PathRules in the metadata
                for meta in metadata:
                    if isinstance(meta, PathRules):
                        # AUTOMATIC VALIDATION HAPPENS HERE
                        # (Assuming PathSpec.ok() is updated to accept the rules dict/kwargs)
                        validated_path = PathSpec.ok(
                            target=value,
                            resolve=meta.resolve,
                            must_exists=meta.must_exists,
                        )
                        # Overwrite the raw input with the validated Path
                        bound.arguments[name] = validated_path
                        break

        # Call the original function with the sanitized arguments
        return func(*bound.args, **bound.kwargs)

    return wrapper


class _PathGuard:
    @staticmethod
    @validate_paths
    def rotate(
        _source: _SourcePath,  # Automatically requires must_exists=True
        _target: _TargetPath,  # Automatically validated and cast to Path
        sync_mode: str | SyncMode = SyncMode.INCREMENT,
        _reset: bool = False,
    ) -> Path:
        """Move Source to Target and if reset: Create empty File or Dir"""

        # Look how clean this is!
        # `source` and `target` are already guaranteed to be valid Path objects.

        try:
            sync_mode = SyncMode(sync_mode)
        except ValueError as e:
            raise PathGuardError(f"Invalid SyncMode: {sync_mode}") from e

        return Path()
        # ... logic continues safely ...
