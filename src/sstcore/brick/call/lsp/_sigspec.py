"""
Analyze the Signature of Callables (SigSpec & SigVar)

- Combine signature inspection, single-spec views and delegation
- Apply _lsp substitution rules and _algebra (set operations)

                      DependencyLevel.sstcore.brick.call.lsp[1.1:1]
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

from ....port._types import Types as _T  # noqa: N814
from ....port.empty import VOID, MayBe, MayNot
from ....port.primitives import TupleField
from ....port.primitives._tuples import _SigVar
from ....port.sigspect import LspViolation
from ... import reflect
from . import _algebra, _rules

EMPTY: type[_empty] = _empty

type Buckets = dict[_ParameterKind, list[SigVar]]
type SigVars = tuple[SigVar, ...]


class SigVar(_SigVar):
    """Normalized specification of a single signature parameter."""

    icon = TupleField[str]("λ")
    sep = TupleField[str](": ")

    def __new__(
        cls,
        name: str,
        kind: _ParameterKind,
        default: Any = VOID,
        annotation: Any = VOID,
    ) -> Self:
        _default: MayBe[Any] = VOID if default is EMPTY else default
        _annotation: MayBe[Any] = VOID if annotation is EMPTY else annotation
        return tuple.__new__(cls, (name, kind, _default, _annotation))

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
        """Return a copy of SigVar with updated attributes."""
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
        """Create from inspect.Parameter with optional overrides."""
        return cls(
            name=param.name,
            kind=param.kind,
            default=param.default if default is VOID else default,
            annotation=param.annotation if annotation is VOID else annotation,
        )


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

    #  LINE: -- Single-Spec Views (SigSpecing) -- -- - -- -- - -- --

    @property
    def positionals(self) -> SigVars:
        """All parameters addressable by position in index order."""
        return self.pos + self.both

    @property
    def keyword_map(self) -> dict[str, SigVar]:
        """All parameters addressable by keyword name."""
        return {arg.name: arg for arg in (*self.both, *self.key)}

    @property
    def both_indices(self) -> dict[str, int]:
        """Positional index lookup for positional-or-keyword parameters."""
        offset = len(self.pos)
        return {arg.name: offset + i for i, arg in enumerate(self.both)}

    @property
    def min_pos_only(self) -> int:
        """Count of required positional-only parameters."""
        return sum(1 for arg in self.pos if not arg.has_default)

    @property
    def min_positional(self) -> int:
        return sum(1 for arg in self.positionals if not arg.has_default)

    @property
    def max_positional(self) -> int | None:
        """Maximum positional arguments accepted, or None if *args exists."""
        return None if self.args else len(self.positionals)

    @property
    def all_params(self) -> SigVars:
        return self.pos + self.both + self.key

    @property
    def required(self) -> SigVars:
        return tuple(p for p in self.all_params if not p.has_default)

    @property
    def has_var_positional(self) -> bool:
        return bool(self.args)

    @property
    def has_var_keyword(self) -> bool:
        return bool(self.kwargs)

    #  LINE: -- LSP Façade -- -- - -- -- - -- -- - -- -- - -- -- - -- --

    def allows(
        self, other: SigSpec, tolerance: MayNot[LspViolation] = None
    ) -> bool:
        """Check whether Other may substitute Self under Tolerance"""
        limit: LspViolation = self.tolerance if tolerance is None else tolerance
        return _rules.allows(base=self, new=other, tolerance=limit)

    def diff(
        self, other: SigSpec, *, ignore: LspViolation = LspViolation.ZERO
    ) -> LspViolation:
        """Compute all LSP violations when replacing Self with Other"""
        return _rules.evaluate(base=self, new=other, ignore=ignore)

    #  LINE: -- Algebraic & Comparison Operators -- -- - -- -- - -- --

    def __sub__(self, other: Self) -> Self:
        """Compute structural capability difference (left - right)"""
        return (
            NotImplemented
            if not isinstance(other, SigSpec)
            else _algebra.subtract(left=self, right=other)
        )

    def __and__(self, other: Self) -> Self:
        """Compute structural capability intersection (left & right)"""
        return (
            NotImplemented
            if not isinstance(other, SigSpec)
            else _algebra.intersect(left=self, right=other)
        )

    def __or__(self, other: Self) -> Self:
        """Compute structural capability union (left | right)"""
        return (
            NotImplemented
            if not isinstance(other, SigSpec)
            else _algebra.union(left=self, right=other)
        )

    def ___rshift__(self, other: Self | Callable[..., Any]) -> LspViolation:
        """Evaluate LSP violations when replacing `self` with `other`."""
        return (
            NotImplemented
            if (target := self._coerce(other)) is None
            else self.diff(target)
        )

    def __lshift__(self, other: Self | Callable[..., Any]) -> LspViolation:
        """Evaluate LSP violations when replacing `other` with `self`."""
        return (
            NotImplemented
            if (target := self._coerce(other)) is None
            else target.diff(self)
        )

    def __contains__(self, other: object) -> bool:
        """Return whether `other` is a valid replacement under tolerance."""
        return (
            False
            if (target := self._coerce(other)) is None
            else self.allows(target)
        )

    def __ge__(self, other: Self | Callable[..., Any]) -> bool:
        """Does `self` allow `other` as a substitute? (self >= other)"""
        return (
            NotImplemented
            if (target := self._coerce(other)) is None
            else self.allows(target)
        )

    def ___le__(self, other: Self | Callable[..., Any]) -> bool:
        """Is `self` a valid substitute for `other`? (self <= other)"""
        return (
            NotImplemented
            if (target := self._coerce(other)) is None
            else target.allows(
                self,
                tolerance=target.tolerance
                if isinstance(other, SigSpec)
                else self.tolerance,
            )
        )

    def __gt__(self, other: Self | Callable[..., Any]) -> bool:
        """Does `self` strictly allow `other` (asymmetric preorder)?"""
        return (
            NotImplemented
            if (target := self._coerce(other)) is None
            else (
                self.allows(other=target, tolerance=self.tolerance)
                and not target.allows(self, tolerance=self.tolerance)
            )
        )

    def __lt__(self, other: Self | Callable[..., Any]) -> bool:
        """Is `self` a strict substitute for `other` (asymmetric preorder)?"""
        if (target := self._coerce(other)) is None:
            return NotImplemented
        tol = target.tolerance if isinstance(other, SigSpec) else self.tolerance

        return target.allows(self, tolerance=tol) and not self.allows(
            target, tolerance=tol
        )

    def ___lt__(self, other: Self | Callable[..., Any]) -> bool:
        """Is `self` a strict substitute for `other` (asymmetric preorder)?"""
        return (
            NotImplemented
            if (target := self._coerce(other)) is None
            else target.allows(
                self,
                tolerance=(
                    tol := target.tolerance
                    if isinstance(other, SigSpec)
                    else self.tolerance
                ),
            )
            and not self.allows(target, tolerance=tol)
        )

    #  LINE: -- Transformations & Inspection -- -- - -- -- - -- --

    def bind_self(self) -> Self:
        """Return a new SigSpec with leading receiver (self/cls) bound"""
        if self.pos:
            return replace(self, pos=self.pos[1:])
        if self.both:
            return replace(self, both=self.both[1:])
        if self.args:
            return self
        raise TypeError(
            "Cannot bind receiver (self/cls) to signature,"
            f"got 0 positional parameters: {self}"
        )

    def evolve(
        self,
        is_async: MayNot[bool] = None,
        is_generator: MayNot[bool] = None,
        binding: MayNot[reflect.sig.Binding] = None,
        tolerance: MayNot[LspViolation] = None,
    ) -> Self:
        """Copy the Spec to a new configuration with the same SigVars."""
        return replace(
            self,
            is_async=self.is_async if is_async is None else is_async,
            is_generator=(
                self.is_generator if is_generator is None else is_generator
            ),
            binding=self.binding if binding is None else binding,
            tolerance=self.tolerance if tolerance is None else tolerance,
        )

    @classmethod
    def _coerce(cls, other: object) -> MayNot[Self]:
        match other:
            case cls():
                return other
            case _ if isinstance(sig := getattr(other, "signature", None), cls):
                return sig
            case _ if callable(other):
                return cls.detect(other)
            case _:
                return None

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
        """Inspect a callable and build a normalized SigSpec."""
        _binding = reflect.sig.Binding.detect(target)
        raw: Callable[..., Any] = _binding.raw(target)
        unwrapped: Callable[..., Any] = _inspect.unwrap(raw)
        sig: Signature = _inspect.signature(raw)
        hints: _T.StrDict = reflect.typehint.find(
            unwrapped, include_extras=include_extras
        )

        buckets: Buckets = {part: [] for part in _ParameterKind}
        for param in sig.parameters.values():
            resolved: Any = hints.get(param.name, param.annotation)
            arg = SigVar.detect(param, annotation=resolved)
            buckets[arg.kind].append(arg)

        spec = cls(
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
        if (
            bind_to_self and _binding is not reflect.sig.Binding.STATIC
        ) or _binding is reflect.sig.Binding.METHOD:
            return spec.bind_self()
        return spec
