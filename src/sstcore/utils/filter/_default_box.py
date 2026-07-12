from .path import PathFilter, ProjectFilter


def make_filter(
    mode: str, extra_include=None, extra_exclude=None
) -> PathFilter:
    if mode == "none":
        return PathFilter()
    if mode == "project":
        f = ProjectFilter()
    elif mode == "latex":
        f = ProjectFilter(
            exclude={"build", "dist", "_build"},
            require_any={".tex", ".cls", ".sty", ".bib"},
        )
    elif mode == "docs":
        f = ProjectFilter(
            exclude={"__pycache__", ".git"},
            require_any={".md", ".rst", ".txt", ".pdf"},
        )
    else:
        raise ValueError(f"Unknown filter_mode={mode}")

    if extra_include:
        f.require_any.update(extra_include)
    if extra_exclude:
        f.exclude.update(extra_exclude)

    return f
