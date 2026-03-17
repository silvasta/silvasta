from pathlib import Path

from pick import pick

# WARN: name/path/stem confusing, find best configurability


def picker(
    elements: list[str], pattern: str = "*", title: str | None = None
) -> str:
    """Show elements from list, select 1 and get name back"""

    if title is None:
        title = "Choose an element:"

    option, _ = pick(elements, title)
    print(f"You chose {option}")

    return option


def pick_from_folder(
    path: Path, pattern: str = "*", title: str | None = None
) -> Path:
    """Show elements from folder, select 1 and get path name"""

    # TODO: merge with multiple, 1 func for path-to-folder
    elements: list = sorted(e.name for e in path.glob(pattern))
    option: str = picker(elements)

    return path / option


def pick_multiple(
    elements: list,
    title: str = "Choose all elements to process:",
    min_selection_count=1,
) -> list[tuple[str, int]]:
    """Show elements, select and get names and index"""
    options_with_index: list[tuple[str, int]] = pick(
        elements,
        title,
        multiselect=True,
        min_selection_count=min_selection_count,
    )
    print(options_with_index)  # TODO: clean prints!
    print("You chose:")
    for option in options_with_index:
        print(f"{option}")
    return options_with_index


def pick_multiple_get_name(elements: list) -> list[str]:
    """Show list elements, pick, return selected names"""

    return [selected[0] for selected in pick_multiple(elements)]


def pick_multiple_get_index(elements: list) -> list[int]:
    """Show list elements, pick, return selected index"""

    return [selected[1] for selected in pick_multiple(elements)]


# TASK: finally create pick modul
# - check with template and with sachmet
#
def pick_multiple_from_folder(path: Path, pattern: str = "*.*") -> list[Path]:
    """Show elements from folder, select multiple and get path names"""

    elements: list[str] = sorted(e.name for e in path.glob(pattern))
    selected: list[str] = pick_multiple_get_name(elements)

    return [path / select for select in selected]
