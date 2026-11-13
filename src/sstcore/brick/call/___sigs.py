"""
Analyze and Compare Callable Signatures against Liskov Substitution Rules

.
"""

from __future__ import annotations

__all__: list[str] = [
    "EMPTY",
    "LspViolation",
    "SigPart",
    "SigArg",
    "SigParam",
    "PosArgs",
    "AnyArgs",
    "Args",
    "KeyArgs",
    "Kwargs",
    "SigSpec",
]

from collections.abc import Callable, Iterator
from dataclasses import dataclass
from enum import IntFlag, auto
from inspect import (
    Parameter,
    _empty,
    _ParameterKind,
    isasyncgenfunction,
    iscoroutinefunction,
    isgeneratorfunction,
    signature,
    unwrap,
)
from types import UnionType
from typing import (
    Any,
    Literal,
    NamedTuple,
    Self,
    Union,
    get_args,
    get_origin,
    get_type_hints,
    overload,
)

from ...port.solid import EnumZero

EMPTY: type[_empty] = _empty
BindingKind = Literal["function", "method", "classmethod", "staticmethod"]


#  LINE: -- LSP Violation Classification -- -- - -- -- - -- -- - -- --


class _LspViolationBase(IntFlag):
    @property
    def bits(self) -> str:
        """Provide the Bit Representation (with Zeros and Ones)."""
        return f"{self:0{len(type(self))}b}"

    def _describe(self) -> tuple[str, str]:
        """Return (title, detail) for a single flag or named preset."""
        return (self.name or str(self.value), "")

    @property
    def title(self) -> str:
        """Short one-line summary of the violation(s)."""
        if self.value == 0 or self.name is not None:
            return self._describe()[0]
        return " | ".join(member.title for member in self)

    @property
    def detail(self) -> str:
        """Extended explanation of runtime and static typing impact."""
        if self.value == 0 or self.name is not None:
            return self._describe()[1]
        return "\n".join(f"- {member.name}: {member.detail}" for member in self)

    def explain(self, brief: bool = False) -> str:
        """Return a human-readable explanation of this violation mask."""
        if brief or not self.detail:
            return self.title
        return f"{self.title}\n\n{self.detail}"

    def __str__(self) -> str:
        return f"{type(self).__name__}[{self.bits}]::{self.name}[{self.value}]"

    def __format__(self, format_spec: str) -> str:
        match format_spec:
            case "":
                return str(self)
            case "b":
                return self.bits
            case _:
                if (
                    any(c in format_spec for c in "<>^")
                    and format_spec[-1] not in "bcdoxXn"
                ):
                    return format(str(self), format_spec)
                return super().__format__(format_spec)


class LspViolation(_LspViolationBase):
    """Categorize orthogonal grades of LSP signature and callable violations."""

    ZERO = 0

    # Positional & Arity
    POS_ONLY_RENAMED = auto()
    DROPPED_VAR_POS = auto()
    REDUCED_MAX_POS = auto()
    INCREASED_MIN_POS = auto()

    # Keyword & Binding Vectors
    DROPPED_VAR_KW = auto()
    LOST_KW_ACCESS = auto()
    LOST_POS_ACCESS = auto()
    DROPPED_KW_NAME = auto()
    ADDED_REQUIRED_KW = auto()

    # Parameter Types (Contravariance)
    ADDED_PARAM_CONSTRAINT = auto()
    NARROWED_PARAM_TYPE = auto()
    DISJOINT_PARAM_TYPE = auto()

    # Return Types (Covariance)
    WIDENED_RETURN_SUPERSET = auto()
    OVERLAPPING_RETURN_UNION = auto()
    DISJOINT_RETURN_TYPE = auto()

    # Execution Semantics
    SYNC_ASYNC_MISMATCH = auto()
    GENERATOR_MISMATCH = auto()
    DESCRIPTOR_BINDING_SHIFT = auto()

    # -- Presets -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    HOOK_PLUGIN = (
        POS_ONLY_RENAMED
        | DROPPED_VAR_POS
        | DROPPED_VAR_KW
        | ADDED_PARAM_CONSTRAINT
    )

    SINK_CALLBACK = (
        POS_ONLY_RENAMED
        | DROPPED_VAR_POS
        | DROPPED_VAR_KW
        | DROPPED_KW_NAME
        | WIDENED_RETURN_SUPERSET
        | OVERLAPPING_RETURN_UNION
        | DISJOINT_RETURN_TYPE
    )

    MORPHING_INCLUSIVE = (
        POS_ONLY_RENAMED | ADDED_PARAM_CONSTRAINT | WIDENED_RETURN_SUPERSET
    )

    MORPHING_ANY_RETURN = (
        MORPHING_INCLUSIVE | OVERLAPPING_RETURN_UNION | DISJOINT_RETURN_TYPE
    )

    def _describe(self) -> tuple[str, str]:
        match self:
            case LspViolation.ZERO:
                return (
                    "No violation",
                    "Replacement signature is strictly LSP-compliant; not even positional-only parameter renaming is permitted.",
                )

            # Positional & Arity
            case LspViolation.POS_ONLY_RENAMED:
                return (
                    "Positional-only parameter renamed",
                    "Callers cannot pass positional-only parameters by keyword, so runtime calls never break, though strict reflection or stub checkers flag the name mismatch.",
                )
            case LspViolation.DROPPED_VAR_POS:
                return (
                    "Variadic positional absorption lost",
                    "Baseline promised infinite positional argument absorption via *args; replacement caps positional arity.",
                )
            case LspViolation.REDUCED_MAX_POS:
                return (
                    "Finite positional capacity reduced",
                    "Baseline accepted a larger finite number of positional arguments than replacement; fails when optional positional arguments are supplied.",
                )
            case LspViolation.INCREASED_MIN_POS:
                return (
                    "Minimum required positional arguments increased",
                    "Replacement demands more positional arguments than baseline's minimum (by removing a default or adding a required parameter).",
                )

            # Keyword & Binding Vectors
            case LspViolation.DROPPED_VAR_KW:
                return (
                    "Keyword absorption lost",
                    "Baseline absorbed arbitrary keyword arguments; replacement rejects unknown keys with TypeError.",
                )
            case LspViolation.LOST_KW_ACCESS:
                return (
                    "Keyword access vector removed",
                    "Parameter still exists at the same position, but changed from positional-or-keyword to positional-only (/); callers passing it by keyword fail with TypeError.",
                )
            case LspViolation.LOST_POS_ACCESS:
                return (
                    "Positional access vector removed",
                    "Parameter still exists with the same name, but changed from positional-or-keyword to keyword-only (*); callers passing it positionally fail with TypeError.",
                )
            case LspViolation.DROPPED_KW_NAME:
                return (
                    "Named keyword parameter removed",
                    "A specific keyword parameter accepted by baseline no longer exists and cannot be absorbed by **kwargs.",
                )
            case LspViolation.ADDED_REQUIRED_KW:
                return (
                    "Mandatory keyword parameter added",
                    "Replacement introduces a new keyword-only parameter without a default value; standard callers fail with TypeError.",
                )

            # Parameter Types (Contravariance)
            case LspViolation.ADDED_PARAM_CONSTRAINT:
                return (
                    "Parameter type annotation added",
                    "Baseline accepted Any (untyped), while replacement declares an explicit type constraint; safe in plain Python, fails under runtime type guards.",
                )
            case LspViolation.NARROWED_PARAM_TYPE:
                return (
                    "Parameter type narrowed (contravariance break)",
                    "Replacement accepts a strict subtype of baseline's input; fails whenever a valid supertype or union branch from baseline is passed.",
                )
            case LspViolation.DISJOINT_PARAM_TYPE:
                return (
                    "Incompatible parameter type",
                    "Replacement parameter type has zero overlap with baseline's parameter type; guaranteed failure for any valid baseline input.",
                )

            # Return Types (Covariance)
            case LspViolation.WIDENED_RETURN_SUPERSET:
                return (
                    "Return type widened to superset (covariance break)",
                    "Original return type remains included as a subtype or union member of the new return type; callers checking types dynamically can still handle it.",
                )
            case LspViolation.OVERLAPPING_RETURN_UNION:
                return (
                    "Return type partially shifted",
                    "Intersection exists between baseline and replacement return types, but some baseline return types disappear while unexpected new types appear.",
                )
            case LspViolation.DISJOINT_RETURN_TYPE:
                return (
                    "Incompatible return type",
                    "Replacement return type shares zero overlap with baseline's return type; safe only for sinks where the caller discards the return value.",
                )

            # Execution Semantics
            case LspViolation.SYNC_ASYNC_MISMATCH:
                return (
                    "Sync/async calling convention mismatch",
                    "Switching between def and async def breaks the coroutine protocol: sync callers receive an unawaited coroutine, or async callers fail awaiting a non-awaitable.",
                )
            case LspViolation.GENERATOR_MISMATCH:
                return (
                    "Generator/eager execution mismatch",
                    "Switching between a standard return and yield changes immediate execution into lazy iterator creation.",
                )
            case LspViolation.DESCRIPTOR_BINDING_SHIFT:
                return (
                    "Descriptor binding convention changed",
                    "Changing between bound method, @classmethod, and @staticmethod alters implicit receiver (self/cls) injection and shifts positional indices.",
                )

            # Presets
            case LspViolation.HOOK_PLUGIN:
                return (
                    "Plugin/hook extension preset",
                    "Allows narrowing open *args/**kwargs extension points into concrete typed parameters while permitting positional-only renames.",
                )
            case LspViolation.SINK_CALLBACK:
                return (
                    "Fire-and-forget sink callback preset",
                    "Ignores return type changes completely and allows dropping unused variadic or optional keyword arguments.",
                )
            case LspViolation.MORPHING_INCLUSIVE:
                return (
                    "Inclusive return-morphing preset",
                    "Allows widening the return type as long as the baseline return type remains a valid subtype or member of the new return contract.",
                )
            case LspViolation.MORPHING_ANY_RETURN:
                return (
                    "Unrestricted return-morphing preset",
                    "Allows replacing the return type with any type while preserving strict input call compatibility.",
                )

            case _:
                return super()._describe()


#  LINE: -- Parameter Kind & Single Parameter Spec -- -- - -- -- - -- --


class SigPart(EnumZero):
    """
    Govern the 5 Parameter Kinds - f(a, /, b, b=B, *c, d=D, **e)

    - 0: Pure Positional Arguments
    - 1: Mixed Positional and Keyword Arguments
    - 2: Unbound Tuple(len[0,..N]) with Positional Arguments
    - 3: Pure Keyword Arguments
    - 4: Unbound Dict(len[0,..N]) with Keyword Arguments
    """

    POSARG = auto()
    ANYARG = auto()
    ARGS = auto()
    KEYARG = auto()
    KWARGS = auto()

    def to_inspect(self) -> _ParameterKind:
        """Provide corresponding inspect._ParameterKind."""
        return _ParameterKind(self.value)

    @overload
    @classmethod
    def map(cls, target: SigPart, /) -> _ParameterKind: ...
    @overload
    @classmethod
    def map(cls, target: _ParameterKind, /) -> SigPart: ...
    @classmethod
    def map(
        cls, target: SigPart | _ParameterKind, /
    ) -> _ParameterKind | SigPart:
        """Swap SigPart or inspect._ParameterKind to its counterpart."""
        match target:
            case SigPart():
                return _ParameterKind(target.value)
            case _ParameterKind():
                return cls(target.value)


class SigArg(NamedTuple):
    """Define the immutable spec of 1 signature parameter."""

    name: str
    kind: SigPart
    default: Any = EMPTY
    annotation: Any = EMPTY

    @property
    def has_default(self) -> bool:
        return self.default is not EMPTY

    @property
    def has_annotation(self) -> bool:
        return self.annotation is not EMPTY

    @classmethod
    def from_parameter(
        cls, param: Parameter, resolved_annotation: Any = EMPTY
    ) -> Self:
        annotation = (
            resolved_annotation
            if resolved_annotation is not EMPTY
            else param.annotation
        )
        return cls(
            name=param.name,
            kind=SigPart.map(param.kind),
            default=param.default,
            annotation=annotation,
        )

    def __str__(self) -> str:
        return f"{type(self).__name__}[{self.name}]::{self.kind}"


#  LINE: -- Kind-Specific Ordered Parameter Sets -- -- - -- -- - -- --


class SigParam:
    """
    Ordered, immutable set-like container for parameters of a single SigPart kind.

    Backed by a valueless dict to preserve declaration order with O(1) lookup.
    """

    KIND: SigPart | None = None
    MAX_ITEMS: int | None = None

    __slots__ = ("_data", "_by_name")

    def __init__(self, *args: SigArg):
        if self.MAX_ITEMS is not None and len(args) > self.MAX_ITEMS:
            raise ValueError(
                f"{type(self).__name__} accepts at most {self.MAX_ITEMS} item(s), got {len(args)}"
            )
        data: dict[SigArg, None] = {}
        by_name: dict[str, SigArg] = {}
        for arg in args:
            if self.KIND is not None and arg.kind is not self.KIND:
                raise TypeError(
                    f"{type(self).__name__} requires {self.KIND}, got {arg.kind}"
                )
            if arg.name in by_name:
                raise ValueError(f"Duplicate parameter name: {arg.name!r}")
            data[arg] = None
            by_name[arg.name] = arg

        self._data: dict[SigArg, None] = data
        self._by_name: dict[str, SigArg] = by_name

    @property
    def names(self) -> list[str]:
        return list(self._by_name)

    @property
    def required(self) -> tuple[SigArg, ...]:
        return tuple(arg for arg in self._data if not arg.has_default)

    @property
    def optional(self) -> tuple[SigArg, ...]:
        return tuple(arg for arg in self._data if arg.has_default)

    def get(self, name: str, default: Any = None) -> SigArg | Any:
        return self._by_name.get(name, default)

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[SigArg]:
        return iter(self._data)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SigParam):
            return NotImplemented
        return type(self) is type(other) and tuple(self._data) == tuple(
            other._data
        )

    def __hash__(self) -> int:
        return hash((type(self), tuple(self._data)))

    def __contains__(self, item: object) -> bool:
        match item:
            case str():
                return item in self._by_name
            case SigArg():
                return item in self._data
            case _:
                return False

    @overload
    def __getitem__(self, key: str) -> SigArg: ...
    @overload
    def __getitem__(self, key: int) -> SigArg: ...
    def __getitem__(self, key: str | int) -> SigArg:
        match key:
            case str():
                return self._by_name[key]
            case int():
                return tuple(self._data)[key]
            case _:
                raise TypeError(f"Unsupported key type: {type(key).__name__}")

    def __sub__(self, other: Self) -> Self:
        if not isinstance(other, type(self)):
            return NotImplemented
        return type(self)(
            *(arg for arg in self._data if arg not in other._data)
        )

    def __and__(self, other: Self) -> Self:
        if not isinstance(other, type(self)):
            return NotImplemented
        return type(self)(*(arg for arg in self._data if arg in other._data))

    def __or__(self, other: Self) -> Self:
        if not isinstance(other, type(self)):
            return NotImplemented
        merged = {**self._by_name, **other._by_name}
        return type(self)(*merged.values())

    def __str__(self) -> str:
        return f"{type(self).__name__}[{','.join(self.names)}]"

    def __repr__(self) -> str:
        return f"{self}({','.join(f'{arg!r}' for arg in self)})"


class PosArgs(SigParam):
    """Positional-only parameters (a, b, /)."""

    KIND = SigPart.POSARG

    def check_renames(self, target_slots: list[SigArg]) -> LspViolation:
        """Flag if any positional-only parameter changed its name at its index."""
        for idx, base_arg in enumerate(self):
            if (
                idx < len(target_slots)
                and target_slots[idx].name != base_arg.name
            ):
                return LspViolation.POS_ONLY_RENAMED
        return LspViolation.ZERO


class AnyArgs(SigParam):
    """Positional-or-keyword parameters (a, b=1)."""

    KIND = SigPart.ANYARG


class Args(SigParam):
    """Variadic positional parameter (*args)."""

    KIND = SigPart.ARGS
    MAX_ITEMS = 1

    @property
    def param(self) -> SigArg | None:
        return next(iter(self._data), None)


class KeyArgs(SigParam):
    """Keyword-only parameters (*, k, m=2)."""

    KIND = SigPart.KEYARG


class Kwargs(SigParam):
    """Variadic keyword parameter (**kwargs)."""

    KIND = SigPart.KWARGS
    MAX_ITEMS = 1

    @property
    def param(self) -> SigArg | None:
        return next(iter(self._data), None)


#  LINE: -- Type Variance Helpers -- -- - -- -- - -- -- - -- -- - -- --


def _unpack_union(tp: Any) -> tuple[Any, ...]:
    origin = get_origin(tp)
    if origin is Union or origin is UnionType:
        return get_args(tp)
    return (tp,)


def _is_untyped(tp: Any) -> bool:
    return tp is EMPTY or tp is Any


def _is_subtype(sub: Any, sup: Any) -> bool:
    """Best-effort runtime subtype check supporting unions, None, and generics."""
    if sub == sup or sup is Any or sup is EMPTY:
        return True
    if sub is Any or sub is EMPTY:
        return False
    if sub is None:
        sub = type(None)
    if sup is None:
        sup = type(None)

    sub_members = _unpack_union(sub)
    sup_members = _unpack_union(sup)
    if len(sub_members) > 1 or len(sup_members) > 1:
        return all(
            any(_is_subtype(s_m, p_m) for p_m in sup_members)
            for s_m in sub_members
        )

    sub_origin = get_origin(sub) or sub
    sup_origin = get_origin(sup) or sup

    if isinstance(sub_origin, type) and isinstance(sup_origin, type):
        try:
            if not issubclass(sub_origin, sup_origin):
                return False
        except TypeError:
            return False

        sub_args = get_args(sub)
        sup_args = get_args(sup)
        if not sup_args:
            return True
        if len(sub_args) != len(sup_args):
            return False
        return all(
            _is_subtype(sa, pa)
            for sa, pa in zip(sub_args, sup_args, strict=True)
        )

    return False


def _types_overlap(t1: Any, t2: Any) -> bool:
    if _is_untyped(t1) or _is_untyped(t2):
        return True
    m1 = _unpack_union(t1)
    m2 = _unpack_union(t2)
    return any(_is_subtype(a, b) or _is_subtype(b, a) for a in m1 for b in m2)


def _check_param_variance(base_t: Any, new_t: Any) -> LspViolation:
    """Evaluate contravariant parameter type compatibility (base -> new)."""
    if _is_untyped(new_t):
        return LspViolation.ZERO
    if _is_untyped(base_t):
        return LspViolation.ADDED_PARAM_CONSTRAINT
    if _is_subtype(base_t, new_t):
        # Contravariant: replacement accepts base_t or a wider supertype
        return LspViolation.ZERO
    if _types_overlap(base_t, new_t):
        return LspViolation.NARROWED_PARAM_TYPE
    return LspViolation.DISJOINT_PARAM_TYPE


def _check_return_variance(base_r: Any, new_r: Any) -> LspViolation:
    """Evaluate covariant return type compatibility (base -> new)."""
    if _is_untyped(base_r):
        return LspViolation.ZERO
    if _is_untyped(new_r):
        return LspViolation.WIDENED_RETURN_SUPERSET
    if _is_subtype(new_r, base_r):
        # Covariant: replacement returns base_r or a narrower subtype
        return LspViolation.ZERO
    if _is_subtype(base_r, new_r):
        return LspViolation.WIDENED_RETURN_SUPERSET
    if _types_overlap(base_r, new_r):
        return LspViolation.OVERLAPPING_RETURN_UNION
    return LspViolation.DISJOINT_RETURN_TYPE


#  LINE: -- Signature Specification -- -- - -- -- - -- -- - -- -- - -- --


@dataclass(frozen=True, slots=True)
class SigSpec:
    """
    Preprocessed, immutable callable signature supporting set-like LSP comparison:

        if new_sig in base_sig: ...
        violations = base_sig - new_sig
    """

    pos: PosArgs
    both: AnyArgs
    args: Args
    key: KeyArgs
    kwargs: Kwargs
    result: Any = EMPTY

    is_async: bool = False
    is_generator: bool = False
    binding: BindingKind = "function"
    tolerance: LspViolation = LspViolation.ZERO

    @classmethod
    def from_callable(
        cls,
        target: Callable[..., Any],
        *,
        tolerance: LspViolation = LspViolation.ZERO,
        include_extras: bool = False,
    ) -> Self:
        """Inspect a callable and build a normalized SigSpec."""
        binding: BindingKind = "function"
        raw = target
        if isinstance(raw, staticmethod):
            binding = "staticmethod"
            raw = raw.__func__
        elif isinstance(raw, classmethod):
            binding = "classmethod"
            raw = raw.__func__
        elif getattr(raw, "__self__", None) is not None:
            binding = "method"

        unwrapped = unwrap(raw)
        sig = signature(raw)

        try:
            hints = get_type_hints(unwrapped, include_extras=include_extras)
        except Exception:
            hints = getattr(unwrapped, "__annotations__", {})

        buckets: dict[SigPart, list[SigArg]] = {part: [] for part in SigPart}
        for param in sig.parameters.values():
            resolved = hints.get(param.name, param.annotation)
            arg = SigArg.from_parameter(param, resolved_annotation=resolved)
            buckets[arg.kind].append(arg)

        return cls(
            pos=PosArgs(*buckets[SigPart.POSARG]),
            both=AnyArgs(*buckets[SigPart.ANYARG]),
            args=Args(*buckets[SigPart.ARGS]),
            key=KeyArgs(*buckets[SigPart.KEYARG]),
            kwargs=Kwargs(*buckets[SigPart.KWARGS]),
            result=hints.get("return", sig.return_annotation),
            is_async=iscoroutinefunction(unwrapped)
            or isasyncgenfunction(unwrapped),
            is_generator=isgeneratorfunction(unwrapped)
            or isasyncgenfunction(unwrapped),
            binding=binding,
            tolerance=tolerance,
        )

    def with_tolerance(self, tolerance: LspViolation) -> Self:
        """Return a copy of this SigSpec configured with a new violation tolerance."""
        return type(self)(
            pos=self.pos,
            both=self.both,
            args=self.args,
            key=self.key,
            kwargs=self.kwargs,
            result=self.result,
            is_async=self.is_async,
            is_generator=self.is_generator,
            binding=self.binding,
            tolerance=tolerance,
        )

    @property
    def positional_slots(self) -> list[SigArg]:
        """All parameters addressable by position in index order."""
        return [*self.pos, *self.both]

    @property
    def keyword_map(self) -> dict[str, SigArg]:
        """All parameters addressable by keyword name."""
        return {arg.name: arg for arg in (*self.both, *self.key)}

    @property
    def min_positional(self) -> int:
        return sum(1 for arg in self.positional_slots if not arg.has_default)

    @property
    def max_positional(self) -> int | None:
        """Maximum positional arguments accepted, or None if unbounded (*args)."""
        return None if self.args else len(self.positional_slots)

    def diff(self, other: SigSpec) -> LspViolation:
        """
        Compute all LSP violations introduced when replacing `self` (baseline)

        with `other` (candidate). Returns LspViolation.ZERO when strictly valid.
        """
        violations = LspViolation.ZERO

        # 1. Execution & Calling Convention
        if self.is_async != other.is_async:
            violations |= LspViolation.SYNC_ASYNC_MISMATCH
        if self.is_generator != other.is_generator:
            violations |= LspViolation.GENERATOR_MISMATCH
        if self.binding != other.binding:
            violations |= LspViolation.DESCRIPTOR_BINDING_SHIFT

        # 2. Positional Vector & Arity
        base_pos = self.positional_slots
        new_pos = other.positional_slots

        if other.min_positional > self.min_positional:
            violations |= LspViolation.INCREASED_MIN_POS

        if self.args and not other.args:
            violations |= LspViolation.DROPPED_VAR_POS
        elif not self.args and not other.args and len(new_pos) < len(base_pos):
            violations |= LspViolation.REDUCED_MAX_POS

        violations |= self.pos.check_renames(new_pos)

        # Positional parameter type contravariance
        overlap_len = min(len(base_pos), len(new_pos))
        for idx in range(overlap_len):
            violations |= _check_param_variance(
                base_pos[idx].annotation, new_pos[idx].annotation
            )

        if other.args.param is not None:
            for idx in range(overlap_len, len(base_pos)):
                violations |= _check_param_variance(
                    base_pos[idx].annotation, other.args.param.annotation
                )
            if self.args.param is not None:
                violations |= _check_param_variance(
                    self.args.param.annotation, other.args.param.annotation
                )

        # 3. Keyword Vector & Access Modes
        base_kw = self.keyword_map
        new_kw = other.keyword_map
        new_pos_only_names = set(other.pos.names)
        base_any_names = set(self.both.names)
        new_key_only_names = set(other.key.names)

        if self.kwargs and not other.kwargs:
            violations |= LspViolation.DROPPED_VAR_KW

        for name, base_arg in base_kw.items():
            if name in new_kw:
                new_arg = new_kw[name]
                if name in base_any_names and name in new_key_only_names:
                    violations |= LspViolation.LOST_POS_ACCESS
                violations |= _check_param_variance(
                    base_arg.annotation, new_arg.annotation
                )
            elif name in new_pos_only_names:
                violations |= LspViolation.LOST_KW_ACCESS
            elif other.kwargs.param is not None:
                violations |= _check_param_variance(
                    base_arg.annotation, other.kwargs.param.annotation
                )
            else:
                violations |= LspViolation.DROPPED_KW_NAME

        if self.kwargs.param is not None and other.kwargs.param is not None:
            violations |= _check_param_variance(
                self.kwargs.param.annotation, other.kwargs.param.annotation
            )

        # Newly introduced required keyword-addressable parameters
        base_min_pos = self.min_positional
        for idx, arg in enumerate(other.both):
            if (
                arg.name not in base_kw
                and not arg.has_default
                and (len(self.pos) + idx) >= base_min_pos
            ):
                violations |= LspViolation.ADDED_REQUIRED_KW

        for arg in other.key:
            if arg.name not in base_kw and not arg.has_default:
                violations |= LspViolation.ADDED_REQUIRED_KW

        # 4. Return Type Covariance
        violations |= _check_return_variance(self.result, other.result)

        return violations

    def allows(
        self, other: SigSpec, tolerance: LspViolation | None = None
    ) -> bool:
        """Check whether `other` may substitute `self` under the given tolerance."""
        limit = self.tolerance if tolerance is None else tolerance
        return (self.diff(other) & ~limit) == LspViolation.ZERO

    def __sub__(self, other: SigSpec) -> LspViolation:
        """Return the LspViolation bitmask of contracts in `self` broken by `other`."""
        if not isinstance(other, SigSpec):
            return NotImplemented
        return self.diff(other)

    def __contains__(self, other: object) -> bool:
        """Return True if `other` is an acceptable replacement under `self.tolerance`."""
        if not isinstance(other, SigSpec):
            return False
        return self.allows(other)

    def __str__(self) -> str:
        parts: list[str] = []
        if self.pos:
            parts.extend(arg.name for arg in self.pos)
            parts.append("/")
        parts.extend(arg.name for arg in self.both)
        if self.args.param:
            parts.append(f"*{self.args.param.name}")
        elif self.key:
            parts.append("*")
        parts.extend(arg.name for arg in self.key)
        if self.kwargs.param:
            parts.append(f"**{self.kwargs.param.name}")
        prefix = "async " if self.is_async else ""
        return f"{prefix}SigSpec({', '.join(parts)})"


if __name__ == "__main__":

    def strict_base(x: int | str, /, mode: str = "fast") -> int | None: ...
    def valid_sub(
        x: int | str | float, mode: object = "safe", extra: bool = True
    ) -> int: ...
    def invalid_sub(y: int, /, *, mode: str) -> str: ...

    base = SigSpec.from_callable(strict_base)
    good = SigSpec.from_callable(valid_sub)
    bad = SigSpec.from_callable(invalid_sub)

    print("Base:", base)
    print("Good in Base (strict):", good in base, "->", base - good)
    print("Bad in Base (strict): ", bad in base, "->", base - bad)
    print((base - bad).explain())

    print("---")

    def hook_base(*args: Any, **kwargs: Any) -> None: ...
    def hook_impl(event_id: int = 0) -> None: ...

    hook = SigSpec.from_callable(hook_base, tolerance=LspViolation.HOOK_PLUGIN)
    plugin = SigSpec.from_callable(hook_impl)

    print("Hook raw diff:", hook - plugin)
    print("Plugin allowed by hook:", plugin in hook)
