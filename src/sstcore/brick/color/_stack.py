"""
Colors in Action

- ColorStack: Attach Colors and Modifier on existing Functions

- (TerminalFormatter) Ansi implementation? Generalize!

"""

__all__: list[str] = [
    "ColorStack",
    "TerminalFormatter",  # NOTE: unsure if this will be completed/refactored
]

from collections.abc import Callable
from typing import Any, Self

from ...port.func import Listening
from ...port.view import Stringable

# WARN: below: mix of different implementations and experiments!!
# WARN: below: mix of different implementations and experiments!!
# WARN: below: mix of different implementations and experiments!!


class ColorStack[**Param, Result]:
    """Stack Colors and Attributes on top of each other and Functions"""

    def __init__(
        self,
        root: Callable[..., Any],
        layers: tuple[str, ...] = (),
    ) -> None:
        self._root = root
        self._layers = layers

        for name, member in TO_DEFINE_COLORS:
            color = self.get_color(member)
            setattr(self, name, CallingColor(color, emit))

        self.forward: Listening = lambda target: target
        # self._emit = emit

    def __getattr__(self, name: str) -> ColorStack:
        # validate against shortcuts / modifiers if you want fail-fast
        return ColorStack(self._root, self._layers + (name,))

    def __init2__(
        self,
        color: Optional[Coloring] = None,
        modifiers: Optional[tuple[str, ...]] = None,
        box_ref: Optional[Any] = None,
    ):
        self._color: Optional[Coloring] = color
        self._modifiers: tuple[str, ...] = modifiers or ()
        self._box_ref: Optional[Any] = box_ref

    def getat2(self, name: str) -> ColorStack:
        # 1. Check if the requested attribute is a modifier
        if name in ANSI_MODIFIERS:
            return ColorStack(
                color=self._color,
                modifiers=self._modifiers + (ANSI_MODIFIERS[name],),
                box_ref=self._box_ref,
            )

        # 2. Check if the attribute is a color shortcut or a named color from Box
        if self._box_ref is not None:
            try:
                resolved_color = self._box_ref.get(name)
                return ColorStack(
                    color=resolved_color,
                    modifiers=self._modifiers,
                    box_ref=self._box_ref,
                )
            except KeyError, AttributeError:
                pass

        raise AttributeError(
            f"'{type(self).__name__}' has no attribute '{name}'"
        )

    def set_routing(self, forward: Listening):
        self.forward: Listening = forward

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        # Strategy A: first string arg gets painted
        # Strategy B: kwargs color= accumulated
        # Start with A for printer.dip style
        if args and self._layers:
            text = args[0]
            for layer in self._layers:
                coloring = self._box.get(layer)
                text = coloring(text)
            args = (text, *args[1:])
        return self._root(*args, **kwargs)

    def __call2__(self, text: Stringable) -> str:
        text_str = str(text)

        # Handle formatting based on the active ColorBox adapter
        if self._box_ref and self._box_ref.active == ColorAdapter.RICH_CLI:
            # Assembly for Rich Markup
            style_tags = []
            if self._color:
                style_tags.append(str(self._color))
            for mod in self._modifiers:
                # Map ANSI codes back to Rich equivalent strings
                rich_mod = {v: k for k, v in ANSI_MODIFIERS.items()}.get(
                    mod, mod
                )
                style_tags.append(rich_mod)

            tag_spec = " ".join(style_tags)
            return f"[{tag_spec}]{text_str}[/]" if tag_spec else text_str

        # Standard ANSI escape engine
        if not self._color and not self._modifiers:
            return text_str

        codes = list(self._modifiers)
        if self._color:
            # Extract numerical sequence from ANSI escape if possible
            color_str = str(self._color)
            if color_str.startswith("\033[") and color_str.endswith("m"):
                clean_code = color_str[2:-1]
                codes.extend(clean_code.split(";"))
            else:
                return self._color(text_str)  # Fallback to base colors

        prefix = f"\033[{';'.join(codes)}m"
        return f"{prefix}{text_str}\033[0m"

    def __repr__(self) -> str:
        return (
            f"ColorStack(color={self._color!r}, modifiers={self._modifiers!r})"
        )


class TerminalFormatter(ColorStack):
    """
    IDEA: MultiStack

    - Stack on top of existing function
    - execute this function in __call__
    - attach color and modifiers by __getattr__ like:
      printer.header.bold.green.underline("My bold green Header")
    """

    COLORS = {  # TODO: replace by new color setup
        "red": "\033[31m",
        "green": "\033[32m",
        "blue": "\033[34m",
    }
    MODIFIERS = {  # TODO: find proper setup
        "bold": "\033[1m",
        "underline": "\033[4m",
    }
    RESET = "\033[0m"

    def __init__(self, current_color="", current_modifiers=""):
        self.current_color: str = current_color
        self.current_modifiers: str = current_modifiers

    def __getattr__(self, name) -> Self:
        if name in self.COLORS:
            return type(self)(
                current_color=self.COLORS[name],
                current_modifiers=self.current_modifiers,
            )
        if name in self.MODIFIERS:
            return type(self)(
                current_color=self.current_color,
                current_modifiers=self.current_modifiers
                + self.MODIFIERS[name],
            )
        raise AttributeError(f"{self} Missing Attribute: '{name}'!")

    def __call__(self, colored_start, regular_text, color_name=None):
        active_color = self.COLORS.get(color_name, self.current_color)
        prefix = f"{self.current_modifiers}{active_color}"
        return f"{prefix}[ {colored_start} ]{self.RESET} {regular_text}"
