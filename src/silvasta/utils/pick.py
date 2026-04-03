from pathlib import Path

from pick import pick

# WARN: name/path/stem confusing, find best configurability
# TODO: logger
# TASK: finally create pick modul
# - check with template and with sachmet


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
    # WARN: throws bad explaining exception for empty folder!
    elements: list = sorted(e.name for e in path.glob(pattern))
    option: str = picker(elements, pattern=pattern, title=title)

    return path / option


def pick_multiple(
    elements: list,
    title: str = "Choose all elements to process:",
    # TODO: forward arguments not completed, look for better solution!
    min_selection_count=1,
    quiet=False,
) -> list[tuple[str, int]]:
    """Show elements, select and get names and index"""

    options_with_index: list[tuple[str, int]] = pick(
        elements,
        title,
        multiselect=True,
        min_selection_count=min_selection_count,
    )

    if not quiet:
        print("You chose:")
        for option, index in options_with_index:
            print(f"{index}: {option}")

    return options_with_index


def pick_multiple_get_name(
    elements: list,
    title: str = "Choose all elements to process:",
    min_selection_count=1,
    quiet=False,
) -> list[str]:
    """Show list elements, pick, return selected names"""

    return [selected[0] for selected in pick_multiple(elements)]


def pick_multiple_get_index(
    elements: list,
    title: str = "Choose all elements to process:",
    min_selection_count=1,
    quiet=False,
) -> list[int]:
    """Show list elements, pick, return selected index"""

    return [selected[1] for selected in pick_multiple(elements)]


def pick_multiple_from_folder(path: Path, pattern: str = "*.*") -> list[Path]:
    """Show elements from folder, select multiple and get path names"""

    if elements := sorted(e.name for e in path.glob(pattern)):
        return [
            path / selected  #
            for selected in pick_multiple_get_name(elements)
        ]
    else:
        print("Nothing to pick")
        return []
