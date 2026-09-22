"""
IMPLEMENT STUB FILE WRITER HERE

- Temporary until ready to move to proper place

"""

# NEXT: implement

from pathlib import Path


def stub_file_local() -> Path:
    return stub_file(file=Path(__file__))


def stub_file(file: Path) -> Path:  # TODO: PathGuard
    stem = f"{Path(file).stem}_stub"
    return Path(f"{file}i").with_stem(stem)
