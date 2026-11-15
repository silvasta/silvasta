"""
Support Handling of Python package.module:Object Paths

-
"""

__all__: list[str] = [
    "DotPath",
    "ModulePath",
]

import importlib.util
import inspect
import pkgutil
import sys
from collections.abc import Callable, Iterable, Iterator
from importlib import import_module
from keyword import iskeyword
from types import ModuleType
from typing import Any, NamedTuple, NotRequired, Self, TypedDict
from typing import Unpack as _U  # noqa:N814


class DotPath(str):
    """Validate dotted Python identifier path (like pkg.mod or .sub.mod)"""

    __slots__ = ()

    def __new__(cls, target, /, *, allow_relative: bool = False) -> Self:
        """Confirm input and create ...valid.dot.path (leading dots on flag)"""
        if target and not cls.accepts(target, allow_relative=allow_relative):
            raise ValueError(f"Invalid dotted Python path: {target!r}")
        return super().__new__(cls, target)

    def __truediv__(self, sub: str) -> Self:
        """Concat [DotPath("my.path") / "extra.path"] -> [my.path.extra.path]"""
        if not self.accepts(sub, allow_relative=False):
            raise ValueError(f"Invalid dotted segment: {sub!r}")
        return type(self)(f"{self}.{sub}" if self else sub)

    @property
    def is_relative(self) -> bool:
        return self.startswith(".")

    @property
    def depth(self) -> int:
        """Relative Degree: Number of leading dots (0 for absolute paths)"""
        return len(self) - len(self.lstrip("."))

    @property
    def parts(self) -> Iterator[str]:
        """Identifier segments with leading dots stripped"""
        if core := self.lstrip("."):
            yield from core.split(".")

    @classmethod
    def double_dot(cls, target: str, /, **tk: _U[_Rel]) -> _Double[Self]:
        """Split to [module:qualname] or [module:""] or for invalid: ["":""]"""
        print(f"double_dot::{tk=}")
        _mod, _sep, _qual = target.strip().partition(":")
        if cls.accepts(_mod, **tk):
            if not _sep:
                return cls(_mod), cls("")
            if cls.accepts(_qual, allow_relative=False):
                return cls(_mod), cls(_qual)
        return cls(""), cls("")

    @staticmethod
    def accepts(target: str, /, **tk: _U[_Rel]) -> bool:
        """Is target a legal dotted Python identifier path?"""

        _allow_relative = tk.get("allow_relative", True)

        if core := target.lstrip(".") if _allow_relative else target:
            return all(
                part.isidentifier() and not iskeyword(part)
                for part in core.split(".")
            )
        return False


type _Double[T] = tuple[T, T]
type DotStr = DotPath | str


class _Rel(TypedDict):
    allow_relative: NotRequired[bool]


class _QA(TypedDict):
    require_qualattr: NotRequired[bool]


class _RelQA(_Rel, _QA): ...


class _ModQual(TypedDict, total=False):
    module: DotStr
    qualname: DotStr


class _ModulePathBase(NamedTuple):
    """Assign Attrs and Unlock __new__ for subclasses"""

    module: DotPath
    qualname: DotPath = DotPath("")


class ModulePath(_ModulePathBase):
    """Represent package.module:qualname including Path Utils"""

    def __new__(cls, module: DotStr, qualname: DotStr | str = "", /):
        """Make values DotPath before instantiation"""
        if not cls.accepts(cls.concat(module, ":", qualname)):
            raise ValueError(f"Invalid for ModulePath: {module=}, {qualname=}")
        return tuple.__new__(
            cls, (DotPath(module), DotPath(qualname, allow_relative=False))
        )

    def __truediv__(self, extension: str) -> Self:
        """
        Extend Module Path or Replace(":") or Extend("::") Qualname

        - ModulePath("my.path") / "next" # = "my.path.next"
        - ModulePath("my.path:Cls") / "next" # = "my.path.next:Cls"

        - ModulePath("my.path:Cls") / ":next" # = "my.path:next"
        - ModulePath("my.path:Cls") / "::next" # = "my.path:Cls.next"

        """
        if extension.startswith("::"):
            return self.evolve(qualname=self.qualname / extension[2:])

        if extension.startswith(":"):
            return self.evolve(qualname=extension[1:])

        return self.evolve(module=self.module / extension)

    def __str__(self) -> str:
        return self.concat(self.module, ":", self.qualname)

    @staticmethod
    def accepts(target: str, /, **tk: _U[_RelQA]) -> bool:
        """Is the Syntax valid for ModulePaths?"""
        _need_qualattr = tk.pop("require_qualattr", False)
        _mod, _qual = DotPath.double_dot(target, **tk)
        return bool(_mod) and (not _need_qualattr or bool(_qual))

    @staticmethod
    def concat(module: str, sep: str, qualname: str, /) -> str:
        return f"{module}{f'{sep}{qualname}' if qualname else ''}"

    @property
    def dotted(self) -> str:
        return self.concat(self.module, ".", self.qualname)

    @property
    def modules(self) -> tuple[str, ...]:
        """Module identifier segments"""
        return tuple(self.module.parts)

    @property
    def submodules(self) -> tuple[str, ...]:
        """Module segments after root project (or all segments if relative)."""
        return self.modules if self.is_relative else self.modules[1:]

    @property
    def quals(self) -> tuple[str, ...]:
        """Qualname identifier segments"""
        return tuple(self.qualname.parts)

    @property
    def is_relative(self) -> bool:
        return self.module.is_relative

    @property
    def is_absolute(self) -> bool:
        return not self.module.is_relative

    @property
    def depth(self) -> int:
        """Relative Degree: Number of leading dots (0 for absolute paths)"""
        return self.module.depth

    @property
    def public(self) -> str:
        """Walk upwards until the nearest Public Package"""
        parts: list[str] = list(self.modules)
        while len(parts) > 1 and parts[-1].startswith("_"):
            parts.pop()
        return ".".join(parts)

    @property
    def project(self) -> str:
        """Provide root package name, first part in absolute module path"""
        return "" if self.is_relative else self.modules[0]

    def detect_project(self, *, raise_error=False) -> str:
        """Inspect root package name and compare with absolute module path"""
        detected: str = _caller_package(depth=2).partition(".")[0]
        if self.is_absolute and detected != (assigned := self.project):
            if raise_error:
                raise RuntimeError(f"Project Mismatch: {detected=},{assigned=}")
        return detected

    @classmethod
    def parse(cls, target: str, /, **tk: _U[_Rel]) -> Self:
        """Parse 'pkg.mod:Cls.attr' or 'pkg.mod' into canonical ModulePath"""
        return cls(*DotPath.double_dot(target, **tk))

    @classmethod
    def identify(cls, target: Any, /, *, default: str = "builtins") -> Self:
        """Extract ModulePath from identified Object"""

        if inspect.ismodule(target):
            return cls(target.__name__, "")

        _obj = target if _is_definition(target) else type(target)

        return cls(_modulename(_obj, default=default), _qualname(_obj))

    @classmethod
    def cwd(cls, *, depth: int = 1) -> Self:
        """Extract current Module/Package of caller as ModulePath"""
        return cls(_caller_package(depth + 1))

    def evolve(self, **tk: _U[_ModQual]) -> Self:
        """Update Module or Qualname on new ModulePath"""
        return type(self)(
            tk.get("module", self.module), tk.get("qualname", self.qualname)
        )

    def resolve(self, *anchors: str | Self, check_exists: bool = True) -> Self:
        """Resolve Relative into Absolute ModulePath"""
        if self.is_absolute:
            return self

        return self.evolve(
            module=_resolve_relative(
                self.module,
                *(self.norm(anchors) or [_caller_package(depth=2)]),
                check_exists=check_exists,
            )
        )

    @classmethod
    def norm(cls, anchors: Iterable[Self | str]) -> Iterator[str]:
        """Transform Anchors into"""
        for anchor in anchors:
            match anchor:
                case cls():
                    normalized: str = anchor.module
                case str():
                    normalized: str = anchor
                case _:
                    message = f"Expected ModulePath or str, got: {type(anchor)=}, {anchor=}"
                    raise TypeError(message)
            if DotPath.accepts(normalized):
                yield normalized

    def lazy_loader[R](
        self,
        *,
        call_if_callable: bool = True,
        ensure_exists: bool = False,
        package: str | None = None,
    ) -> Callable[[], R]:
        """Bind Zero-Arg Closure that importes resolved Target"""

        if ensure_exists and not self.importable(package=package):
            _text = "qualname attr" if self.module_exists(package) else "module"
            raise ImportError(f"Missing {_text} for Import: {self}")

        def _call_it(target, /) -> bool:
            return call_if_callable and callable(target)

        def loader() -> R:
            return (
                target()
                if _call_it(target := self.importing(package))
                else target
            )

        return loader

    def module_exists(self, package: str | None = None) -> bool:
        """Check if module spec exists without executing leaf module"""
        return _module_exists(self.module, package=package)

    def import_module(self, package: str | None = None) -> ModuleType:
        """Provide the imported Module, anchor by package for relative paths"""
        return import_module(self.module, package=package)

    def importable(self, package: str | None = None) -> bool:
        """Verify that the module and all qualname attributes can be imported"""
        if not self.module_exists(package=package):
            return False
        try:
            self.importing(package)
            return True
        except Exception:
            return False

    def importing(self, package: str | None = None) -> Any:
        """Import the Attribute defined by qualname from module, anchor by package if relative"""

        if self.is_absolute and len(self.quals):
            return pkgutil.resolve_name(f"{self}")

        module: ModuleType = import_module(name=self.module, package=package)

        extracted: Any = module
        for next_part in self.qualname.parts:
            extracted: Any = getattr(extracted, next_part)
        return extracted


def _caller_package(depth: int = 2) -> str:
    """Inspect stack frame to determine caller's package or module name."""
    try:
        _frameget = sys._getframe(depth).f_globals.get
        package: Any | None = _frameget("__package__") or _frameget("__name__")
        if isinstance(package, str) and package and package != "__main__":
            return package
        if spec := _frameget("__spec__"):
            if spec.parent:
                return spec.parent
    except ValueError:
        pass
    return (__package__ or __name__).partition(".")[0]


def _is_definition(target: Any, /) -> bool:
    return any(
        (
            inspect.isclass(target),
            inspect.isfunction(target),
            inspect.ismethod(target),
            inspect.isbuiltin(target),
        )
    )


def _modulename(target: Any, /, default="builtins") -> str:
    if isinstance(mod := getattr(target, "__module__", None), str) and mod:
        return mod
    return default


def _qualname(target: Any, /, default="") -> str:
    for attr in ("__qualname__", "__name__"):
        if isinstance(val := getattr(target, attr, None), str) and val:
            return val
    return default


# REMOVE: when filter in class body established
def _anchor_strings(*anchors: str | ModulePath) -> tuple[str, ...]:
    return tuple(
        anchor.module if isinstance(anchor, ModulePath) else anchor
        for anchor in anchors
    )


def _module_exists(module: str, /, package: str | None = None) -> bool:
    """Return ModuleSpec if module exists without executing leaf module, else None."""
    try:
        return importlib.util.find_spec(module, package=package) is not None
    except ImportError, ValueError, TypeError:
        return False


def _resolve_relative(
    module: str, /, *anchors: str, check_exists: bool = True
) -> str:
    """Resolve relative module against candidate anchors, optionally probing existence."""
    if not module.startswith("."):
        return module

    first_hit: str | None = None

    for anchor in anchors:
        try:
            resolved: str = importlib.util.resolve_name(module, anchor)
        except ValueError, ImportError:
            continue

        if first_hit is None:
            first_hit: str = resolved

        if not check_exists or _module_exists(resolved):
            return resolved

    if first_hit is not None and not check_exists:
        return first_hit

    raise ImportError(
        f"Cannot resolve relative module {module!r} against anchors {anchors!r}"
    )


if __name__ == "__main__":
    _module, _attr = DotPath.double_dot(
        "my.path:Cls.attr", allow_reltive=False, test=3
    )
    print(f"{_module=}, {_attr=}")
    DotPath.double_dot("t")
    DotPath.double_dot("t", allow_relativ=False)  # AI: this is dangerous...

    ModulePath("mod").evolve(bad="test")  # AI: no warnings...
