"""
Generate stub files automatically

-

"""

__all__ = [
    "TypeForm",
    "TypedDict",
]

import importlib
import re
import sys
from collections.abc import Callable
from typing import Any


def latest_python() -> bool:
    return sys.version_info >= (3, 15)


if latest_python():
    from typing import TypedDict as TypedDict
    from typing import TypeForm as TypeForm
else:
    from typing_extensions import TypedDict as TypedDict
    from typing_extensions import TypeForm as TypeForm


def generate_stub(line: str) -> str:
    # Transforms: "lazy from sstcore.data import heavy"
    # To:         "from sstcore.data import heavy"
    # IDEA: str.leftstrip("lazy")
    return re.sub(r"^(\s*)lazy\s+(import|from)", r"\1\2", line)


def extract_lazy_targets(line: str, lazy_dict: dict[str, str]) -> None:
    # Matches: "lazy from .system import System"
    # Captures: group(1) = ".system", group(2) = "System"
    match = re.match(r"^\s*lazy\s+from\s+([.\w]+)\s+import\s+(\w+)", line)

    if match:
        module, name = match.groups()
        # You might need logic here to resolve relative imports (the '.')
        # based on the current file path, but the extraction is clean.
        lazy_dict[name] = f"{module}.{name}"


def create_lazy_loader(
    module_name: str, lazy_imports: dict[str, str]
) -> Callable[[str], Any]:
    """
    Generate a PEP 562 __getattr__ function to defer module execution.

    Compatible with Python 3.14 and 3.15 without parse-time syntax errors.
    """

    def __getattr__(name: str) -> Any:  # noqa: N807
        if name in lazy_imports:
            target_path = lazy_imports[name]
            module = importlib.import_module(target_path)

            # Cache the imported module in the caller's globals
            # so subsequent accesses bypass __getattr__ entirely
            sys.modules[module_name].__dict__[name] = module
            return module

        raise AttributeError(
            f"module {module_name!r} has no attribute {name!r}"
        )

    return __getattr__


_LAZY_IMPORTS = {
    "ConfigManager": "sstcore.system.config",
    "Emitter": "sstcore.system.event",
    "System": "sstcore.system._core",
}

__getattr__ = create_lazy_loader(__name__, _LAZY_IMPORTS)


def __dir__() -> list[str]:
    return list(globals().keys()) + list(_LAZY_IMPORTS.keys())
