"""
Visualize results in CLI line by line like a scroll.

- use printer and color
- hide internal complexity
- provide easy access

"""

# LATER: PrintOption: split and refactor before expose

__all__: list[str] = [
    "safe_typer",
]


from . import _safe_typer as safe_typer
