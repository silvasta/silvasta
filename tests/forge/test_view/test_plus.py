from sstcore.forge.view import Cli, Str, ViewInjector


def test_plus_updates_spec():
    base = ViewInjector(Cli.PANEL)
    updated = base.plus(Cli.DEBUG)

    assert base.cli == Cli.PANEL  # оригинал не меняется
    assert updated.cli == Cli.DEBUG


def test_plus_multiple():
    base = ViewInjector()
    updated = base.plus(Cli.HEADER, Str.MODULE)

    assert updated.cli == Cli.HEADER
    assert updated.string == Str.MODULE
