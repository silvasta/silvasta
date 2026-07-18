"""
Provide Dynamic Option Collection for high-interval visual inspection

- Replace 1 Scroll function with at least 1 stable default function...
- Provide Registry that switches function (automatic, random, when needed)
- Mix arguments to create different visual examples

- Ensure Toggle to move easy and fast back to regular execution mode
"""

__all__: list[str] = [
    "PrintFunc",
    "SelectMode",
    "VariantMeta",
    "PrintOption",
]

import random
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum, auto
from functools import update_wrapper
from itertools import product
from typing import Any, Protocol, cast

from ...utils import printer
from ...utils.color import ColorBox, colorize

c: ColorBox = ColorBox.bold()

type PrintFunc = Callable[..., None]


class SelectMode(StrEnum):
    # LATER: this as govern
    # - attach here small dataclass with needed SelectState
    # - create method to switch in between states,
    #   including special args (eg weights cycle id)
    # - finally provide current index, based on input and state
    # Ensure something like a (global?) toggle?
    FIXED = auto()
    RANDOM = auto()
    SEQUENTIAL = auto()
    WEIGHTED = auto()
    CYCLE = auto()


@dataclass
class VariantMeta[FuncT: PrintFunc]:
    # LATER: attach function directly here?
    # -> reduce _registry to list of FuncVariation ar similar?
    # now: self._registry: list[tuple[PrintFunc, VariantMeta]] = []
    # after: self._registry: list[FunctionVariation] = []
    name: str
    enabled: bool = True
    tags: set[str] = field(default_factory=set)


class PrintOptionBase[FuncT: PrintFunc]:
    """Build Printer Scroll with optional random dispatches"""

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        """Provide regular usage or dispatch to random selections"""

        if self.select_mode == SelectMode.FIXED:
            self.set_current(value=0)

        self.print_function(*args, **kwargs)

    def __init__(self, *, select_mode=SelectMode.FIXED):
        """Prepare Registry and ensure default print option is ready"""

        self.select_mode: SelectMode = select_mode

        # used by selection modes # LATER: move to Enum (attached dataclass)?
        self._cycle_index = 0
        self.weights: list[float] | None = None

        # registry setup, access and exclude
        self._registry: list[tuple[FuncT, VariantMeta[FuncT]]] = []
        self._current: int | None = None
        self._excluded: set[int] = set()

        self.register(self._load_default_function())

        if select_mode != SelectMode.FIXED:  # LATER: _hook even for fixed?
            self._set_more_if_desired()

    def _load_default_function(self) -> FuncT:
        """Provide default print function option for Registry[0]"""
        raise NotImplementedError

    def _set_more_if_desired(self):
        """Assign even more print options or anything else for init"""

    def __str__(self) -> str:
        return type(self).__name__

    def __rich__(self) -> str:
        return colorize.modules(self, target_color="cyan")

    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
    ### Registry Access
    ### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --

    @property
    def print_function(self) -> FuncT:
        return self._registry[self.current_id][0]

    @property
    def current_meta(self) -> VariantMeta[FuncT]:
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

    def _valid_index_list(self, with_zero=True) -> list[int]:
        start: int = 0 if with_zero else 1
        return [
            index
            for index in range(start, len(self._registry))
            if index not in self._excluded
        ]

    def show(self):
        printer.lines_with_len(
            name=str(self),
            lines=[self._registry[i][1] for i in self._valid_index_list()],
        )

    def register(
        self,
        target: FuncT,
        *,
        name: str | None = None,
        tags: list[str] | None = None,
        enabled: bool = True,
        set_active: bool = False,
    ) -> FuncT:

        meta: VariantMeta[FuncT] = VariantMeta[FuncT](
            name=name or getattr(target, "__name__", "function"),
            enabled=enabled,
            tags=set(tags or []),
        )
        self._registry.append((target, meta))

        if set_active:
            self.set_current(len(self._registry) - 1)

        return target

    def _select(self) -> int:
        """Get new Target Index for Registry Access depending on SelectMode"""

        if not (valid_idx := self._valid_index_list()):
            return 0

        match self.select_mode:  # LATER: move check to SelectMode?
            case SelectMode.RANDOM:
                return random.choice(valid_idx)

            case SelectMode.SEQUENTIAL | SelectMode.CYCLE:
                # LATER: what is difference, sequential|cycle?
                idx: int = valid_idx[self._cycle_index % len(valid_idx)]
                self._cycle_index = (self._cycle_index + 1) % len(valid_idx)
                return idx

            case SelectMode.WEIGHTED:
                if self.weights:
                    weights: list[float] = [self.weights[i] for i in valid_idx]
                    return random.choices(valid_idx, weights=weights, k=1)[0]
                # LATER: maybe some warn if missing weights

        return 0  # for SelectMode.Fixed or missing weights


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### The Unified Protocol
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class PrintOptionProtocol[FuncT: PrintFunc](Protocol):
    """Provide type checker with information across all Mixins and Base"""

    _registry: list[tuple[FuncT, VariantMeta[FuncT]]]
    _excluded: set[int]
    _cycle_index: int
    select_mode: SelectMode
    weights: list[float] | None

    def set_current(self, value: int) -> None: ...
    def reset(self) -> None: ...

    def register(
        self,
        target: FuncT,
        *,
        name: str | None = None,
        tags: list[str] | None = None,
        enabled: bool = True,
        set_active: bool = False,
    ) -> Any: ...

    def set_mode(
        self,
        mode: SelectMode | None = None,
        weights: list[float] | None = None,
    ) -> None: ...
    def _valid_index_list(self, with_zero: bool) -> list[int]: ...


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Mixins
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class FunctionFactoryMixin[FuncT: PrintFunc]:
    """Generate combinatorial variants from parameter grid"""

    def grid[ParamT: Callable[..., None]](
        self: PrintOptionProtocol[FuncT],
        template: ParamT,  # LATER: check if and how to enforce this
        param_grid: dict[str, list[Any]],
        filter_func: Callable[[dict], bool] | None = None,
        common_kwargs: dict[str, Any] | None = None,
        tags_prefix: str = "",
    ) -> None:
        """Assemble Parameter dynamically to PrintFunc and Register"""

        common_kwargs: dict[str, Any] = common_kwargs or {}
        keys: list[str] = list(param_grid.keys())
        values: list[list[Any]] = list(param_grid.values())
        count = 0

        base_name: str = getattr(template, "__name__", "variant")

        for combo_values in product(*values):
            params: dict[str, Any] = dict(zip(keys, combo_values, strict=True))

            if filter_func and not filter_func(params):
                continue

            # Extracted closure factory to avoid late-binding issues in loops
            def make_variant(fixed_params: dict[str, Any]) -> FuncT:
                # LATER: why not partial?
                def variant(*args: Any, **call_kwargs: Any) -> None:
                    merged: dict[str, Any] = {
                        **common_kwargs,
                        **fixed_params,
                        **call_kwargs,
                    }
                    return template(*args, **merged)

                update_wrapper(variant, template)
                return cast(FuncT, variant)

            # Generate Clean Metadata
            param_names: str = "_".join(f"{k}={v}" for k, v in params.items())
            # LATER: better name, unreadable, terrible for e.g. boxes
            variant_name = f"{base_name}_{param_names}"

            tags: set[str] = {tags_prefix} if tags_prefix else set()
            tags.update(f"{k}_{v}" for k, v in params.items())

            # Register by VariantMeta approach
            self.register(
                target=make_variant(params),
                name=variant_name,
                tags=list(tags),
            )
            count += 1

        if count:
            printer(f"{count} PrintOptions from Grid", end=" ")
            printer(self)


class RandomSelectMixin[FuncT: PrintFunc]:
    """Control random or sequential exploration of variants"""

    def set_mode(
        self: PrintOptionProtocol[FuncT],
        mode: SelectMode | None = None,
        weights: list[float] | None = None,
    ):
        """Change SelectMode or weights"""
        if mode is not None:
            self.select_mode: SelectMode = mode
        if weights is not None:
            self.weights: list[float] | None = weights
        self.reset()

    def disable(self: PrintOptionProtocol, identifier: int | str | PrintFunc):
        """Disable by index, name, or function"""
        for i, (func, meta) in enumerate(self._registry):
            if (
                i == identifier
                or (isinstance(identifier, str) and meta.name == identifier)
                or func == identifier
            ):
                self._excluded.add(i)
                break

    def play_multiple(self: PrintOptionProtocol):
        """Queue non-default variants for sequential playback"""

        # NOTE: unsure if and for what this makes sense at all...
        # Instead of dynamically creating a sub-queue (which requires altering the
        # Base _select logic), we pick a random valid starting point and force
        # the sequencer mode so the next `n` executions will flow naturally in a row.

        if not (all_targets := self._valid_index_list(with_zero=False)):
            return

        start_index: int = random.choice(all_targets)

        self.set_mode(SelectMode.SEQUENTIAL)

        # Point cycle index at chosen start location within the valid list
        self._cycle_index: int = all_targets.index(start_index)


class PrintOption[FuncT: PrintFunc](
    FunctionFactoryMixin[FuncT],
    RandomSelectMixin[FuncT],
    PrintOptionBase[FuncT],
):
    """Mix full setup of all PrintOptionMixins"""
