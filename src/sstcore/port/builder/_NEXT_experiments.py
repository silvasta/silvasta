from ...bricks.view import Cli, Log, Repr, Rich, Str, ViewBuilder, view
from ..view import CliRenderable


@view(Log.DATA, Repr.DEBUG, Cli.PANEL, Rich.NAME, Str.MODULE)
class Full: ...


class AnyView:
    def __str__(self):
        return "hello"


@view(Cli.HEADER, Rich.MODULE, Rich.NAME).plus(AnyView)
class Extended:
    x = 3


test1 = view(Cli.HEADER, Rich.MODULE, Rich.NAME).compose(AnyView)

test2: ViewBuilder[type[Extended]] = ViewBuilder(Cli.DEBUG)

class2 = test2.build()
instance = class2()
is_int = instance.x

test3: ViewBuilder[type[CliRenderable]] = ViewBuilder(Cli.HEADER)
class3 = test3.build("Class3")
to_print = class3()


@view(Cli.HEADER, Rich.MODULE, Rich.NAME).compose(AnyView)
class Extended2: ...


def test_cls(mix1: type, mix2: type):
    class Combo(mix1, mix2): ...
