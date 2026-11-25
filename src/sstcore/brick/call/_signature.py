"""
Analyze the Signature of Callables

-
"""

__all__: list[str] = [
    "SigPart",
    "SigVar",
    "SigParam",
    "SigVar",
]

import inspect as _inspect
from collections.abc import Callable, Iterator
from dataclasses import dataclass, replace
from enum import auto
from inspect import Parameter, Signature, _empty, _ParameterKind
from typing import Any, NamedTuple, Self, overload

from ...port._types import Types as _T  # noqa:N814
from ...port.casting import LspViolation
from ...port.empty import VOID, MayNot
from ...port.solid import EnumZero
from .. import reflect

EMPTY: type[_empty] = _empty


type Buckets = dict[SigPart, list[SigVar]]


class SigPart(EnumZero):  # MOVE: to reflect.sig?
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

    # IDEA: RETURN? then truly all parts can be detected

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

    @classmethod
    def buckets(cls, hints: _T.StrDict, sig: Signature) -> Buckets:
        # IDEA: from func?
        """Fill Table with all SigVars mapped to SigParts"""
        buckets: Buckets = {part: [] for part in SigPart}
        for param in sig.parameters.values():
            resolved: Any = hints.get(param.name, param.annotation)
            arg: SigVar = SigVar.detect(param, annotation=resolved)
            buckets[arg.kind].append(arg)
        return buckets


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class _SigVarData(NamedTuple):  # MOVE: to port.primitives._tuples
    name: str
    kind: SigPart
    default: Any = VOID
    annotation: Any = VOID


class SigVar(_SigVarData):
    """Define the Spec of 1 Signature Part: Parameter or Return"""

    # NEXT: ensure that for kind=RETURN -> default=VOID or Raise
    # def __new__(cls, *args, **kwargs): ...
    # - other ideas, install the detect here as overload?
    # - if not, how else to use new and still propagate the signature?

    # AI_TASK: compare with
    def __str__(self) -> str:
        return f"{type(self).__name__}[{self.name}]::{self.kind}"

    @property
    def has_default(self) -> bool:
        return self.default is not VOID

    @property
    def has_annotation(self) -> bool:
        return self.annotation is not VOID

    @classmethod
    def detect(
        cls, param: Parameter, default: Any = VOID, annotation: Any = VOID
    ) -> Self:
        return cls(
            name=param.name,
            kind=SigPart.map(param.kind),
            # CHECK: what is with EMPTY? when filtered out?
            default=param.default if default is VOID else default,
            annotation=param.annotation if annotation is VOID else annotation,
        )


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class SigParam:
    # AI: unsure if this is actually needed
    # - for sure some comparison inbetween each of the 5 categories would be nice,
    #   - but doing them disjointed from the SigSpec might be rare
    #   - doing  them disjointed provides only partial results
    # -> maybe the best to mount all checks to the final class?
    """Define the Rules for 1 Signature Parameter Kind"""

    __slots__ = ("_data",)

    def __init__(self, *args: SigVar):
        self._data: dict[SigVar, None] = {arg: None for arg in args}

    @property
    def names(self) -> list[str]:
        return [arg.name for arg in self._data]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[SigVar]:
        return iter(self._data)

    def __contains__(self, item: object) -> bool:
        # TODO: - check by name - check by SigVar - what else? return item in self._data
        raise NotImplementedError(item)

    def __getitem__(self, key: str) -> Any:
        # TODO: - get by name? return self._data[key]
        raise NotImplementedError(key)

    @property
    def required(self) -> tuple[SigVar, ...]:
        return tuple(arg for arg in self._data if not arg.has_default)

    @property
    def optional(self) -> tuple[SigVar, ...]:
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
        merged = {**self._by_name, **other._by_name}
        return type(self)(*merged.values())


#  LINE: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class PosArgs(SigParam): ...


class AnyArgs(SigParam): ...


class Args(SigParam): ...


class KeyArgs(SigParam): ...


class Kwargs(SigParam): ...


#  LINE: -- Func -- -- - -- -- - -- -- - -- -- - -- -- - -- --


#  LINE: -- Signature -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@dataclass(frozen=True, slots=True)
class SigSpec:
    # NEXT: assign simpler types
    pos: PosArgs
    both: AnyArgs
    args: Args
    key: KeyArgs
    kwargs: Kwargs

    result: Any = VOID

    is_async: bool = False
    is_generator: bool = False
    binding: reflect.sig.Binding = reflect.sig.Binding.FUNC
    tolerance: LspViolation = LspViolation.ZERO

    # TODO: return Args/Kwargs or Params from port._params as property

    @property
    def positional_slots(self) -> list[SigVar]:
        """All parameters addressable by position in index order"""
        return [*self.pos, *self.both]

    @property
    def keyword_map(self) -> dict[str, SigVar]:
        """All parameters addressable by keyword name"""
        return {arg.name: arg for arg in (*self.both, *self.key)}

    @property
    def min_positional(self) -> int:
        return sum(1 for arg in self.positional_slots if not arg.has_default)

    @property
    def max_positional(self) -> int | None:
        """Maximum positional arguments accepted, or None if unbounded (*args)."""
        return None if self.args else len(self.positional_slots)

    def __sub__(self, other: Self) -> Self:
        """Delegate the difference logic to the individual groups"""
        if not isinstance(other, type(self)):
            return NotImplemented
        raise NotImplementedError

    def __and__(self, other: Self) -> Self:
        if not isinstance(other, type(self)):
            return NotImplemented
        """Delegate the intersection logic to the individual groups"""
        raise NotImplementedError

    def __contains__(self, other: object) -> bool:
        """Is the incoming a valid replacement? (according to self.tolerance)"""
        if not isinstance(other, SigSpec):
            return False
        return self.allows(other)

    def allows(
        self, other: SigSpec, tolerance: MayNot[LspViolation] = None
    ) -> bool:
        """Check whether `other` may substitute `self` under the given tolerance."""
        limit: LspViolation = self.tolerance if tolerance is None else tolerance
        return (self.diff(other) & ~limit) == LspViolation.ZERO

    def diff(self, other: SigSpec) -> LspViolation:
        """
        Compute all LSP violations introduced when replacing `self` (baseline)

        with `other` (candidate). Returns LspViolation.ZERO when strictly valid.
        """
        # AI_TASK: this needs to be split down! many small pieces
        violations: LspViolation = LspViolation.ZERO

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
                    base_pos[idx].annotation,
                    other.args.param.annotation,
                )
            if self.args.param is not None:
                violations |= _check_param_variance(
                    self.args.param.annotation,
                    other.args.param.annotation,
                )

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
                    base_arg.annotation,
                    other.kwargs.param.annotation,
                )
            else:
                violations |= LspViolation.DROPPED_KW_NAME

        if self.kwargs.param is not None and other.kwargs.param is not None:  # ty:ignore FIX:
            violations |= _check_param_variance(
                self.kwargs.param.annotation,
                other.kwargs.param.annotation,
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

    def evolve(
        self,
        is_async: MayNot[bool] = None,
        is_generator: MayNot[bool] = None,
        binding: MayNot[reflect.sig.Binding] = None,
        tolerance: MayNot[LspViolation] = None,
    ) -> Self:
        """Copy the Spec to new Configuration with same SigVars"""
        return replace(
            self,
            is_async=self.is_async if is_async is None else is_async,
            is_generator=self.is_generator
            if is_generator is None
            else is_generator,
            binding=self.binding if binding is None else binding,
            tolerance=self.tolerance if tolerance is None else tolerance,
        )

    @classmethod
    def detect(
        cls,
        target: Callable[..., Any],
        *,
        tolerance: LspViolation = LspViolation.ZERO,
        include_extras: bool = False,
    ) -> Self:
        """Inspect Callable and build normalized SigSpec"""
        _binding = reflect.sig.Binding.detect(target)
        raw: Callable = _binding.raw(target)
        unwrapped: Callable = _inspect.unwrap(raw)
        sig: Signature = _inspect.signature(raw)
        hints: _T.StrDict = reflect.typehint.find(
            unwrapped, include_extras=include_extras
        )
        buckets: Buckets = SigPart.buckets(hints, sig)
        return cls(
            pos=PosArgs(*buckets[SigPart.POSARG]),
            both=AnyArgs(*buckets[SigPart.ANYARG]),
            args=Args(*buckets[SigPart.ARGS]),
            key=KeyArgs(*buckets[SigPart.KEYARG]),
            kwargs=Kwargs(*buckets[SigPart.KWARGS]),
            result=reflect.sig.returns(hints, sig),
            is_async=reflect.sig.is_async(unwrapped),
            is_generator=reflect.sig.is_generator(unwrapped),
            binding=_binding,
            tolerance=tolerance,
        )


def _check_param_variance(base_t: Any, new_t: Any) -> LspViolation:
    """Evaluate contravariant parameter type compatibility (base -> new)."""

    if reflect.types.is_untyped(new_t):
        return LspViolation.ZERO

    if reflect.types.is_untyped(base_t):
        return LspViolation.ADDED_PARAM_CONSTRAINT

    if reflect.types.is_subtype(base_t, new_t):
        return LspViolation.ZERO

    if reflect.types.overlap(base_t, new_t):
        return LspViolation.NARROWED_PARAM_TYPE

    return LspViolation.DISJOINT_PARAM_TYPE


def _check_return_variance(base_r: Any, new_r: Any) -> LspViolation:
    """Evaluate covariant return type compatibility (base -> new)."""

    if reflect.types.is_untyped(base_r):
        return LspViolation.ZERO

    if reflect.types.is_untyped(new_r):
        return LspViolation.WIDENED_RETURN_SUPERSET

    if reflect.types.is_subtype(new_r, base_r):
        return LspViolation.ZERO

    if reflect.types.is_subtype(base_r, new_r):
        return LspViolation.WIDENED_RETURN_SUPERSET

    if reflect.types.overlap(base_r, new_r):
        return LspViolation.OVERLAPPING_RETURN_UNION

    return LspViolation.DISJOINT_RETURN_TYPE
