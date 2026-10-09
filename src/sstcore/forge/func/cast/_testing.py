from pathlib import Path
from typing import Annotated

from src.sstcore.util.path.guard import PathInput
from sstcore.port.color import Color, ColorIdentifier

from ._engine import cast_args
from ._rules import PathRules, Resolver

# The static type checker sees 'ColorIdentifier' or 'PathInput'.
# The runtime engine sees 'Resolver' or 'PathRules'.
CastColor = Annotated[ColorIdentifier, Resolver(Color.resolve)]
Source = Annotated[PathInput, PathRules(must_exists=True, resolve=True)]
SourcePath = Annotated[Path, PathRules(must_exists=True, resolve=True)]
TargetPath = Annotated[Path, PathRules(ensure_parent=True)]

# AI: here below all typing for the signatures is broken:
# - outside: no autocomplete, no warnings on bad assigns
# - inside: shows the extended type, warnings on the "clean" path


@cast_args
def apply_theme(
    primary: CastColor, secondary: CastColor = Color.BLACK
) -> None:
    # Guaranteed to be Color objects here!
    print(f"Primary: {primary.name}, Secondary: {secondary.name}")


# FAIL:
apply_theme(primary="blue", fail=1)


@cast_args
def copy_file(source: Source, target: TargetPath) -> None:
    # Guaranteed to be resolved, existing/validated Path objects here!
    print(f"Copying {source.name} to {target.name}")


apply_theme("blue", 1)  # Works flawlessly
# Validates, casts to Path, throws PathGuardError if missing
copy_file("./src.txt", "./dest.txt")


@cast_args
def rotate(source: SourcePath, target: TargetPath, reset: bool = False):
    # `source` is guaranteed to be a resolved Path that exists.
    # `target` is guaranteed to be a Path.
    print(f"Moving {source.name} to {target.name}")


rotate(Path("docs/test.txt"), not_target="docs/new.txt")
