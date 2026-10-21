"""
Functor Meta Tests

- Output
---
uv run testings_with_functor.py
Usage 2: Direct
/tmp/file.txt
Usage 2: Bare Decorator
/tmp/system_log.txt
Usage 2: Parameterized
/var/log/AUTO.log
---

"""

from typing import Any, TypeGuard

from sstcore.brick.forge.blueprint._functor import FunctorMetaData
from sstcore.brick.func._tor import BaseFunctor
from sstcore.port.functor import Functor as Functor


def is_string(val: Any) -> TypeGuard[str]:
    return isinstance(val, str)


FunctorInput = FunctorMetaData(detect=is_string)


class PathResolver(BaseFunctor, data=FunctorInput):
    def apply(self, target: str, *args, **kwargs):
        # Your core logic goes here!
        prefix = self.config.get("prefix", "/tmp")

        # If decorating a function, self._func exists
        if self._func:
            target = self._func(target, *args, **kwargs)

        return f"{prefix}/{target}"


print("Usage 2: Direct")

y = PathResolver("file.txt")
y: str = y
print(y)


print("Usage 2: Bare Decorator")


@PathResolver
def get_name(name: str) -> str:
    return f"{name}_log.txt"


x = get_name("system")
x: str = get_name("system")
print(x)


print("Usage 2: Parameterized")


@PathResolver(prefix="/var/log")
def get_sys_name(name: str):
    return f"{name}.log"


print(get_sys_name("AUTO"))
