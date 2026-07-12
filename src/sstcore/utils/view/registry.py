"""
Store the Mixins in proper Container

  Enum   : Implemented Mixin Method
  - Cli  : __cli__
  - Str  : __str__
  - Rich : __rich__
  - Repr : __repr__
  - Log  : __log__

"""

from enum import Enum, auto

from . import mixin
from .protocol import (
    CliRenderable,
    LogSerializable,
    MixinSentinel,
    RichRenderable,
)


class Cli(Enum):
    PANEL = auto()
    BAR = auto()
    LINE = auto()
    TABLE = auto()
    MARKDOWN = auto()
    OFF = auto()

    @property
    def mixin(self) -> type[CliRenderable]:
        match self:
            case self.PANEL:
                return mixin.cli.CliFullPanelMixin

            case self.BAR:
                return mixin.cli.CliSlimPanelMixin

            case self.LINE:
                return mixin.cli.CliLineMixin

            case self.TABLE:  # TODO: attach or delete
                raise NotImplementedError("Cli.TABLE Mixin")

            case self.MARKDOWN:  # TODO: attach or delete
                raise NotImplementedError("Cli.MARKDOWN Mixin")

            case self.OFF:
                return MixinSentinel


class Str(Enum):
    DEFAULT = auto()  # LATER: change! DEFAULT -> ?
    SHORT = auto()
    OFF = auto()

    @property
    def mixin(self) -> type:
        match self:
            case self.DEFAULT:
                return mixin.string.NameMixin

            case self.SHORT:
                return mixin.string.SimpleNameMixin

            case self.OFF:
                return MixinSentinel


class Rich(Enum):
    DEFAULT = auto()
    SHORT = auto()
    OFF = auto()

    @property
    def mixin(self) -> type[RichRenderable]:
        match self:
            case self.DEFAULT:
                return mixin.rich.ModuleNameMixin

            case self.SHORT:
                return mixin.rich.SimpleNameMixin

            case self.OFF:
                return MixinSentinel


class Repr(Enum):
    DEFAULT = auto()
    FULL = auto()
    OFF = auto()

    @property
    def mixin(self) -> type:
        match self:
            case self.DEFAULT:
                return mixin.repr.DataMixin

            case self.FULL:
                return mixin.repr.FullReprMixin

            case self.OFF:
                return MixinSentinel


class Log(Enum):
    DEFAULT = auto()
    FULL = auto()
    PYDANTIC = auto()
    OFF = auto()

    @property
    def mixin(self) -> type[LogSerializable]:
        match self:
            case self.DEFAULT:
                return mixin.log.LogMixin

            case self.FULL:
                return mixin.log.DebugLogMixin

            case self.PYDANTIC:
                return mixin.log.PydanticDataMixin

            case self.OFF:
                return MixinSentinel
