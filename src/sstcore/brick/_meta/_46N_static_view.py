"""
And some Extensions and Ideas

-
"""

from collections.abc import Callable
from dataclasses import dataclass
from types import FunctionType
from typing import TYPE_CHECKING, Any

from ...port.color import ColorBox
from ...port.event.dto import PanelDTO
from ..color.box import Colors

colors: ColorBox = Colors()


@dataclass(frozen=True, slots=True)
class _ToolkitConf:
    title: str | None = None
    rich: Callable[[type], str] | None = None
    frame: Any = None
    cli_content: Any = None  # None → list(cls.toolkit())
    log_extra_key: str = "toolkit"
    make_error: Callable[[type], BaseException] | None = None


class StaticToolkitMeta(type):
    """ONLY CHANGES HERE (TO 46B)"""

    _conf: dict[type, _ToolkitConf] = {}

    def __new__(
        mcls,
        name: str,
        bases: tuple[type, ...],
        ns: dict[str, Any],
        *,
        title: str | None = None,
        rich: Callable[[type], str] | None = None,
        frame: Any = None,
        cli_content: Any = None,
        **_kwargs,
    ):
        # AI: why not  just __init__?
        # - or then directly build the views below here

        cls = super().__new__(mcls, name, bases, ns)
        mcls._conf[cls] = _ToolkitConf(
            title=title,
            rich=rich,
            frame=frame,
            cli_content=cli_content,
        )
        return cls

    def _cfg(cls) -> _ToolkitConf:
        return StaticToolkitMeta._conf.get(cls, _ToolkitConf())

    def __str__(cls) -> str:
        return cls._cfg().title or cls.__name__

    def __rich__(cls) -> str:
        rich = cls._cfg().rich
        return rich(cls) if rich else f"{colors.azure(cls)}"

    def __cli__(cls) -> PanelDTO:
        cfg = cls._cfg()
        content = cfg.cli_content
        if content is None:
            content = list(cls.toolkit())
        elif callable(content):
            content = content(cls)
        return PanelDTO(
            content=content,
            title=cls.__rich__(),
            frame=cfg.frame or colors.azure,
        )


class PathGuard(
    metaclass=StaticToolkitMeta,
    title=" PathGuard ",
    rich=lambda cls: f"{colors.a('Path')}{colors.s('Guard')}",
    frame="cyan",
    cli_content="Safety and Comfort for Path and File System operations",
): ...


def _enforce_facade__new__(mcls, name, bases, ns):
    """FAIL! Better the idea with auto converting staticmethod"""
    _SKIP = {
        "__module__",
        "__qualname__",
        "__doc__",
        "__annotations__",
        "__init__",
    }

    for key, value in ns.items():
        if key in _SKIP or key.startswith("_"):
            continue
        if isinstance(
            value, (staticmethod, classmethod, type)
        ):  # Spec, SyncMode, Reason
            continue
        if isinstance(value, FunctionType):
            raise TypeError(
                f"{name}.{key} must be staticmethod; got a plain function"
            )


class _ToolkitNS(dict):
    def __setitem__(self, key, value):
        if (
            isinstance(value, FunctionType)
            and not key.startswith("_")
            and not isinstance(value, (staticmethod, classmethod))
        ):
            value = staticmethod(value)
        super().__setitem__(key, value)


class StaticToolkitMeta(type):
    @classmethod
    def __prepare__(mcls, name, bases, **kw):
        """Yes! EXACTLY LIKE THIS"""

        # AI_FOCUS: maybe not exactly like this but with exactly this effect,
        # - attach methods very simple in class body
        # -> convert here to staticmethod
        return _ToolkitNS()


if TYPE_CHECKING:
    from ...util.path.guard import PathSpec, _ensure


class TidyPathGuard(metaclass=StaticToolkitMeta):
    """NO! why is this still fucked up??!!"""

    # AI: the idea was as well to clean up the in the IDE displayed types...
    # - ok, before the issue was that I couldn't assign a callable type because of staticmethod
    # - with that here it should be not anymore an issue, right?

    dir = _ensure.dir  # FunctionType → wrapped
    file: Callable = _ensure.file
    Spec = PathSpec
