import pytest

from sstcore.forge.view import (
    Cli,
    Log,
    Repr,
    Rich,
    Str,
    ViewBuilder,
    ViewComposer,
    ViewInjector,
    view,
)
from sstcore.port.empty import ViewSentinel
from sstcore.port.event.dto import LogDTO, PanelDTO
from sstcore.port.raising import SstCoreError
from sstcore.port.represent import CliSerializable, LogSerializable


def test_empty_viewbuilder_defaults():
    """Empty ViewBuilder defaults all categories to OFF and filters sentinels."""
    builder = ViewBuilder()
    assert builder.cli is Cli.OFF
    assert builder.log is Log.OFF
    assert builder.repr is Repr.OFF
    assert builder.string is Str.OFF
    assert builder.rich is Rich.OFF
    assert builder.mixins == ()
    assert ViewSentinel not in builder.mixins


def test_viewbuilder_evolve():
    """ViewBuilder.evolve returns a new frozen instance with updated fields."""
    base = ViewBuilder(cli=Cli.PANEL)
    updated = base.evolve(log=Log.DATA, string=Str.SHORT)

    assert base.log is Log.OFF
    assert updated.cli is Cli.PANEL
    assert updated.log is Log.DATA
    assert updated.string is Str.SHORT
    assert len(updated.mixins) == 3


def test_viewinjector_plus_and_duplicate_error():
    """ViewInjector.plus updates categories and rejects duplicates in one call."""
    injector = ViewInjector().plus(Cli.PANEL, Log.DATA)
    assert injector.cli is Cli.PANEL
    assert injector.log is Log.DATA

    with pytest.raises(SstCoreError, match="Duplicated"):
        ViewInjector().plus(Cli.PANEL, Cli.LINE)


def test_view_invalid_target_raises():
    """Passing a non-class, non-MixinCatalog object to view() raises TypeError."""
    with pytest.raises(TypeError, match="expected a class or catalog specs"):
        view(123)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("specs", "expected_methods", "expected_str"),
    [
        (
            (Cli.PANEL, Str.NAME),
            {"__cli__", "__str__"},
            "SampleEntityView[test123]",
        ),
        (
            (Rich.SHORT, Log.DEBUG),
            {"__rich__", "__log__"},
            None,
        ),
        (
            (Cli.HEADER, Repr.DATA, Log.DATA),
            {"__cli__", "__repr__", "__log__"},
            None,
        ),
        (
            (Cli.PANEL, Str.SHORT, Rich.NAME, Repr.DEBUG, Log.DATA),
            {"__cli__", "__str__", "__rich__", "__repr__", "__log__"},
            "SampleEntityView",
        ),
    ],
)
def test_view_combinations(
    specs: tuple,
    expected_methods: set[str],
    expected_str: str | None,
):
    """Valid catalog combinations inject the expected mixin methods."""

    @view(*specs)
    class SampleEntity:
        name = "test123"
        value = 42

        def __init__(self) -> None:
            self.instance_val = 99

    obj = SampleEntity()
    cls = type(obj)

    assert cls.__name__ == "SampleEntityView"
    assert ViewSentinel not in cls.__mro__

    for method in expected_methods:
        assert hasattr(obj, method), f"Missing expected method {method}"

    if "__cli__" in expected_methods:
        assert isinstance(obj, CliSerializable)
        dto = obj.__cli__()
        assert isinstance(dto, PanelDTO)

    if "__str__" in expected_methods and expected_str is not None:
        assert expected_str in str(obj)

    if "__log__" in expected_methods:
        assert isinstance(obj, LogSerializable)
        log_dto = obj.__log__()
        assert isinstance(log_dto, LogDTO)

    if "__repr__" in expected_methods:
        rendered_repr = repr(obj)
        assert "SampleEntity" in rendered_repr


def test_compose_method_directly():
    """Standalone .compose() produces a pure mixin base class without target."""
    spec = ViewBuilder(cli=Cli.PANEL, repr=Repr.DEBUG)
    view_base = spec.compose(name="Demo")

    assert view_base.__name__ == "DemoView"
    assert len(spec.mixins) == 2

    default_base = spec.compose()
    assert default_base.__name__ == "ViewBase"

    instance = view_base()
    assert isinstance(instance, CliSerializable)
    assert ViewSentinel not in view_base.__mro__


def test_presets_attached_to_view():
    """ViewComposer exposes pre-configured ViewInjector presets."""
    assert isinstance(view, ViewComposer)
    assert isinstance(view.pydantic, ViewInjector)
    assert isinstance(view.printer, ViewInjector)
    assert isinstance(view.safe_typer, ViewInjector)
    assert isinstance(view.functor, ViewInjector)

    assert view.pydantic.cli is Cli.TABLE
    assert view.pydantic.log is Log.DATA
    assert view.printer.cli is Cli.HEADER
    assert view.safe_typer.cli is Cli.PANEL
    assert view.functor.repr is Repr.DATA
