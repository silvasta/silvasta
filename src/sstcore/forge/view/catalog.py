"""
Store the Mixins in Proper Container

  Enum   : Implemented Mixin Method
  - Cli  : __cli__
  - Str  : __str__
  - Rich : __rich__
  - Repr : __repr__
  - Log  : __log__
                          TODO   DependencyLevel.sstcore.brick.views[1]
"""

__all__: list[str] = [
    "Cli",
    "Str",
    "Rich",
    "Repr",
    "Log",
    #
    "ViewSentinel",
]

import enum as _enum

from ...port import represent as _represent
from ...port import solid as _solid
from ...port._error import EnumError as _EnumError
from ...port.empty import ViewSentinel
from . import _views


class Cli(_solid.MixinCatalog):
    LINE = _enum.auto()
    PANEL = _enum.auto()
    TABLE = _enum.auto()
    HEADER = _enum.auto()
    PATHS = _enum.auto()
    DEBUG = _enum.auto()
    MARKDOWN = _enum.auto()
    OFF = _enum.auto()

    @property
    def mixin(self) -> type[_represent.CliSerializable]:
        match self:
            case self.LINE:
                return _views.cli.LineMixin

            case self.PANEL:
                return _views.cli.PanelMixin

            case self.TABLE:
                return _views.cli.TableMixin

            case self.HEADER:
                return _views.cli.SlimPanelMixin

            case self.PATHS:
                return _views.cli.PathPanelMixin

            case self.DEBUG:
                return _views.cli.FullPanelMixin

            case self.MARKDOWN:
                return _views.cli.MarkdownMixin  # ty:ignore FIX:

            case self.OFF:
                return ViewSentinel

        raise _EnumError(self, "Failed Dispatch in Match")


class Str(_solid.MixinCatalog):
    SHORT = _enum.auto()
    NAME = _enum.auto()
    MODULE = _enum.auto()
    OFF = _enum.auto()

    @property
    def category(self) -> str:
        """Override _enum.auto-generated Str.str that silently causes issues"""
        return "string"

    @property
    def mixin(self) -> type[_represent.Stringable]:
        match self:
            case self.SHORT:
                return _views.string.SimpleNameMixin

            case self.NAME:
                return _views.string.NameMixin

            case self.MODULE:
                return _views.string.ModuleNameMixin

            case self.OFF:
                return ViewSentinel

        raise _EnumError(self, "Failed Dispatch in Match")


class Rich(_solid.MixinCatalog):
    SHORT = _enum.auto()
    NAME = _enum.auto()
    MODULE = _enum.auto()
    OFF = _enum.auto()

    @property
    def mixin(self) -> type[_represent.RichView]:
        match self:
            case self.SHORT:
                return _views.rich.SimpleRichNameMixin

            case self.NAME:
                return _views.rich.RichNameMixin

            case self.MODULE:
                return _views.rich.RichModuleNameMixin

            case self.OFF:
                return ViewSentinel

        raise _EnumError(self, "Failed Dispatch in Match")


class Repr(_solid.MixinCatalog):
    BOX = _enum.auto()
    DATA = _enum.auto()
    DEBUG = _enum.auto()
    OFF = _enum.auto()

    @property
    def mixin(self) -> type[_represent.LogStringable]:
        match self:
            case self.BOX:
                return _views.repr.ReprMixin
        match self:
            case self.DATA:
                return _views.repr.ReprDataMixin

            case self.DEBUG:
                return _views.repr.FullReprMixin

            case self.OFF:
                return ViewSentinel

        raise _EnumError(self, "Failed Dispatch in Match")


class Log(_solid.MixinCatalog):
    DATA = _enum.auto()
    DEBUG = _enum.auto()
    OFF = _enum.auto()

    @property
    def mixin(self) -> type[_represent.LogSerializable]:
        match self:
            case self.DATA:
                return _views.log.LogDataMixin

            case self.DEBUG:
                return _views.log.FullLogMixin

            case self.OFF:
                return ViewSentinel

        raise _EnumError(self, "Failed Dispatch in Match")
