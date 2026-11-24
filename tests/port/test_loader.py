"""Loader resolution and install order. Extraction itself is test_typearg.py."""

import pytest

from sstcore.port.empty import VOID
from sstcore.port.structures import Loader


def load_str() -> str:
    return "loaded"


def load_int(n: int) -> int:
    return n


def load_union() -> int | str:
    return "x"


def naked():
    return 1


class IntLoader(Loader[..., int]): ...


class SubIntLoader(IntLoader): ...


class OpenLoader[X](Loader[..., X]): ...


class ListLoader[X](Loader[..., list[X]]): ...


class IntListLoader(ListLoader[int]): ...


OPEN_X = OpenLoader.__type_params__[0]


@pytest.mark.parametrize(
    (
        "case",
        "loader",
        "value",
        "value_source",
        "parameters",
        "parameters_source",
    ),
    [
        ("bare", Loader(), VOID, "none", Ellipsis, "unknown"),
        ("subscript", Loader[..., int](), int, "generic", Ellipsis, "generic"),
        ("subclass", IntLoader(), int, "generic", Ellipsis, "generic"),
        ("deep", SubIntLoader(), int, "generic", Ellipsis, "generic"),
        ("open", OpenLoader(), OPEN_X, "unbound", Ellipsis, "generic"),
        (
            "open default",
            OpenLoader(default=5),
            int,
            "default",
            Ellipsis,
            "generic",
        ),
        (
            "substituted",
            IntListLoader(),
            list[int],
            "generic",
            Ellipsis,
            "generic",
        ),
        ("default", Loader(default=5), int, "default", Ellipsis, "unknown"),
        (
            "default zero",
            Loader(default=0),
            int,
            "default",
            Ellipsis,
            "unknown",
        ),
        (
            "default bool",
            Loader(default=True),
            bool,
            "default",
            Ellipsis,
            "unknown",
        ),
        (
            "default none",
            Loader(default=None),
            None,
            "default",
            Ellipsis,
            "unknown",
        ),
        ("func", Loader(load_str), str, "func", (), "func"),
        ("func args", Loader(load_int), int, "func", (int,), "func"),
        ("union func", Loader(load_union), int | str, "func", (), "func"),
        ("naked", Loader(naked), VOID, "none", (), "func"),
        (
            "func beats default",
            Loader(load_str, default=5),
            str,
            "func",
            (),
            "func",
        ),
        (
            "explicit beats both",
            IntLoader(load_str, default="nope"),  # ty:ignore
            int,
            "generic",
            Ellipsis,
            "generic",
        ),
    ],
)
def test_resolved_channels(
    case: str,
    loader: Loader,
    value: object,
    value_source: str,
    parameters: object,
    parameters_source: str,
) -> None:
    found = loader.type_args
    assert found.value == value, case
    assert found.value_source == value_source  # ty:ignore FIX:
    assert found.parameters == parameters
    assert found.parameters_source == parameters_source
    assert loader.target_type == value


@pytest.mark.parametrize(
    ("loader", "text"),
    [
        (Loader(), "Loader[(...), UnTyped]"),
        (Loader(default=5), "Loader[(...), int]"),
        (Loader(load_str), "Loader[(), str]"),
        (IntLoader(), "IntLoader[(...), int]"),
        (OpenLoader(), "OpenLoader[(...), X]"),
        (IntListLoader(), "IntListLoader[(...), list[int]]"),
    ],
)
def test_str_uses_resolved_pair(loader: Loader, text: str) -> None:
    assert str(loader) == text


def test_loaded_value_is_in_str() -> None:
    loader = Loader(load_str)
    loader()
    assert str(loader) == "Loader['loaded' :: (), str]"


def test_unused_channels_stay_on_the_spectrum() -> None:
    found = IntLoader(load_str, default="nope").type_args  # ty:ignore
    assert found.value is int
    assert found.func_return is str  # ty:ignore FIX:
    assert found.default_type is str  # ty:ignore FIX:
    assert "Pair" not in found.summary()
    assert "int" in found.summary()


@pytest.mark.parametrize(
    ("loader", "expected"),
    [
        (Loader(), False),
        (Loader(default=0), True),
        (Loader(default=VOID), False),
        (Loader(load_str), True),
    ],
)
def test_bool_means_configured(loader: Loader, expected: bool) -> None:
    assert bool(loader) is expected


def test_empty_value_raises() -> None:
    loader = Loader()
    with pytest.raises(LookupError):
        _ = loader.value
    with pytest.raises(LookupError):
        loader()


def test_void_from_func_falls_through_to_default() -> None:
    def nada() -> int:
        return VOID  # ty:ignore

    loader = Loader(nada, default=4, prefer="func")
    assert loader() == 4
    assert loader.reset() == 1


@pytest.mark.parametrize(
    ("prefer", "expected", "counted"),
    [
        ("func", 7, 1),
        ("default", 3, 0),
    ],
)
def test_prefer(prefer: str, expected: int, counted: int) -> None:
    def func() -> int:
        return 7

    loader = Loader(func, default=3, prefer=prefer)  # ty:ignore
    assert loader() == expected
    assert loader.reset() == counted


def test_call_does_not_count_install_does() -> None:
    loader = Loader(load_str)
    assert loader.call() == "loaded"
    assert loader.reset() == 0
    assert loader() == "loaded"
    assert loader.reset() == 1
    assert not loader.is_ready


def test_bind_resets_and_replaces() -> None:
    def other() -> str:
        return "other"

    loader = Loader(load_str)
    loader()
    returned = loader.bind(other)
    assert returned is other
    assert not loader.is_ready
    assert loader() == "other"


def test_clone_keeps_config_not_value() -> None:
    loader = Loader(load_str, default="d", prefer="default")
    assert loader() == "d"
    cloned = loader.clone()
    assert loader.is_ready
    assert not cloned.is_ready
    assert cloned() == "d"
