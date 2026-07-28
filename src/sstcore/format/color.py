"""
Provide Base Level string Colorizing

- Improve visual input for Modules without imports (from utils...)

                                                           ModuleLevel[0]
"""
# INFO: Intended as Package Root

__all__: list[str] = [
    # ...
]


# TASK: refactor colorbox, decouple:
# - ColorPallette: single source of color codes
# - ColorBox: the simple toolkit, maybe (parts) remain in utils
# - colorize: the box like module with advanced tools
# Important:
# - the main color set is (for now) rich compatible but,
#   the base color set will be designed independent of any framework
# - useable in cli and tui, ok rich could be enough, and as well other ui layer
# INFO: same for format (same purpose, different tools)
