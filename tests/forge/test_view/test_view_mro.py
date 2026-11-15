from sstcore.forge.view import (
    Cli,
    Log,
    Repr,
    Rich,
    Str,
    ViewBuilder,
    view,
    views,
)
from sstcore.port.empty import ViewSentinel
from sstcore.port.represent import (
    CliSerializable,
    LogSerializable,
    RichView,
    SstFullView,
    is_renderable,
    is_richable,
    is_serializable,
)


@view(Cli.LINE, Str.SHORT, Log.DATA, Repr.BOX, Rich.SHORT)
class FullDecorated:
    pass


def test_multiple_mixins_mro():
    """Decorated class MRO contains exact catalog mixins before base class."""
    instance = FullDecorated()
    mro = type(instance).__mro__

    assert views.cli.LineMixin in mro
    assert views.string.SimpleNameMixin in mro
    assert views.log.LogDataMixin in mro
    assert views.repr.ReprMixin in mro
    assert views.rich.SimpleRichNameMixin in mro
    assert ViewSentinel not in mro

    # Mixins are prepended before the original class by default
    line_idx = mro.index(views.cli.LineMixin)
    log_idx = mro.index(views.log.LogDataMixin)
    assert line_idx < log_idx


def test_inject_prepend_order():
    """ViewBuilder.inject respects prepend=True vs prepend=False in MRO."""

    class Base:
        pass

    builder = ViewBuilder(cli=Cli.PANEL, string=Str.SHORT)

    prepended_cls = builder.inject(Base, prepend=True)
    appended_cls = builder.inject(Base, prepend=False)

    prep_mro = prepended_cls.__mro__
    app_mro = appended_cls.__mro__

    assert prep_mro.index(views.cli.PanelMixin) < prep_mro.index(Base)
    assert app_mro.index(Base) < app_mro.index(views.cli.PanelMixin)


def test_represent_protocols_and_type_guards():
    """Verify runtime protocol conformance and represent type guards."""
    instance = FullDecorated()

    assert isinstance(instance, CliSerializable)
    assert isinstance(instance, LogSerializable)
    assert isinstance(instance, RichView)
    assert is_serializable(instance)
    assert is_renderable(instance)
    assert is_richable(instance)

    for method in ("__cli__", "__log__", "__repr__", "__str__", "__rich__"):
        assert hasattr(SstFullView, method)
        assert hasattr(instance, method)
