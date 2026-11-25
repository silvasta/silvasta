"""
Utils

-
"""

__all__: list[str] = [
    "tuple_format",
    "format_named_value",
    "format_explain",
    "SpecParse",
]

import collections.abc as _cabc
import typing as _typing
from typing import Any

from ._zero import stringed

_VALID_FLAGS: frozenset[str] = frozenset("bivn")
_EXPLAIN_FLAGS: frozenset[str] = frozenset("bivnte")


#  LINE: -- Format -- -- - -- -- - -- -- - -- -- - -- -- - -- --


class _TupleFormat: ...


def tuple_format(self, spec: str, /) -> str:
    """
    Composable Format Mini-Language:

      'b' : bare (only joined content, no ClassName[icon|...] wrapper)
      'i' : icon-only wrapper ([icon|...] without ClassName)
      'v' : verbose (preserve child ClassName wrappers & raw reprs)
      'n' : newline separated (multiline pretty output)
      ';X': use 'X' as custom separator (e.g., f"{obj:b; | }")

    """
    parsed: SpecParse = SpecParse.read(spec)
    body: str = parsed.active_sep(fallback=self.sep).join(
        child.__format__(parsed.child_spec)
        if isinstance(child, _TupleFormat)
        else stringed(child, verbose=parsed.verbose)
        for child in self.joins()
    )
    if parsed.multiline and body:
        indented: str = "\n".join(f"  {line}" for line in body.splitlines())
        body = f"\n{indented}\n"

    return body if parsed.bare else _format_box(self, parsed.icon_only, body)


def _tuple_format(self: Any, spec: str, /) -> str:
    # CHECK:
    valid_flags: frozenset[str] = getattr(self, "format_flags", _VALID_FLAGS)
    parsed: SpecParse = SpecParse.read(spec, valid=valid_flags)

    def _format_child(child: Any, parsed: SpecParse) -> str:
        """Format nested formattable units with child_spec, or fallback to stringed."""
        if isinstance(child, FormattableUnit):
            return child.__format__(parsed.child_spec)
        return stringed(child, verbose=parsed.verbose)

    body: str = (
        custom_body(parsed)
        if (custom_body := getattr(self, "_format_body", None))
        else parsed.active_sep(fallback=self.sep).join(
            _format_child(child, parsed) for child in self.joins()
        )
    )

    if parsed.multiline and body and not parsed.bare:
        indented: str = "\n".join(f"  {line}" for line in body.splitlines())
        body = f"\n{indented}\n"

    return body if parsed.bare else _format_box(self, parsed.icon_only, body)


@_typing.runtime_checkable
class FormattableUnit(_typing.Protocol):
    icon: str
    sep: str

    def joins(self) -> _cabc.Iterator[Any]: ...


def format_named_value(self, spec: str) -> str:
    """Reduced Setup for NamedValue / Var"""
    parsed: SpecParse = SpecParse.read(spec)
    val_str: str = stringed(self.value, verbose=parsed.verbose)
    body = f"{self.name}{self.sep}{val_str}"
    return (
        body
        if parsed.bare and not parsed.verbose
        else _format_box(self, parsed.icon_only, body)
    )


def format_explain(self: Any, spec: str, /) -> str:
    """
    Composable Format Mini-Language for ExplainTuple:

      '' / 't' : title (collapsed to single-line unless 'n' is set)
      'e'      : extended detail only
      'v'      : verbose (title + detail)
      'n'      : multiline output (title followed by indented detail)
      'i'      : wrap in icon box ([ⓘ | ...])
      'b'      : bare (unboxed, also compatible with TupleControl child_spec)
      ';X'     : custom separator between parts
    """
    parsed: SpecParse = SpecParse.read(spec, valid=_EXPLAIN_FLAGS)
    line_sep: str = parsed.separator or " | "

    title: str = _collapse_or_multiline(
        self.title, multiline=parsed.multiline, sep=line_sep
    )
    detail: str = _collapse_or_multiline(
        self.detail, multiline=parsed.multiline, sep=line_sep
    )

    include_both: bool = (
        (parsed.verbose or (parsed.multiline and not parsed.title_only))
        and not parsed.explain_only
    ) or (parsed.title_only and parsed.explain_only)

    if parsed.explain_only and not parsed.title_only:
        body: str = detail
    elif include_both and detail:
        if parsed.multiline:
            indented: str = "\n".join(
                f"  {line}" for line in self.detail.splitlines()
            )
            body = f"{title}\n{indented}"
        else:
            sep: str = parsed.active_sep(fallback=getattr(self, "sep", " — "))
            body = f"{title}{sep}{detail}"
    else:
        body = title

    if parsed.icon_only:
        if parsed.multiline and body:
            indented_box = "\n".join(f"  {line}" for line in body.splitlines())
            body = f"\n{indented_box}\n"
        return _format_box(self, icon_only=True, body=body)

    return body


def _split_spec(spec) -> tuple[str, str]:
    return (
        (spec.split(";", 1) + [""])[:2]  #
        if ";" in spec
        else (spec, "")
    )


def _collapse_or_multiline(
    text: str, *, multiline: bool, sep: str = " | "
) -> str:
    """Collapse multiline composite text into single-line unless multiline (:n) is active."""
    if multiline or "\n" not in text:
        return text
    return sep.join(line.strip() for line in text.splitlines() if line.strip())


def _format_box(self, icon_only: bool, body: str) -> str:
    prefix: str = f"{self.icon} | " if self.icon else ""
    header: str = "" if icon_only else type(self).__name__
    return f"{header}[{prefix}{body}]"


class SpecParse(_typing.NamedTuple):
    bare: bool
    icon_only: bool
    verbose: bool
    multiline: bool

    title_only: bool = False
    explain_only: bool = False

    separator: str | None = None
    flags: frozenset[str] = frozenset()

    def __contains__(self, flag: object) -> bool:
        return isinstance(flag, str) and flag in self.flags

    def active_sep(self, fallback: str) -> str:
        if self.separator is not None:
            return self.separator
        return "\n" if self.multiline else fallback

    @property
    def child_spec(self) -> str:
        base: str = "v" if self.verbose else "b"
        return f"{base}n" if self.multiline else base

    @classmethod
    def read(
        cls,
        spec: str,
        /,
        *,
        valid: frozenset[str] = _VALID_FLAGS,
    ) -> SpecParse:
        """Parse Format Spec against allowed flag set."""
        _flags, _has_sep, _sep = spec.partition(";")
        if _unknown := (flag_set := frozenset(_flags)) - valid:
            raise ValueError(f"Unknown format: {''.join(sorted(_unknown))!r}")
        return cls(
            bare="b" in _flags,
            icon_only="i" in _flags,
            verbose="v" in _flags,
            multiline="n" in _flags,
            title_only="t" in _flags,
            explain_only="e" in _flags,
            flags=flag_set,
            separator=_sep if _has_sep else None,
        )

    @staticmethod
    def accepts(
        spec: str,
        /,
        *,
        valid: frozenset[str] = _EXPLAIN_FLAGS,
        exclude: frozenset[str] = frozenset("b"),
    ) -> bool:
        """Check if a format_spec uses valid target flags and/or custom separator."""
        if not spec:
            return False
        flags, has_sep, sep = spec.partition(";")
        return (
            bool(flags or (has_sep and sep)) and set(flags) <= valid - exclude
        )
