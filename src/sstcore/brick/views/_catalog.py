"""
Store the Mixins in proper Container

  Enum   : Implemented Mixin Method
  - Cli  : __cli__
  - Str  : __str__
  - Rich : __rich__
  - Repr : __repr__
  - Log  : __log__

"""

__all__: list[str] = [
    # all mixins
    "cli",
    "str",
    "rich",
    "repr",
    "log",
    "ViewMixins",
    # all enums
    "Cli",
    "Str",
    "Rich",
    "Repr",
    "Log",
    "MixinCatalog",
]

from enum import Enum, auto

from ...port.calling import LogStringable, Richable, Stringable
from ...port.event import CliRenderable, LogSerializable
from ...port.view import Renderable
from ..labor import clsname
from ..none import ViewSentinel
from . import _cli as cli
from . import _log as log
from . import _repr as repr
from . import _rich as rich
from . import _str as string


class ViewMixins:  # LATER: attach better
    cli = cli
    log = log
    repr = repr
    rich = rich
    string = string


class MixinCatalog(Enum):  # MOVE: maybe port?
    @property
    def category(self) -> str:
        return clsname(self).lower()

    @property
    def mixin(self) -> type[Renderable]:
        raise NotImplementedError

    def fail_info(self, reason: str) -> str:
        return f"{self}View[{self.name}] Failed: {reason}"

    def __str__(self) -> str:
        return f"{clsname(self)}View[{self.name}]"


class Cli(MixinCatalog):
    LINE = auto()
    PANEL = auto()
    TABLE = auto()
    HEADER = auto()
    PATHS = auto()
    DEBUG = auto()
    MARKDOWN = auto()
    OFF = auto()

    @property
    def mixin(self) -> type[CliRenderable]:
        match self:
            case self.LINE:
                return cli.LineMixin

            case self.TABLE:
                return cli.TableMixin

            case self.PANEL:
                return cli.PanelMixin

            case self.HEADER:
                return cli.SlimPanelMixin

            case self.DEBUG:
                return cli.FullPanelMixin

            case self.PATHS:
                return cli.PathPanelMixin

            case self.MARKDOWN:
                return cli.MarkdownMixin

            case self.OFF:
                return ViewSentinel


class Str(MixinCatalog):
    SHORT = auto()
    NAME = auto()
    MODULE = auto()
    OFF = auto()

    @property
    def category(self) -> str:
        """Override str that silently causes issues"""
        return "string"

    @property
    def mixin(self) -> type[Stringable]:
        match self:
            case self.SHORT:
                return string.SimpleNameMixin

            case self.NAME:
                return string.NameMixin

            case self.MODULE:
                return string.ModuleNameMixin

            case self.OFF:
                return ViewSentinel


class Rich(MixinCatalog):
    SHORT = auto()
    NAME = auto()
    MODULE = auto()
    OFF = auto()

    @property
    def mixin(self) -> type[Richable]:
        match self:
            case self.SHORT:
                return rich.SimpleRichNameMixin

            case self.NAME:
                return rich.RichNameMixin

            case self.MODULE:
                return rich.RichModuleNameMixin

            case self.OFF:
                return ViewSentinel


class Repr(MixinCatalog):
    BOX = auto()
    DATA = auto()
    DEBUG = auto()
    OFF = auto()

    @property
    def mixin(self) -> type[LogStringable]:
        match self:
            case self.BOX:
                return repr.ReprMixin
        match self:
            case self.DATA:
                return repr.ReprDataMixin

            case self.DEBUG:
                return repr.FullReprMixin

            case self.OFF:
                return ViewSentinel


class Log(MixinCatalog):
    DATA = auto()
    DEBUG = auto()
    OFF = auto()

    @property
    def mixin(self) -> type[LogSerializable]:
        match self:
            case self.DATA:
                return log.LogDataMixin

            case self.DEBUG:
                return log.FullLogMixin

            case self.OFF:
                return ViewSentinel
