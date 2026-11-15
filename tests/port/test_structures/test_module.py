"""
Confirm the functionalities of the module path utils

-
"""

import math
from typing import Any

import pytest

from sstcore.port.structures._module import DotPath, ModulePath
from sstcore.util.path._module import ModuleArg, ModuleInput, ModuleSpec


class DummyClass:
    """Top-level helper class for identification and import tests."""

    def method(self) -> str:
        return "ok"

    @staticmethod
    def factory() -> int:
        return 42


# LINE: -- 1. Syntax & Parsing Tests -- -- - -- -- - -- -- - -- -- - -- -- - -- --


@pytest.mark.parametrize(
    ("raw", "allow_rel", "expected"),
    [
        ("package.module.sub", False, True),
        ("hello", False, True),
        (".module", False, False),
        (".module", True, True),
        ("..pkg.mod", True, True),
        ("...", True, False),
        ("", False, False),
        ("hello..", False, False),
        ("pkg.class.sub", False, False),  # 'class' is a Python keyword
        ("pkg.mod:Cls", False, False),  # ':' is not part of a pure dotpath
    ],
)
def test_is_dotpath(raw: str, allow_rel: bool, expected: bool) -> None:
    assert DotPath(raw, allow_relative=allow_rel) is expected


@pytest.mark.parametrize(
    ("raw", "kwargs", "expected"),
    [
        ("package.module.sub", {}, True),
        ("package.module.sub", {"require_attr": True}, False),
        ("package.module.sub:Cls", {"require_attr": True}, True),
        ("module:Cls.sub_attr", {"require_attr": True}, True),
        (".module:Cls", {"allow_relative": False}, False),
        (".module:Cls", {"allow_relative": True, "require_attr": True}, True),
        ("package:Cls:attr", {}, False),
        ("package.for:Cls", {}, False),
        ("hello..", {}, False),
    ],
)
def test_modulepath_accepts(
    raw: str, kwargs: dict[str, bool], expected: bool
) -> None:
    assert ModulePath.accepts(raw, **kwargs) is expected


def test_modulepath_properties_and_slicing() -> None:
    mp = ModulePath.parse("sstcore.port._private:MyCls.method")
    mod, qual = mp  # NamedTuple unpacking

    assert mod == "sstcore.port._private"
    assert qual == "MyCls.method"
    assert mp.project == "sstcore"
    assert mp.modules == ("sstcore", "port", "_private")
    assert mp.submodules == ("port", "_private")
    assert mp.public == "sstcore.port"
    assert mp.quals == ("MyCls", "method")
    assert mp.dotted == "sstcore.port._private.MyCls.method"
    assert str(mp) == "sstcore.port._private:MyCls.method"

    # Relative path slicing does not confuse first segment with project root
    rel = ModulePath.parse("..util._helper:Func", allow_relative=True)
    assert rel.is_relative is True
    assert rel.depth == 2
    assert rel.project == ""
    assert rel.submodules == ("util", "_helper")

    # Division & qualname mutation
    extended = mp / "sub" / ":"
    assert str(extended) == "sstcore.port._private.sub"


# LINE: -- 2. Object Identification Tests -- -- - -- -- - -- -- - -- -- - -- --


@pytest.mark.parametrize(
    ("obj", "expected_mod", "expected_qual"),
    [
        (math, "math", ""),
        (DummyClass, __name__, "DummyClass"),
        (DummyClass(), __name__, "DummyClass"),
        (DummyClass.method, __name__, "DummyClass.method"),
        (DummyClass().method, __name__, "DummyClass.method"),
        (
            ModulePath("a.b", "C"),
            "sstcore.port.structures._module",
            "ModulePath",
        ),
    ],
)
def test_modulepath_identify(
    obj: Any, expected_mod: str, expected_qual: str
) -> None:
    mp = ModulePath.identify(obj)
    assert mp.module == expected_mod
    assert mp.qualname == expected_qual


# LINE: -- 3. Resolution, Existence & Import Tests -- -- - -- -- - -- -- - -- --


def test_resolve_and_cwd() -> None:
    cwd = ModulePath.cwd()
    assert cwd.module != ""

    rel = ModulePath.parse("._dataclass:ArgSpec", allow_relative=True)
    resolved = rel.resolve("sstcore.port.structures")
    assert resolved == ModulePath(
        "sstcore.port.structures._dataclass", "ArgSpec"
    )
    assert resolved.importable() is True


def test_existence_and_lazy_loader() -> None:
    valid = ModulePath("math", "sqrt")
    missing_attr = ModulePath("math", "non_existent_func")
    missing_mod = ModulePath("non_existent_pkg_xyz", "Cls")

    assert valid.module_exists() is True
    assert valid.importable() is True

    assert missing_attr.module_exists() is True
    assert missing_attr.importable() is False

    assert missing_mod.module_exists() is False
    assert missing_mod.importable() is False

    # Lazy loader without calling vs with calling
    fn_loader = valid.lazy_loader(call_if_callable=False, ensure_exists=True)
    assert fn_loader() is math.sqrt

    factory_mp = ModulePath.identify(DummyClass.factory)
    val_loader = factory_mp.lazy_loader(
        call_if_callable=True, ensure_exists=True
    )
    assert val_loader() == 42

    with pytest.raises(ImportError):
        missing_attr.lazy_loader(ensure_exists=True)


# LINE: -- 4. ModuleSpec Parameterized Pipeline Tests -- -- - -- -- - -- -- - -- --


@pytest.mark.parametrize(
    ("arg", "expected", "options"),
    [
        (
            "sstcore.port.structures._module:ModulePath",
            ModulePath("sstcore.port.structures._module", "ModulePath"),
            {"require_attr": True, "must_exists": True},
        ),
        (
            "math",
            ModulePath("math", ""),
            {"module_exists": True, "must_exists": True},
        ),
        (
            "._module:ModulePath",
            ModulePath("._module", "ModulePath"),
            {"allow_relative": True, "require_attr": True},
        ),
        (
            "._module:ModulePath",
            ModulePath("sstcore.port.structures._module", "ModulePath"),
            {"resolve": True, "require_attr": True, "must_exists": True},
        ),
        (
            DummyClass,
            ModulePath(__name__, "DummyClass"),
            {"require_attr": True},
        ),
    ],
)
def test_modulespec_ok(
    arg: ModuleArg | Any,
    expected: ModulePath,
    options: ModuleInput,
) -> None:
    """Valid inputs and ModuleInput flag combinations normalize and validate cleanly."""
    assert ModuleSpec.ok(arg, **options) == expected


@pytest.mark.parametrize(
    ("arg", "options", "error_cls"),
    [
        ("math", {"require_attr": True}, ValueError),
        (".rel:Cls", {"allow_relative": False}, ValueError),
        ("unknown_pkg_xyz", {"module_exists": True}, ModuleNotFoundError),
        ("math:unknown_attr", {"must_exists": True}, ImportError),
    ],
)
def test_modulespec_validation_failures(
    arg: str,
    options: ModuleInput,
    error_cls: type[Exception],
) -> None:
    with pytest.raises(error_cls):
        ModuleSpec.ok(arg, **options)


def test_modulespec_from_path_rejects_objects() -> None:
    assert ModuleSpec.from_path("math:sqrt").validate() == ModulePath(
        "math", "sqrt"
    )
    with pytest.raises(TypeError):
        ModuleSpec.from_path(DummyClass)  # ty: ignore
