import sys
from typing import Any

__all__ = ["sentinel"]


def use_latest_features() -> bool:
    return sys.version_info >= (3, 15)


if use_latest_features():
    # In 3.15, sentinel is a built-in class, so we can just grab it
    import builtins

    sentinel = builtins.sentinel
else:
    # Python 3.14 Fallback: Mimic the 3.15 behavior
    def sentinel(name: str, repr: str | None = None) -> Any:
        class Sentinel:
            def __repr__(self) -> str:
                return repr if repr is not None else f"<{name}>"

            def __bool__(self) -> bool:
                # PEP 661 specifies sentinels are truthy
                return True

        # The class name is updated to help with debugging
        Sentinel.__name__ = name
        return Sentinel()

# ---------------------------------------------------------
# Usage anywhere else in sstcore:
# ---------------------------------------------------------
# from sstcore.port.sentinel import sentinel
# MISSING = sentinel("MISSING")
