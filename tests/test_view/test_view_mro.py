from sstcore.utils.view import Cli, Log, Str, ViewBuilder, view
from sstcore.utils.view.mixin.cli import CliLineMixin
from sstcore.utils.view.mixin.log import LogMixin
from sstcore.utils.view.mixin.string import SimpleNameMixin


@view(ViewBuilder(cli=Cli.LINE, str=Str.SHORT, log=Log.DEFAULT))
class M:
    pass


def test_multiple_mixins_mro():
    m = M()
    bases = type(m).__mro__
    assert CliLineMixin in bases
    assert SimpleNameMixin in bases
    assert LogMixin in bases
