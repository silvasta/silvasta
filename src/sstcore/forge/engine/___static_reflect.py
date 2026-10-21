import inspect
from types import FunctionType, ModuleType
from typing import Any

from ._meta_view import ClsViewBase
from ._static_func import StaticFuncMetaData


def _extract_module_functions(module: ModuleType) -> dict[str, FunctionType]:
    """Extract public functions and __core__ from a module."""
    extracted = {}
    for name, func in inspect.getmembers(module, inspect.isfunction):
        # CRITICAL: Only grab functions defined IN this module,
        # ignoring external imports (like 'os' or 'sys')
        if func.__module__ == module.__name__:
            if name == "__core__" or not name.startswith("_"):
                extracted[name] = func
    return extracted


class StaticFuncMeta(ClsViewBase):
    """Create Blueprint for Static Functorials"""

    # TASK: solve recursive module deepnes

    def __new__(
        mcls,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        data: StaticFuncMetaData | None = None,
        module: ModuleType | None = None,  # Accept the module via class kwargs
        **kwargs,
    ):
        """Attach all methods as staticmethod and load input for dunder data"""

        # 1. Inject module functions into the namespace
        if module is not None:
            extracted = _extract_module_functions(module)
            for k, v in extracted.items():
                # Allow class-body definitions to override module definitions
                if k not in namespace:
                    namespace[k] = v

        # EXTRACT:

        # 2. Auto-convert to staticmethod (whitelist __core__)
        new_static_methods: dict[str, Any] = {
            key: staticmethod(value)
            for key, value in namespace.items()
            if (not key.startswith("_") or key == "__core__")
            and isinstance(value, FunctionType)
        }
        namespace.update(new_static_methods)

        return super().__new__(mcls, name, bases, namespace, **kwargs)

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:  # noqa:N805
        """Route class calls to __core__ or block instantiation."""
        if hasattr(cls, "__core__"):
            return cls.__core__(*args, **kwargs)  # ty:ignore

        # Route to SstError/custom error if no core is defined
        raise TypeError(
            f"StaticFunc[{cls.__name__}] has no __core__ and is Not available as Instance!"
        )

    def toolkit(cls, sort: bool = True) -> list[str]:  # noqa:N805
        # ... your existing toolkit code ...
        pass
