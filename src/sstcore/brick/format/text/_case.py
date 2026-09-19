"""
Transform String to Cases

- string_to_cases
- StringToCases
- stringToCases
- string-to-cases
                                                       DependencyLevel[0]
"""

# LATER: not only transform but as well split!
# IDEA: use eg PathGuard -> Path is blue, Guard is green
# - even better for Error in red or branding eg projects,
# SachmisDataError visualizes project, domain, and danger
# (check first in cli how it renders before too much effort)

__all__: list[str] = [
    "to_snake",
    "to_camel",
    "to_pascal",
    "to_kebab",
]

import re as _re


def to_snake(text: str) -> str:
    # LATER: extract pattern like:
    # SNAKE = r"XXX"
    # or whatever they are, and expose in module body
    s: str = _re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", text)
    return _re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s).lower().replace("-", "_")


def to_camel(text: str) -> str:
    components = to_snake(text).split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def to_pascal(text: str) -> str:
    return "".join(x.title() for x in to_snake(text).split("_"))


def to_kebab(text: str) -> str:
    return to_snake(text).replace("_", "-")
