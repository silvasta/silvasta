"""
Analyze the Signature of Callables

-
"""

__all__: list[str] = [
    "SigVar",
    "SigSpec",
]

import inspect as _inspect
from collections.abc import Callable
from dataclasses import dataclass, replace
from inspect import Parameter, Signature, _empty, _ParameterKind
from typing import Any, Self

from ...port._types import Types as _T  # noqa:N814
from ...port.casting import LspViolation
from ...port.empty import VOID, MayBe, MayNot
from ...port.primitives import TupleField
from ...port.primitives._tuples import _SigVar
from .. import reflect
from . import _lsp

EMPTY: type[_empty] = _empty


type Buckets = dict[_ParameterKind, list[SigVar]]
type SigVars = tuple[SigVar, ...]


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

    #  LINE: -- Algebraic Operators -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def __sub__(self, other: Self) -> Self:
        """
        Compute structural capability difference (self - other)

        Parameters in `self.both` hold {POS(i), KEY(name)} capabilities:
        - If `other` only has POS(i), the difference retains KEY(name) in `key`.
        - If `other` only has KEY(name), the difference retains POS(i) in `pos`.
        - If `other` has neither, the parameter remains in `both`.
        """
        if not isinstance(other, SigSpec):
            return NotImplemented

        other_pos_len: int = len(other.positionals)
        other_kw: dict[str, SigVar] = other.keyword_map

        diff_pos: list[SigVar] = [
            arg for i, arg in enumerate(self.pos) if i >= other_pos_len
        ]
        diff_both: list[SigVar] = []
        diff_key: list[SigVar] = []

        base_pos_len: int = len(self.pos)
        for offset, arg in enumerate(self.both):
            idx: int = base_pos_len + offset
            has_pos: bool = idx < other_pos_len
            has_key: bool = arg.name in other_kw

            if not has_pos and not has_key:
                diff_both.append(arg)
            elif not has_pos and has_key:
                diff_pos.append(arg.evolve(kind=_ParameterKind.POSITIONAL_ONLY))
            elif has_pos and not has_key:
                diff_key.append(arg.evolve(kind=_ParameterKind.KEYWORD_ONLY))

        for arg in self.key:
            if arg.name not in other_kw:
                diff_key.append(arg)

        diff_args: SigVars = self.args if (self.args and not other.args) else ()
        diff_kwargs: SigVars = (
            self.kwargs if (self.kwargs and not other.kwargs) else ()
        )
        diff_result: Any = (
            VOID
            if reflect.types.is_subtype(other.result, self.result)
            else self.result
        )

        return replace(
            self,
            pos=tuple(diff_pos),
            both=tuple(diff_both),
            args=diff_args,
            key=tuple(diff_key),
            kwargs=diff_kwargs,
            result=diff_result,
        )

    def __and__(self, other: Self) -> Self:
        """
        Compute structural capability intersection (self & other)

        Parameters in `self.both` hold {POS(i), KEY(name)} capabilities:
        - If `other` has both POS(i) and KEY(name), it remains in `both`.
        - If `other` only has POS(i), it demotes to `pos` (POSITIONAL_ONLY).
        - If `other` only has KEY(name), it demotes to `key` (KEYARG).
        """
        if not isinstance(other, SigSpec):
            return NotImplemented

        other_pos_len: int = len(other.positionals)
        other_kw: dict[str, SigVar] = other.keyword_map

        and_pos: list[SigVar] = [
            arg for i, arg in enumerate(self.pos) if i < other_pos_len
        ]
        and_both: list[SigVar] = []
        and_key: list[SigVar] = []

        base_pos_len: int = len(self.pos)
        for offset, arg in enumerate(self.both):
            idx: int = base_pos_len + offset
            has_pos: bool = idx < other_pos_len
            has_key: bool = arg.name in other_kw

            if has_pos and has_key:
                and_both.append(arg)
            elif has_pos and not has_key:
                and_pos.append(arg.evolve(kind=_ParameterKind.POSITIONAL_ONLY))
            elif not has_pos and has_key:
                and_key.append(arg.evolve(kind=_ParameterKind.KEYWORD_ONLY))

        for arg in self.key:
            if arg.name in other_kw:
                and_key.append(arg)

        and_args: SigVars = self.args if (self.args and other.args) else ()
        and_kwargs: SigVars = (
            self.kwargs if (self.kwargs and other.kwargs) else ()
        )

        if reflect.types.is_subtype(self.result, other.result):
            and_result: Any = self.result
        elif reflect.types.is_subtype(other.result, self.result):
            and_result: Any = other.result
        else:
            and_result: VOID = VOID

        return replace(
            self,
            pos=tuple(and_pos),
            both=tuple(and_both),
            args=and_args,
            key=tuple(and_key),
            kwargs=and_kwargs,
            result=and_result,
        )

    def __or__(self, other: Self) -> Self:
        """Compute structural capability union (self | other)."""
        if not isinstance(other, SigSpec):
            return NotImplemented

        rem: SigSpec = other - self
        return replace(
            self,
            pos=self.pos + rem.pos,
            both=self.both + rem.both,
            args=self.args or other.args,
            key=self.key + rem.key,
            kwargs=self.kwargs or other.kwargs,
            result=other.result if self.result is VOID else self.result,
        )

    def __rshift__(self, other: Self | Callable[..., Any]) -> LspViolation:
        """Evaluate LSP violations when replacing `self` with `other` (self >> other)."""
        target: MayNot[SigSpec] = self._coerce(other)
        if target is None:
            return NotImplemented
        return self.diff(target)

    def __lshift__(self, other: Self | Callable[..., Any]) -> LspViolation:
        """Evaluate LSP violations when replacing `other` with `self` (self << other)."""
        target: MayNot[SigSpec] = self._coerce(other)
        if target is None:
            return NotImplemented
        return target.diff(self)

    def __contains__(self, other: object) -> bool:
        """Is the incoming SigSpec or Callable a valid replacement? (under self.tolerance)"""
        target: MayNot[SigSpec] = self._coerce(other)
        return False if target is None else self.allows(target)

    def __ge__(self, other: Self | Callable[..., Any]) -> bool:
        """Does `self` allow `other` as a substitute? (self >= other)"""
        target: MayNot[SigSpec] = self._coerce(other)
        if target is None:
            return NotImplemented
        return self.allows(target)

    def __le__(self, other: Self | Callable[..., Any]) -> bool:
        """Is `self` a valid substitute for `other`? (self <= other)"""
        target: MayNot[SigSpec] = self._coerce(other)
        if target is None:
            return NotImplemented
        return target.allows(self)

    def __gt__(self, other: Self | Callable[..., Any]) -> bool:
        """Does `self` strictly allow `other` while differing from `other`?"""
        target: MayNot[SigSpec] = self._coerce(other)
        if target is None:
            return NotImplemented
        return self != target and self.allows(target)

    def __lt__(self, other: Self | Callable[..., Any]) -> bool:
        """Is `self` a strict substitute for `other` while differing from `other`?"""
        target: MayNot[SigSpec] = self._coerce(other)
        if target is None:
            return NotImplemented
        return self != target and target.allows(self)

    @classmethod
    def _coerce(cls, other: object) -> MayNot[Self]:
        match other:
            case cls():
                return other
            case _ if callable(other):
                return cls.detect(other)
            case _:
                return None

    #  LINE: -- LSP Evaluation -- -- - -- -- - -- -- - -- -- - -- --
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
        violation: LspViolation = LspViolation.ZERO

        if self.is_async != other.is_async:
            violation |= LspViolation.SYNC_ASYNC_MISMATCH

        if self.is_generator != other.is_generator:
            violation |= LspViolation.GENERATOR_MISMATCH

        if self.binding != other.binding:
            violation |= LspViolation.DESCRIPTOR_BINDING_SHIFT

        return violation

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

        for b_arg, n_arg in zip(self.pos, _new_pos, strict=False):
            if b_arg.name != n_arg.name:
                violation |= LspViolation.POS_ONLY_RENAMED
                break

        overlap: int = min(len(_base_pos), len(_new_pos))
        for i in range(overlap):
            violation |= _lsp.check_param_variance(
                _base_pos[i].annotation, _new_pos[i].annotation
            )

        if other.args:
            for i in range(overlap, len(_base_pos)):
                violation |= _lsp.check_param_variance(
                    _base_pos[i].annotation, other.args[0].annotation
                )
            if self.args:
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
            elif other.kwargs:
                violation |= _lsp.check_param_variance(
                    base_arg.annotation, other.kwargs[0].annotation
                )
            else:
                violation |= LspViolation.DROPPED_KW_NAME

        if self.kwargs and other.kwargs:
            violation |= _lsp.check_param_variance(
                self.kwargs[0].annotation, other.kwargs[0].annotation
            )

        _base_min: int = self.min_positional
        for idx, arg in enumerate(other.both):
            if (
                arg.name not in _base_kw
                and not arg.has_default
                and (len(other.pos) + idx) >= _base_min
            ):
                violation |= LspViolation.ADDED_REQUIRED_KW

        for arg in other.key:
            if not arg.has_default and (
                arg.name not in _base_kw or _base_kw[arg.name].has_default
            ):
                violation |= LspViolation.ADDED_REQUIRED_KW

        return violation

    #  LINE: -- Transformations & Inspection -- -- - -- -- - -- --

    def bind_self(self) -> Self:
        """Return a new SigSpec with the leading receiver parameter (self/cls) bound."""
        if self.pos:
            return replace(self, pos=self.pos[1:])
        if self.both:
            return replace(self, both=self.both[1:])
        if self.args:
            return self
        raise TypeError(
            f"Cannot bind receiver (self/cls) to signature with 0 positional parameters: {self}"
        )

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
        /,
        *,
        bind_to_self: bool = False,
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
        # REMOVE:
        # buckets: Buckets = _ParameterKind.buckets(hints, sig)

        # AI_TASK: is it that easy?
        # - still I need the modification of all _ParameterKind.POSITIONAL_ONLY etc
        buckets: Buckets = {part: [] for part in _inspect._ParameterKind}
        for param in sig.parameters.values():
            resolved: Any = hints.get(param.name, param.annotation)
            arg: SigVar = SigVar.detect(param, annotation=resolved)
            buckets[arg.kind].append(arg)

        spec: Self = cls(
            pos=tuple(buckets[_ParameterKind.POSITIONAL_ONLY]),
            both=tuple(buckets[_ParameterKind.POSITIONAL_OR_KEYWORD]),
            args=tuple(buckets[_ParameterKind.VAR_POSITIONAL]),
            key=tuple(buckets[_ParameterKind.KEYWORD_ONLY]),
            kwargs=tuple(buckets[_ParameterKind.VAR_KEYWORD]),
            result=reflect.sig.returns(hints, sig),
            is_async=reflect.sig.is_async(unwrapped),
            is_generator=reflect.sig.is_generator(unwrapped),
            binding=_binding,
            tolerance=tolerance,
        )
        if bind_to_self and _binding is not reflect.sig.Binding.METHOD:
            return spec.bind_self()
        return spec


#  LINE: -- Param Data  -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class SigVar(_SigVar):  # TODO: TupleBase?
    """Define the Spec of 1 Signature Part: Parameter or Return"""

    icon = TupleField[str]("λ")
    sep = TupleField[str](": ")

    def __new__(
        cls,
        name: str,
        kind: _ParameterKind,
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

    def evolve(
        self,
        *,
        name: MayNot[str] = None,
        kind: MayNot[_ParameterKind] = None,
        default: Any = EMPTY,
        annotation: Any = EMPTY,
    ) -> Self:
        """Return a copy of SigVar with updated attributes"""
        return type(self)(
            name=self.name if name is None else name,
            kind=self.kind if kind is None else kind,
            default=self.default if default is EMPTY else default,
            annotation=self.annotation if annotation is EMPTY else annotation,
        )

    @classmethod
    def detect(
        cls, param: Parameter, default: Any = VOID, annotation: Any = VOID
    ) -> Self:
        """Create from Parameter and update with additional values"""
        return cls(
            name=param.name,
            kind=param.kind,
            default=param.default if default is VOID else default,
            annotation=param.annotation if annotation is VOID else annotation,
        )
