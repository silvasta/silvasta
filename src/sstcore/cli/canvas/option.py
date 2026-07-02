"""
Provide dynamic Option Collection for high-interval visual inspection

- Replace 1 Canvas function with 1 stable default function...
- Provide Registry that swiches function (automatic, random, when needed)
- Mix arguments to create different visual examples
- Clearly show toggle to always and fast go back to execution mode
"""

import random
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum, auto
from functools import update_wrapper
from itertools import product
from typing import Any, overload

from ...utils import printer
from ...utils.color import ColorBox, colorize

c: ColorBox = ColorBox.bold()

type PrintFunc = Callable[[Any], None]


class SelectMode(StrEnum):
    FIXED = auto()
    RANDOM = auto()
    SEQUENTIAL = auto()
    WEIGHTED = auto()
    CYCLE = auto()


@dataclass
class VariantMeta:
    name: str
    enabled: bool = True
    tags: set[str] = field(default_factory=set)


class PrintOptionBase:
    """Provide Printer Canvas execution with optional random dispatches"""

    def __init__(self):
        """Prepare Registry and ensure default print option is ready"""

        self._registry: list[tuple[PrintFunc, VariantMeta]] = []
        self._current: int | None = None
        self.select_mode: SelectMode = SelectMode.FIXED
        self.weights: list[float] | None = None
        self._excluded: set[int] = set()
        self._cycle_index = 0

        self._set_default_function()
        if len(self._registry) != 1:
            raise RuntimeError("Assign exactly 1 default in _set_default!")
        self._set_more_if_desired()

    def __call__(self, *args, use_default_function=True, **kwargs):
        """Provide regular usage or dispatch to random selections"""

        if use_default_function or self.select_mode == SelectMode.FIXED:
            self.set_current(value=0)

        self.print_function(*args, **kwargs)

    def __rich__(self) -> str:
        return colorize.module_path(self, target_color="red")

    def _set_default_function(self):
        """Attach default print option to registry"""
        raise NotImplementedError

    def _set_more_if_desired(self):
        """Assign even more print options or anything else for init"""

    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
    ### Registry Access
    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

    @property
    def print_function(self) -> Callable:
        return self._registry[self.current_id][0]

    @property
    def current_meta(self) -> VariantMeta:
        return self._registry[self.current_id][1]

    @property
    def current_id(self) -> int:
        """Provide Index of current Registry selection"""
        if self._current is None:
            self._current: int = self._select()
        return self._current

    def reset(self):
        """Force new random selection"""
        self._current = None
        self._cycle_index = 0

    def set_current(self, value: int):
        n: int = len(self._registry)
        if 0 <= value < n and value not in self._excluded:
            self._current: int = value
        else:
            self._current = 0
            printer.dip(
                "PrintOption fallback",
                f"Invalid index {value} (n={n})",
                "danger",
            )

    def _valid_index_list(self) -> list[int]:
        return [
            index
            for index in range(len(self._registry))
            if index not in self._excluded
        ]

    def _select(self) -> int:
        """Get new Target Index for Registy Access depending on SelectMode"""

        if not (valid_idx := self._valid_index_list()):
            return 0

        match self.select_mode:
            case SelectMode.RANDOM:
                return random.choice(valid_idx)

            case SelectMode.SEQUENTIAL | SelectMode.CYCLE:
                idx: int = valid_idx[self._cycle_index % len(valid_idx)]
                self._cycle_index = (self._cycle_index + 1) % len(valid_idx)
                return idx

            case SelectMode.WEIGHTED:
                if self.weights:
                    weights: list[float] = [self.weights[i] for i in valid_idx]
                    return random.choices(valid_idx, weights=weights, k=1)[0]

        return 0  # for SelectMode.Fixed or missing weights


class RegisterMixin:
    """Inject external decorator registration into PrintOption"""

    # FIX: Important change:
    # name: self._print_options -> self._registry
    # type: list[PrintOption] -> list[tuple[PrintOption,VariantMeta]]
    # - Just make it work as before

    # TODO: use this new Template but with old overload structure and dispatch logic!
    # class RegisterMixin:
    #     """Decorator-based registration with metadata."""
    #     def register(
    #         self,
    #         target: PrintFunc | None = None,
    #         *,
    #         name: str | None = None,
    #         tags: list[str] | None = None,
    #         enabled: bool = True,
    #         set_current: bool = False,):
    #         def _register(func: PrintFunc):
    #             meta = VariantMeta(
    #                 name=name or func.__name__,
    #                 enabled=enabled,
    #                 tags=set(tags or []),)
    #             self._registry.append((func, meta))  # type: ignore[attr-defined]
    #             if set_current:
    #                 self.set_current(len(self._registry) - 1)  # type: ignore[attr-defined]
    #             return func
    #         if callable(target):
    #             return _register(target)
    #         return _register
    # TODO: end.

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


class FunctionFactoryMixin:
    """Generates combinatorial variants from parameter grids."""

    def register_grid(
        self,
        base_func: Callable,
        param_grid: dict[str, list[Any]],
        filter_func: Callable[[dict], bool] | None = None,
        common_kwargs: dict | None = None,
        tags_prefix: str = "",
    ):
        common_kwargs: dict[str, Any] = common_kwargs or {}

        keys: list[str] = list(param_grid.keys())
        values: list[Any] = list(param_grid.values())

        count = 0  # TODO: check, maybe easier by some len()?

        for combo_values in product(*values):
            # Use original keys with shuffled values... ?
            params: dict[str, Any] = dict(zip(keys, combo_values, strict=True))

            # TODO: what is filter_func?
            if filter_func and not filter_func(params):
                continue

            def make_variant(fixed_params: dict):
                def variant(*args, **call_kwargs):
                    merged: dict[str, Any] = {
                        # why so many kwargs?
                        **common_kwargs,
                        **fixed_params,
                        **call_kwargs,
                    }
                    # TODO: what is base_func?
                    return base_func(*args, **merged)

                # WARN: ty allert -> base_func.__name__
                # TODO: check maybe use one of the created naming templates
                variant_name = f"{base_func.__name__}_{'_'.join(f'{k}={v}' for k, v in fixed_params.items())}"
                # FIX: This should probably be VariantMeta and not internal func: variant...
                variant.variant_name = variant_name  # type: ignore[attr-defined]
                # FIX: yes definitely VariantMeta
                variant.tags = {
                    tags_prefix,
                    *(f"{k}_{v}" for k, v in fixed_params.items()),
                }  # FIX: ok or maybe some kind of closure, unsure if there is no simpler approach
                update_wrapper(variant, base_func)
                return variant

            self.register(  # NOTE: repair RegisterMixin first, use maybe Protocol for typing?
                make_variant(params),
                name="variant_name",  # FIX: definitely, something messed up
                tags=list(params.keys()),
            )  # type: ignore[attr-defined] # NOTE: for example when you get 'fixes' like this
            count += 1

        if count:
            printer.box_mini(
                f"Generated {count} variants from grid", frame="blue"
            )


class RandomSelectMixin:
    """Controlled random/sequential exploration."""

    def set_select_mode(
        self, mode: SelectMode, weights: list[float] | None = None
    ):
        self.select_mode: SelectMode = mode
        # TODO: check if maybe set select_mode without changing weights?
        self.weights: list[float] | None = weights
        self.reset()  # ty:ignore # NOTE:  use maybe Protocol for typing?

    def disable(self, identifier: int | str | PrintFunc):
        """Disable by index, name, or function."""
        for i, (func, meta) in enumerate(self._registry):  # type: ignore[attr-defined]
            if (
                i == identifier
                or (isinstance(identifier, str) and meta.name == identifier)
                or func == identifier
            ):
                self._excluded.add(i)  # ty:ignore # NOTE:  use maybe Protocol for typing?
                break

    def play_multiple(self, n: int = 2):
        # TODO: check what this is doing,
        # idea is to print n different styled but same layouts in a row
        """Queue n non-default variants for sequential playback."""
        valid = [  # TODO: check self._valid_index_list, maybe with some arg for i=1?
            i
            for i in range(1, len(self._registry))  # ty:ignore # NOTE:  use maybe Protocol for typing?
            if i not in self._excluded  # ty:ignore # NOTE:  use maybe Protocol for typing?
        ]  # type: ignore[attr-defined]
        if valid:
            # FIX: what happens with chosen?
            _chosen: list[int] = random.sample(valid, min(n, len(valid)))
            # Force sequential mode for next calls
            self.set_select_mode(SelectMode.SEQUENTIAL)
            self._cycle_index = (
                0  # will start from first chosen via _select logic
            )


class PrintOption(
    FunctionFactoryMixin, RandomSelectMixin, RegisterMixin, PrintOptionBase
):
    """Mix full setup of all PrintOptionMixins"""


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Example Usage (This will be deleted after Debug)
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class MainIntro(PrintOption):
    # NEXT: check how well this applies to .safe_typer
    def _set_default_function(self):
        def default(project_name: str):
            printer.title(
                c.cyan(f"Welcome to {c.white(project_name)}"),
                box=printer.BOX_OPEN,
            )

        self.register(default, name="stable_default")

    def _set_more_if_desired(self):
        # Factory example
        self.register_grid(
            # NEXT: check how well control is with this func stratregy setup
            base_func=self._intro_template,
            param_grid={
                "box": [printer.BOX_OPEN, printer.BOX_MINI, printer.BOX_FULL],
                "frame": ["cyan", "blue", "purple"],
            },
            filter_func=lambda p: (
                not (p["frame"] == "purple" and p["box"] is printer.BOX_MINI)
            ),  # ugly combo
            tags_prefix="intro",
        )

    # NEXT: study different group and attach methods for multiple funcs
    #  (check as well if they are reusable over multiple Canvas Prints)
    def _intro_template(
        self, project_name: str, box=printer.BOX_OPEN, frame="cyan", **_
    ):
        # INFO: parametrized functions to test different styles
        #
        printer.title(  # WARN: same as _set_default_function!!
            # IMPORTANT: reference to default and to here from same template!
            c.cyan(f"Welcome to {c.white(project_name)}"),
            box=box,
            frame=frame,
        )

    # IMPORTANT: Core principles of this module:
    # - Reduce needed templates or layouts to absolute minimum
    # - Avoid any issue that can happen from updating duplicates
    # Highest Goal is to provide Simple usage and API but advanced Features.
    # -> Take the initial pain of increased internal complexity needed for that


if __name__ == "__main__":
    intro = MainIntro()  # exported via __init__.py

# Usage: canvas.safe_typer.intro("flux") or with use_default_function=False

# IMPORTANT: check:  Final Plan — Closing This Topic
# from:  9678_dynamic-print-options_x-g420

# NOTE: stuff like
# #class VisualExperiment:
#     def __init__(self):
#         self.options = [intro, status, ...]
#     def random_tour(self):
#         for opt in self.options:
#             opt.set_selection_mode("random")
#             opt.reset()
#     def disable_ugly(self, tag):
#         for opt in self.options:
#             opt.disable(...)
