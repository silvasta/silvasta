from sstcore.utils.view import Cli, ViewBuilder, view


@view(ViewBuilder(cli=Cli.PANEL))
class B:
    name = "test"


def test_single_mixin_cli():
    b = B()
    dto = b.__cli__()  # ty:ignore
    assert "test" in dto.title
