"""
Provide dynamic Option Collection for high-interval visual inspection

- Replace 1 Canvas function with 1 stable default function...
- Provide Registry that swiches function (automatic, random, when needed)
- Mix arguments to create different visual examples
- Clearly show toggle to always and fast go back to execution mode
"""

from collections.abc import Callable
from typing import Any, overload

from ...utils import printer
from ...utils.color import ColorBox, colorize

c: ColorBox = ColorBox.bold()

type PrintFunc = Callable[[Any], None]


class PrintOptionBase:
    """Provide Printer Canvas execution with optional random dispatches"""

    def __call__(self, *args, use_default_function=True, **kwargs):
        """Provide regular usage or dispatch to random selections"""
        if use_default_function:
            self.set_current(value=0)

        self.print_function(*args, **kwargs)

    def __rich__(self) -> str:
        return colorize.module_path(self, target_color="red")

    def __init__(self):
        """Prepare Registry and ensure default print option is ready"""

        self._print_options: list[PrintFunc] = []
        self._set_default_function()

        if len(self._print_options) != 1:
            raise RuntimeError("Assign exactly 1 default in _set_default!")

        self._current: int | None = None
        self._set_more_if_desired()

    def _set_default_function(self):
        """Attach default print option to registry"""
        raise NotImplementedError

    def _set_more_if_desired(self):
        """Assign even more print options or anything else for init"""

    @property
    def print_function(self) -> Callable:
        return self._print_options[self.current_id]

    @property
    def current_id(self) -> int:
        """Provide Index of current Registry selection"""
        if self._current is None:
            self._current: int = self._select()
        return self._current

    def reset(self):
        """Force new random selection"""
        self._current = None

    def set_current(self, value: int):
        """Ensure safe update of registry index pointer, fail -> default = 0"""
        if 0 <= value < (num_print_options := len(self._print_options)):
            self._current: int = value
        else:
            self._current: int = 0
            text = f"update {value=} but {num_print_options=}..."
            printer.dip("Fail for PrintOption!", text, color="danger")
            printer(self)

    def _select(self) -> int:
        """Apply any form of random arg mixing stuff to get current function"""
        # NEXT:
        # IDEA: random.choices(self.choices, weights=self.weights, k=1)[0]
        # - check grid combinations and automatic func generation
        raise NotImplementedError


class RegisterMixin:
    """Inject external decorator registration into PrintOption"""

    @overload
    def register(self, target: PrintFunc) -> PrintFunc: ...

    @overload
    def register(
        self, *, set_current: bool = False
    ) -> Callable[[PrintFunc], PrintFunc]: ...

    def register(
        self, target: PrintFunc | None = None, *, set_current: bool = False
    ) -> Any:
        """
        Provide Hybrid decorator to append external functions to registry:

        - @po.register
        - @po.register(set_current=True)
        """

        def _add_to_list(func: Callable[[Any], None]):
            self._print_options.append(func)  # ty:ignore
            if set_current:
                self.set_current(value=len(self._print_options) - 1)  # ty:ignore

        # CASE 1: Bare Decorator -> @po.register or simply: po.register(...)
        if callable(target):
            _add_to_list(target)
            return target

        # CASE 2: Decorator with args -> @po.register(set_current=True)
        if target is None:

            def decorator(func: PrintFunc) -> PrintFunc:
                _add_to_list(func)
                return func

            return decorator


# NEXT:
class RandomSelectMixin:
    """Inject random but structured selection into PrintOption"""


# NEXT:
# TODO: check as well for function generation with arg grid, (maybe separate mixin)


class PrintOption(RegisterMixin, RandomSelectMixin, PrintOptionBase):
    """Mix full setup of all PrintOptionMixins"""
