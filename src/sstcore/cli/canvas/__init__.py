"""
Use printer and color to visualize CLI results

- handle complexity inside and provide easy access
- project objects to canvas
"""

# TASK: final name check, alternative is 'scroll'
# reason:
# the longer I think the more feels canvas like a movie,
# updates of always the same screen,
# more like I will use it later in TUI
# scroll:
# is actually closer to the cli feeling,
# when you print a prompt with 10 files or get like 10 responses,
# it actually starts to behave like an endless scroll,
# still is the scroll the right place to handle prints?
# NEXT: decide name befor next bump!

__all__: list[str] = [
    "safe_typer",
]


from . import safe_typer  #  don't name it engine!
