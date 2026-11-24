"""
Analyze the Signature of Callables

-
"""

__all__: list[str] = [
    "SigPart",
    "SigArg",
    "SigParam",
    "SigArg",
]

from collections.abc import Callable, Iterator
from dataclasses import dataclass
from enum import auto
from inspect import (
    Parameter,
    Signature,
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

from ...port.casting import LspViolation
from ...port.empty import VOID
from ...port.solid import EnumZero

EMPTY: type[_empty] = _empty

s = Signature()
p = Parameter("name", _ParameterKind.KEYWORD_ONLY)


class SigPart(EnumZero):
    # CHECK: additional value to just using _ParameterKind?
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
    # IDEA: RETURN?

    def to_inspect(self) -> _ParameterKind:
        """Provide corresponding inspect._ParameterKind"""
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
        """Swap sstcore.Param or inspect._ParameterKind to counterpart"""
        match target:
            case SigPart():
                return _ParameterKind(target.value)
            case _ParameterKind():
                return SigPart(target.value)


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class SigArg(NamedTuple):
    """Define the Spec of 1 Signature Parameter"""

    name: str
    kind: SigPart  # CHECK: default?
    default: Any = VOID
    annotation: Any = VOID

    def __str__(self) -> str:
        return f"{type(self).__name__}[{self.name}]::{self.kind}"

    @property
    def has_default(self) -> bool:
        return self.default is not VOID

    @property
    def has_annotation(self) -> bool:
        return self.annotation is not VOID

    @classmethod
    def from_parameter(
        # CHECK: what is useful??
        cls,
        param: Parameter,
        resolved_annotation: Any = VOID,
    ) -> Self:
        annotation = (
            resolved_annotation
            if resolved_annotation is not VOID
            else param.annotation
        )
        return cls(
            name=param.name,
            kind=SigPart.map(param.kind),
            default=param.default,
            annotation=annotation,
        )


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class SigParam:
    """Define the Rules for 1 Signature Parameter Kind"""

    __slots__ = ("_data",)

    def __init__(self, *args: SigArg):
        self._data: dict[SigArg, None] = {arg: None for arg in args}

    @property
    def names(self) -> list[str]:
        return [arg.name for arg in self._data]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[SigArg]:
        return iter(self._data)

    def __contains__(self, item: object) -> bool:
        # TODO: - check by name - check by SigArg - what else? return item in self._data
        raise NotImplementedError(item)

    def __getitem__(self, key: str) -> Any:
        # TODO: - get by name? return self._data[key]
        raise NotImplementedError(key)

    @property
    def required(self) -> tuple[SigArg, ...]:
        return tuple(arg for arg in self._data if not arg.has_default)

    @property
    def optional(self) -> tuple[SigArg, ...]:
        return tuple(arg for arg in self._data if arg.has_default)

    def __sub__(self, other: Self) -> Self:  # CHECK:
        if not isinstance(other, type(self)):
            return NotImplemented
        return type(self)(
            *(arg for arg in self._data if arg not in other._data)
        )

    def __and__(self, other: Self) -> Self:  # CHECK:
        if not isinstance(other, type(self)):
            return NotImplemented
        return type(self)(*(arg for arg in self._data if arg in other._data))

    def __or__(self, other: Self) -> Self:
        # CHECK:
        if not isinstance(other, type(self)):
            return NotImplemented
        merged = {**self._by_name, **other._by_name}  # ty:ignore FIX:
        return type(self)(*merged.values())


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class PosArgs(SigParam): ...


class AnyArgs(SigParam): ...


class Args(SigParam): ...


class KeyArgs(SigParam): ...


class Kwargs(SigParam): ...


#  LINE: -- Return -- -- - -- -- - -- -- - -- -- - -- -- - -- --
#
def get_return(target: type):
    """
        Just as info how it works

        for -> Any the __annotations__ contain "return":typing.Any
        - Any and EMPTY cannot be used with is{instance|subclass}
    In lenient mode, empty is implicitly treated as Any.

    In strict mode (e.g., mypy --disallow-untyped-defs), empty is an error—it
    """
    if "return" not in target.__annotations__:
        _result = EMPTY


#  LINE: -- Signature -- -- - -- -- - -- -- - -- -- - -- -- - -- --


_BindingKind = Literal["function", "method", "classmethod", "staticmethod"]


@dataclass(frozen=True, slots=True)
class SigSpec:
    pos: PosArgs
    both: AnyArgs
    args: Args
    key: KeyArgs
    kwargs: Kwargs

    result: Any = VOID

    is_async: bool = False
    is_generator: bool = False
    binding: _BindingKind = "function"
    tolerance: LspViolation = LspViolation.ZERO

    def __sub__(self, other: Self) -> Self:
        if not isinstance(other, type(self)):
            return NotImplemented
        # Delegates the difference logic to the individual groups
        # return type(self)(
        #     speed_data=self.speed_data - other.speed_data,
        #     temp_data=self.temp_data - other.temp_data,
        # )
        raise NotImplementedError

    def __and__(self, other: Self) -> Self:
        if not isinstance(other, type(self)):
            return NotImplemented
        # Delegates the intersection logic to the individual groups
        # return MainContainer(
        #     speed_data=self.speed_data & other.speed_data,
        #     temp_data=self.temp_data & other.temp_data,
        # )
        raise NotImplementedError

    @classmethod
    def from_callable(
        cls,
        target: Callable[..., Any],
        *,
        tolerance: LspViolation = LspViolation.ZERO,
        include_extras: bool = False,
    ) -> Self:
        """Inspect a callable and build a normalized SigSpec."""
        binding: _BindingKind = "function"
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

        violations |= self.pos.check_renames(new_pos)  # ty:ignore FIX:

        # Positional parameter type contravariance
        overlap_len = min(len(base_pos), len(new_pos))
        for idx in range(overlap_len):
            violations |= _check_param_variance(
                base_pos[idx].annotation, new_pos[idx].annotation
            )

        if other.args.param is not None:  # ty:ignore FIX:
            for idx in range(overlap_len, len(base_pos)):
                violations |= _check_param_variance(
                    base_pos[idx].annotation,
                    other.args.param.annotation,  # ty:ignore FIX:
                )
            if self.args.param is not None:  # ty:ignore FIX:
                violations |= _check_param_variance(
                    self.args.param.annotation,  # ty:ignore FIX:
                    other.args.param.annotation,  # ty:ignore FIX:
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
            elif other.kwargs.param is not None:  # ty:ignore FIX:
                violations |= _check_param_variance(
                    base_arg.annotation,
                    other.kwargs.param.annotation,  # ty:ignore FIX:
                )
            else:
                violations |= LspViolation.DROPPED_KW_NAME

        if self.kwargs.param is not None and other.kwargs.param is not None:  # ty:ignore FIX:
            violations |= _check_param_variance(
                self.kwargs.param.annotation,  # ty:ignore FIX:
                other.kwargs.param.annotation,  # ty:ignore FIX:
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

    def __contains__(self, other: object) -> bool:
        """Return True if `other` is an acceptable replacement under `self.tolerance`."""
        # TASK: contains == fulfils LSP
        if not isinstance(other, SigSpec):
            return False
        return self.allows(other)

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


#  LINE: -- Func -- -- - -- -- - -- -- - -- -- - -- -- - -- --


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


def _unpack_union(tp: Any) -> tuple[Any, ...]:
    origin = get_origin(tp)
    if origin is Union or origin is UnionType:
        return get_args(tp)
    return (tp,)


def _types_overlap(t1: Any, t2: Any) -> bool:
    if _is_untyped(t1) or _is_untyped(t2):
        return True
    m1 = _unpack_union(t1)
    m2 = _unpack_union(t2)
    return any(_is_subtype(a, b) or _is_subtype(b, a) for a in m1 for b in m2)
