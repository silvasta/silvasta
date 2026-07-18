"""
Visualize results in CLI line by line like a scroll.

- use printer and color
- hide internal complexity
- provide easy access

"""

__all__: list[str] = [
    "safe_typer",
]


from . import safe_typer  #  don't name it engine!
