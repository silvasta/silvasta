"""
Analyze the Signature of Callables

-
"""

__all__: list[str] = [
    "SigVar",
    "SigPart",
    "SigSpec",
]

import inspect as _inspect
from collections.abc import Callable
from dataclasses import dataclass, replace
from enum import auto
from inspect import Parameter, Signature, _empty, _ParameterKind
from typing import Any, NamedTuple, Self, overload

from ...port._types import Types as _T  # noqa:N814
from ...port.casting import LspViolation
from ...port.empty import VOID, MayBe, MayNot
from ...port.primitives import TupleField
from ...port.solid import EnumZero
from .. import reflect
from . import _lsp

EMPTY: type[_empty] = _empty


type Buckets = dict[SigPart, list[SigVar]]
type SigVars = tuple[SigVar, ...]


class SigPart(EnumZero):  # MOVE: to reflect.sig? or port.casting?
    """
    Govern the 5 Parameter Kinds - f(a, /, b, b=B, *c, d=D, **e)

    - 0: Pure Positional Arguments
    - 1: Mixed Positional and Keyword Arguments
    - 2: Unbound Tuple(len[0,..N]) with Positional Arguments
    - 3: Pure Keyword Arguments
    - 4: Unbound Dict(len[0,..N]) with Keyword Arguments

    - 5: Return Value or not

    """

    POSARG = auto()
    ANYARG = auto()
    ARGS = auto()
    KEYARG = auto()
    KWARGS = auto()

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

    @classmethod  # IDEA: from func or sig?
    def buckets(cls, hints: _T.StrDict, sig: Signature) -> Buckets:
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

    icon = TupleField[str]("λ")
    sep = TupleField[str](": ")

    def __new__(
        cls,
        name: str,
        kind: SigPart,
        default: Any = VOID,
        annotation: Any = VOID,
    ) -> Self:
        default: MayBe[Any] = VOID if default is EMPTY else default
        annotation: MayBe[Any] = VOID if annotation is EMPTY else annotation
        return tuple.__new__(cls, (name, kind, default, annotation))

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
            default=param.default if default is VOID else default,
            annotation=param.annotation if annotation is VOID else annotation,
        )


#  LINE: -- Signature -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@dataclass(frozen=True, slots=True)
class SigSpec:
    pos: SigVars = ()
    both: SigVars = ()
    args: SigVars = ()
    key: SigVars = ()
    kwargs: SigVars = ()

    result: Any = VOID

    is_async: bool = False
    is_generator: bool = False
    binding: reflect.sig.Binding = reflect.sig.Binding.FUNC
    tolerance: LspViolation = LspViolation.ZERO

    # TODO: return Args/Kwargs or Params from port._params as property

    @property
    def positionals(self) -> list[SigVar]:
        """All parameters addressable by position in index order"""
        return [*self.pos, *self.both]

    @property
    def keyword_map(self) -> dict[str, SigVar]:
        """All parameters addressable by keyword name"""
        return {arg.name: arg for arg in (*self.both, *self.key)}

    @property
    def min_positional(self) -> int:
        return sum(1 for arg in self.positionals if not arg.has_default)

    @property
    def all_params(self) -> SigVars:
        return self.pos + self.both + self.key  # *args and **kwargs are special

    @property
    def required(self) -> SigVars:
        return tuple(p for p in self.all_params if not p.has_default)

    @property
    def has_var_positional(self) -> bool:
        return bool(self.args)

    @property
    def has_var_keyword(self) -> bool:
        return bool(self.kwargs)

    @property
    def max_positional(self) -> int | None:
        """Maximum positional arguments accepted, or None if unbound: (*args)"""
        return None if self.args else len(self.positionals)

    def __sub__(self, other: Self) -> Self:
        # AI_TASK: how to get the meaningful difference here?
        # - the operation is not commutative, meaning rsub (currently not needed) would not yield the same result
        if not isinstance(other, type(self)):
            return NotImplemented
        raise NotImplementedError

    def __and__(self, other: Self) -> Self:
        # AI_TASK: similar for the and, for kwargs it is easy, even for args, but for both?
        if not isinstance(other, type(self)):
            return NotImplemented
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
        """Compute all LSP violations when replacing `self` with `other`."""
        return (
            self._diff_execution(other)
            | self._diff_positional(other)
            | self._diff_keyword(other)
            | _lsp.check_return_variance(self.result, other.result)
        )

    def _diff_execution(self, other: SigSpec) -> LspViolation:
        violatoin: LspViolation = LspViolation.ZERO

        if self.is_async != other.is_async:
            violatoin |= LspViolation.SYNC_ASYNC_MISMATCH

        if self.is_generator != other.is_generator:
            violatoin |= LspViolation.GENERATOR_MISMATCH

        if self.binding != other.binding:
            violatoin |= LspViolation.DESCRIPTOR_BINDING_SHIFT

        return violatoin

    def _diff_positional(self, other: SigSpec) -> LspViolation:

        violation: LspViolation = LspViolation.ZERO
        _base_pos, _new_pos = self.positionals, other.positionals

        if other.min_positional > self.min_positional:
            violation |= LspViolation.INCREASED_MIN_POS
        if self.args and not other.args:
            violation |= LspViolation.DROPPED_VAR_POS
        elif (
            not self.args and not other.args and len(_new_pos) < len(_base_pos)
        ):
            violation |= LspViolation.REDUCED_MAX_POS

        for b_arg, n_arg in zip(self.pos, _new_pos, strict=True):
            if b_arg.name != n_arg.name:
                violation |= LspViolation.POS_ONLY_RENAMED
                break

        overlap: int = min(len(_base_pos), len(_new_pos))
        for i in range(overlap):
            violation |= _lsp.check_param_variance(
                _base_pos[i].annotation, _new_pos[i].annotation
            )

        if other.args is not None:
            for i in range(overlap, len(_base_pos)):
                violation |= _lsp.check_param_variance(
                    _base_pos[i].annotation, other.args[0].annotation
                )
            if self.args is not None:
                violation |= _lsp.check_param_variance(
                    self.args[0].annotation, other.args[0].annotation
                )

        return violation

    def _diff_keyword(self, other: SigSpec) -> LspViolation:
        violation: LspViolation = LspViolation.ZERO

        _base_kw, _new_kw = self.keyword_map, other.keyword_map
        new_pos_names: set[str] = {a.name for a in other.pos}
        base_both_names: set[str] = {a.name for a in self.both}
        new_key_names: set[str] = {a.name for a in other.key}

        if self.kwargs and not other.kwargs:
            violation |= LspViolation.DROPPED_VAR_KW

        for name, base_arg in _base_kw.items():
            if name in _new_kw:
                if name in base_both_names and name in new_key_names:
                    violation |= LspViolation.LOST_POS_ACCESS
                violation |= _lsp.check_param_variance(
                    base_arg.annotation, _new_kw[name].annotation
                )
            elif name in new_pos_names:
                violation |= LspViolation.LOST_KW_ACCESS
            elif other.kwargs is not None:
                violation |= _lsp.check_param_variance(
                    base_arg.annotation, other.kwargs[0].annotation
                )
            else:
                violation |= LspViolation.DROPPED_KW_NAME

        if self.kwargs is not None and other.kwargs is not None:
            violation |= _lsp.check_param_variance(
                self.kwargs[0].annotation, other.kwargs[0].annotation
            )

        _base_min = self.min_positional
        for idx, arg in enumerate(other.both):
            if (
                arg.name not in _base_kw
                and not arg.has_default
                and (len(self.pos) + idx) >= _base_min
            ):
                violation |= LspViolation.ADDED_REQUIRED_KW

        for arg in other.key:
            if arg.name not in _base_kw and not arg.has_default:
                violation |= LspViolation.ADDED_REQUIRED_KW

        return violation

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
            pos=tuple(*buckets[SigPart.POSARG]),
            both=tuple(*buckets[SigPart.ANYARG]),
            args=tuple(*buckets[SigPart.ARGS]),
            key=tuple(*buckets[SigPart.KEYARG]),
            kwargs=tuple(*buckets[SigPart.KWARGS]),
            result=reflect.sig.returns(hints, sig),
            is_async=reflect.sig.is_async(unwrapped),
            is_generator=reflect.sig.is_generator(unwrapped),
            binding=_binding,
            tolerance=tolerance,
        )
