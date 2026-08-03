from typing import Any


class ThemeRole: ...


class Theme: ...


class Tests:
    def __init__(self, theme: type[Theme] = Theme, shortcuts: bool = True):
        self.theme = theme
        self._shortcuts_enabled = shortcuts

    def __call__(self, text: Any, color: ThemeRole | BaseColor | str) -> str:
        markup = self.theme.get(color)
        return f"[{markup}]{text}[/]" if markup else str(text)

    def __getattr__(self, name: str):
        """Dynamic color routing via attributes or shortcuts."""

        # 1. Handle disabled shortcuts gracefully (Identity function)
        if name in self._shortcuts and not self._shortcuts_enabled:
            return lambda text: str(text)

        # 2. Resolve the token
        # First, check if it's a known shortcut
        token = self._shortcuts.get(name)

        if not token:
            # If not a shortcut, try to resolve it as a known role or color
            try:
                # Try ThemeRole first, then BaseColor
                try:
                    token = ThemeRole(name.lower())
                except ValueError:
                    token = BaseColor(name.lower())
            except ValueError as error:
                raise AttributeError(
                    f"'{type(self).__name__}' object has no attribute '{name}'"
                ) from error

        # 3. Return the formatter closure
        def formatter(text: Any) -> str:
            return self(text, token)

        return formatter
