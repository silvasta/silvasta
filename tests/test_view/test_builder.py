import pytest
from pydantic import BaseModel

from sstcore.contract.cli import CliRenderable, LineDTO, PanelDTO
from sstcore.contract.log import LogDTO, LogSerializable
from sstcore.utils.view import ViewBuilder, view
from sstcore.utils.view.registry import Cli, Log, Repr, Rich, Str


def test_empty_viewbuilder_raises():
    """ViewBuilder requires at least one concrete Mixin (OFF → Sentinel)."""
    msg = "Select at least 1 Mixin for ViewBuilder!"
    with pytest.raises(ValueError, match=msg):
        ViewBuilder()  # all defaults = all OFF

    with pytest.raises(ValueError, match=msg):
        ViewBuilder(
            cli=Cli.OFF, str=Str.OFF, rich=Rich.OFF, repr=Repr.OFF, log=Log.OFF
        )


@pytest.mark.parametrize(
    "spec,expected_methods,test_str_content",
    [
        (
            ViewBuilder(cli=Cli.PANEL, str=Str.DEFAULT),
            {"__cli__", "__str__"},
            "test123",
        ),
        (
            ViewBuilder(rich=Rich.DEFAULT, log=Log.FULL),
            {"__rich__", "__log__"},
            None,
        ),
        (
            ViewBuilder(cli=Cli.LINE, repr=Repr.DEFAULT, log=Log.PYDANTIC),
            {"__cli__", "__repr__", "__log__"},
            "TestEntity",
        ),
        (
            ViewBuilder(
                cli=Cli.PANEL,
                str=Str.SHORT,
                rich=Rich.SHORT,
                repr=Repr.FULL,
                log=Log.DEFAULT,
            ),
            {"__cli__", "__str__", "__rich__", "__repr__", "__log__"},
            "test123",
        ),
    ],
)
def test_view_combinations(spec, expected_methods, test_str_content):
    """Test that valid combinations correctly inject mixins and behavior."""

    @view(spec)
    class TestEntity:
        name = "test123"
        value = 42

    obj = TestEntity()
    cls = type(obj)

    # Core guarantees
    assert hasattr(obj, "__view_spec__")
    assert obj.__view_spec__ is spec
    assert not any("MixinSentinel" in b.__name__ for b in cls.__mro__)

    # Method injection
    for method in expected_methods:
        assert hasattr(obj, method), f"Missing expected method {method}"

    # Behavior checks
    if "__cli__" in expected_methods:
        dto = obj.__cli__()  # type: ignore
        assert isinstance(dto, (PanelDTO, LineDTO))

    if "__str__" in expected_methods and test_str_content:
        s = str(obj)
        assert test_str_content in s or "TestEntity" in s

    if "__log__" in expected_methods:
        assert isinstance(obj.__log__(), LogDTO)  # type: ignore

    if "__repr__" in expected_methods:
        r = repr(obj)
        assert "TestEntity" in r
        if "FULL" in str(spec.repr):  # rough heuristic
            assert "value=42" in r


def test_pydantic_compatibility():
    """Pydantic models should survive composition with model_config + rebuild."""
    spec = ViewBuilder(cli=Cli.PANEL, log=Log.PYDANTIC, str=Str.DEFAULT)

    @view(spec)
    class TestModel(BaseModel):
        name: str = "pydantic-test"
        value: int = 42

    obj = TestModel()
    assert isinstance(obj.__log__(), LogDTO)  # type: ignore
    assert "pydantic-test" in str(obj)
    assert obj.model_dump()["name"] == "pydantic-test"

    # Model features should still work
    validated = TestModel.model_validate({"name": "updated", "value": 99})
    assert validated.name == "updated"
    assert hasattr(validated, "__cli__")
    assert hasattr(validated, "__view_spec__")


def test_mro_and_protocols():
    """Verify mixin ordering, protocol compliance, and sentinel filtering."""
    spec = ViewBuilder(cli=Cli.LINE, str=Str.SHORT, log=Log.DEFAULT)

    @view(spec)
    class Test: ...

    obj = Test()
    mro_names = [b.__name__ for b in type(obj).__mro__]

    assert any("CliLineMixin" in name for name in mro_names)
    assert any("NameMixin" in name for name in mro_names)  # from string
    assert any("LogMixin" in name for name in mro_names)
    assert "MixinSentinel" not in mro_names

    assert isinstance(obj, CliRenderable)
    assert isinstance(obj, LogSerializable)


def test_build_method_directly():
    """Standalone `.build()` should produce a usable base class."""
    spec = ViewBuilder(cli=Cli.LINE, repr=Repr.FULL)
    view_base = spec.build("Demo")

    assert view_base.__name__ == "DemoViewBase"
    assert len(spec.mixins) == 2

    instance = view_base()
    assert hasattr(instance, "__cli__")
    assert hasattr(instance, "__repr__")
    assert not any("MixinSentinel" in b.__name__ for b in view_base.__mro__)
