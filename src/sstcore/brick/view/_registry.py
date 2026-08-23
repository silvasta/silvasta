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
    "Cli",
    "Str",
    "Rich",
    "Repr",
    "Log",
]

from enum import Enum, auto

from ...brick.format import cls_name
from ...port.view import (
    CliRenderable,
    LogSerializable,
    Reprable,
    RichRenderable,
    Stringable,
)
from . import _mixin as mixin


# MOVE: port
class ViewRegistry(Enum):
    @property
    def category(self) -> str:
        return cls_name(self).lower()

    # TODO:
    # @property
    # def mixin(self) -> type[XXX]:

    def fail_info(self, reason: str) -> str:
        return f"{self}View[{self.name}] Failed: {reason}"

    def __str__(self) -> str:
        return f"{cls_name(self)}View[{self.name}]"


class Cli(ViewRegistry):
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
                return mixin.cli.LineMixin

            case self.TABLE:
                return mixin.cli.TableMixin

            case self.PANEL:
                return mixin.cli.PanelMixin

            case self.HEADER:
                return mixin.cli.SlimPanelMixin

            case self.DEBUG:
                return mixin.cli.FullPanelMixin

            case self.PATHS:
                return mixin.cli.PathPanelMixin

            case self.MARKDOWN:
                return mixin.cli.MarkdownMixin

            case self.OFF:
                return mixin.MixinSentinel


class Str(ViewRegistry):
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
                return mixin.string.SimpleNameMixin

            case self.NAME:
                return mixin.string.NameMixin

            case self.MODULE:
                return mixin.string.ModuleNameMixin

            case self.OFF:
                return mixin.MixinSentinel


class Rich(ViewRegistry):
    SHORT = auto()
    NAME = auto()
    MODULE = auto()
    OFF = auto()

    @property
    def mixin(self) -> type[RichRenderable]:
        match self:
            case self.SHORT:
                return mixin.rich.SimpleRichNameMixin

            case self.NAME:
                return mixin.rich.RichNameMixin

            case self.MODULE:
                return mixin.rich.RichModuleNameMixin

            case self.OFF:
                return mixin.MixinSentinel


class Repr(ViewRegistry):
    BOX = auto()
    DATA = auto()
    DEBUG = auto()
    OFF = auto()

    @property
    def mixin(self) -> type[Reprable]:
        match self:
            case self.BOX:
                return mixin.repr.ReprMixin
        match self:
            case self.DATA:
                return mixin.repr.ReprDataMixin

            case self.DEBUG:
                return mixin.repr.FullReprMixin

            case self.OFF:
                return mixin.MixinSentinel


class Log(ViewRegistry):
    DATA = auto()
    DEBUG = auto()
    OFF = auto()

    @property
    def mixin(self) -> type[LogSerializable]:
        match self:
            case self.DATA:
                return mixin.log.LogDataMixin

            case self.DEBUG:
                return mixin.log.FullLogMixin

            case self.OFF:
                return mixin.MixinSentinel
