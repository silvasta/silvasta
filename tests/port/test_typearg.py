"""Runtime generic-argument extraction. No Loader policy here."""

from typing import Generic

import pytest

from sstcore.brick.reflect.___typearg import (
    GenericSpec,
    extract_type_args,
    format_parameters,
    format_type_arg,
    is_concrete_type,
    is_type_parameter,
    preserves_generic_alias_on_instance,
)
from sstcore.port.empty import VOID


class Pair[**P, T]: ...


class IntPair(Pair[..., int]): ...


class SubIntPair(IntPair): ...


class Open[X](Pair[..., X]): ...


class Boxed[X](Pair[..., list[X]]): ...


class IntBox(Boxed[int]): ...


class Either[X](Pair[..., X | None]): ...


class IntEither(Either[int]): ...


class Keyed(Pair[[int, str], bool]): ...


class OneArg(Pair[[int], str]): ...


class Nullary(Pair[[], bytes]): ...


OPEN_X = Open.__type_params__[0]


def declared(
    specs: tuple[GenericSpec, ...], origin: type
) -> GenericSpec | None:
    for spec in specs:
        if spec.is_to_declare(origin):
            return spec
    return None


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (int, False),
        (OPEN_X, True),
        (Ellipsis, False),
        (VOID, False),
        ((int, str), False),
    ],
)
def test_is_type_parameter(value: object, expected: bool) -> None:
    assert is_type_parameter(value) is expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (int, True),
        (int | str, True),
        (None, True),
        ((int, str), True),
        (list[int], True),
        (VOID, False),
        (Ellipsis, False),
        (OPEN_X, False),
        ((int, OPEN_X), False),
    ],
)
def test_is_concrete_type(value: object, expected: bool) -> None:
    assert is_concrete_type(value) is expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (VOID, "VOID"),
        (Ellipsis, "..."),
        (None, "None"),
        (int, "int"),
        ((int, str), "(int, str)"),
        (list[int], "list[int]"),
        (int | None, "int | None"),
        (OPEN_X, "X"),
    ],
)
def test_format_type_arg(value: object, expected: str) -> None:
    assert format_type_arg(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (Ellipsis, "(...)"),
        (VOID, "(...)"),
        ((), "()"),
        ((int, str), "(int, str)"),
        ((int,), "(int)"),
    ],
)
def test_format_parameters(value: object, expected: str) -> None:
    assert format_parameters(value) == expected


@pytest.mark.parametrize(
    ("case", "target", "tee", "pee"),
    [
        ("alias", Pair[..., int], int, Ellipsis),
        ("subclass", IntPair(), int, Ellipsis),
        ("subclass class", IntPair, int, Ellipsis),
        ("deep", SubIntPair(), int, Ellipsis),
        ("substituted", IntBox(), list[int], Ellipsis),
        ("union subst", IntEither(), int | None, Ellipsis),
        ("param list", Keyed(), bool, (int, str)),
        ("one param", OneArg(), str, (int,)),
        ("empty params", Nullary(), bytes, ()),
    ],
)
def test_extract_specialization(
    case: str, target: object, tee: object, pee: object
) -> None:
    spec = declared(extract_type_args(target), Pair)
    assert spec is not None, case
    assert spec.get("T") == tee
    assert spec.get("P") == pee
    assert spec.explicit is True
    assert spec.aligned is True


def test_open_parameter_is_the_subclass_typevar() -> None:
    spec = declared(extract_type_args(Open()), Pair)
    assert spec is not None
    assert spec.get("T") is OPEN_X
    assert spec.get("P") is Ellipsis
    assert str(spec) == "Pair[(...), X]"


def test_unspecialized_is_implicit_identity() -> None:
    specs = extract_type_args(Pair())
    assert declared(specs, Pair) is None
    assert specs[-1].origin is Pair
    assert specs[-1].explicit is False
    assert specs[-1].get("T") is Pair.__type_params__[-1]
    assert not any(spec.origin is Generic for spec in specs)


def test_most_specific_origin_comes_first() -> None:
    origins = [
        spec.origin for spec in extract_type_args(IntBox()) if spec.explicit
    ]
    assert origins[0] is Boxed
    assert origins.index(Boxed) < origins.index(Pair)


def test_missing_name_is_void() -> None:
    spec = declared(extract_type_args(IntPair()), Pair)
    assert spec is not None
    assert spec.get("nope") is VOID


def test_direct_instance_subscript_is_version_dependent() -> None:
    spec = declared(extract_type_args(Pair[..., int]()), Pair)
    if preserves_generic_alias_on_instance():
        assert spec is not None
        assert spec.get("T") is int
    else:
        assert spec is None


def test_aligned_spec_string_has_no_question_mark() -> None:
    spec = declared(extract_type_args(IntPair()), Pair)
    assert spec is not None
    assert str(spec) == "Pair[(...), int]"
