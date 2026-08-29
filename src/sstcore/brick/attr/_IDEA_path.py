from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Any, overload

type Guard = Callable[[Any, Path], Path]
type Build = Callable[..., Path]


def resolve(obj: Any, spec: str) -> Any:
    if spec == "cwd":
        return Path.cwd()
    node: Any = obj
    for part in spec.split("."):
        node = getattr(node, part)
    return node


class PathField:
    """Computed path. `of` is another attribute or 'cwd'. Optional `_names` lookup.

    call=False  -> instance.attr        (Path)
    call=True   -> instance.attr(...)   (factory)
    """

    def __init__(
        self,
        *parts: str,
        of: str,
        named: str | None = None,
        stem: str | None = None,
        suffix: str = "",
        build: Build | None = None,
        guard: Guard | None = None,
        call: bool = False,
        doc: str = "",
    ) -> None:
        self.parts = parts
        self.of = of
        self.named = named
        self.stem = stem
        self.suffix = suffix
        self.build = build
        self.guard = guard
        self.call = call or stem is not None
        self.__doc__ = doc
        self.public_name = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self.public_name = name

    def __set__(self, obj: object, value: object) -> None:
        raise AttributeError(
            f"cannot assign to path field {self.public_name!r}"
        )

    @overload
    def __get__(self, obj: None, owner: type | None = None) -> PathField: ...
    @overload
    def __get__(
        self, obj: object, owner: type | None = None
    ) -> Path | Callable[..., Path]: ...

    def __get__(
        self, obj: object | None, owner: type | None = None
    ) -> PathField | Path | Callable[..., Path]:
        if obj is None:
            return self
        if self.call:
            return self._bind(obj)
        return self._produce(obj)

    def _bind(self, obj: object) -> Callable[..., Path]:
        def bound(*args: Any, **kwargs: Any) -> Path:
            return self._produce(obj, *args, **kwargs)

        bound.__name__ = self.public_name
        bound.__doc__ = self.__doc__
        return bound

    def _produce(self, obj: object, *args: Any, **kwargs: Any) -> Path:
        path = (
            Path(self.build(obj, *args, **kwargs))
            if self.build is not None
            else self._join(obj, *args, **kwargs)
        )
        return self.guard(obj, path) if self.guard is not None else path

    def _join(self, obj: object, *args: Any, **kwargs: Any) -> Path:
        base = Path(resolve(obj, self.of))
        bits: list[str] = []
        if self.named is not None:
            bits.append(str(getattr(obj._names, self.named)))
        if self.stem is not None:
            bits.append(
                str(getattr(obj._names, self.stem)(*args, **kwargs))
                + self.suffix
            )
        bits.extend(self.parts)
        return base.joinpath(*bits) if bits else base


if TYPE_CHECKING:
    from sstcore.util.path.guard import PathGuard


def Dir(
    *parts: str,
    of: str,
    named: str | None = None,
    build: Build | None = None,
    doc: str = "",
) -> PathField:
    return PathField(
        *parts,
        of=of,
        named=named,
        build=build,
        guard=lambda _obj, path: PathGuard.dir(path),
        doc=doc,
    )


def Rel(
    *parts: str,
    of: str,
    named: str | None = None,
    build: Build | None = None,
    doc: str = "",
) -> PathField:
    return PathField(*parts, of=of, named=named, build=build, doc=doc)


def File(
    *parts: str,
    of: str,
    named: str | None = None,
    _default_content: str | None = None,
    raise_error: bool = False,
    doc: str = "",
) -> PathField:
    def guard(obj: Any, path: Path) -> Path:
        return PathGuard.file(
            path, default_content="", raise_error=raise_error
        )

    return PathField(*parts, of=of, named=named, guard=guard, doc=doc)


def Unique(
    *,
    of: str,
    stem: str | None = None,
    suffix: str = "",
    ensure_parent: bool = False,
    build: Build | None = None,
    doc: str = "",
) -> PathField:
    return PathField(
        of=of,
        stem=stem,
        suffix=suffix,
        build=build,
        call=True,
        guard=lambda _obj, path: PathGuard.unique(
            path, ensure_parent=ensure_parent
        ),
        doc=doc,
    )


class TestPaths:
    project_root = Dir(of="_homes.root")
    config_dir = Dir(of="_homes.config")
    log_dir = Dir(of="_homes.log")
    data_dir = Dir(of="_homes.data")
    state_dir = Dir(of="_homes.state")
    plot_dir = Dir(named="plot_dir", of="project_root")

    dot_env_unconfirmed = Rel(".env", of="config_dir")

    summary_file = Unique(
        of="data_dir",
        stem="summary_file",
        ensure_parent=True,
    )


paths = TestPaths()

x = paths.config_dir
