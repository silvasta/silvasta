"""
Helper for Operators

- where to place later on?
"""

import typing as _t

from ..calling import Stringable


class DunderStore(_t.Protocol):
    def __init__(self, dunders: _t.Iterable[str] = ()): ...
    def get(self, name: str, *args, **kwargs) -> str | None: ...


class DunderFormat:
    @staticmethod
    def format(item: Stringable, /) -> str:
        return f"__{DunderFormat.extract(item)}__"

    @staticmethod
    def extract(item: Stringable, /) -> str:
        return str(item).strip("_")


class DunderDict(DunderFormat, dict):
    def __init__(self, dunders: _t.Iterable[str] = ()):
        for method in dunders:
            self[method] = None

    def __setitem__(self, key, _value=None):
        super().__setitem__(key.strip("_"), f"__{key.strip('_')}__")


class DunderSet(DunderFormat, frozenset):
    def __new__(cls, items: _t.Iterable[str] = (), /):
        return super().__new__(cls, (cls.format(item) for item in items))

    def __contains__(self, target: _t.Any) -> bool:
        return super().__contains__(self.format(target))

    def get(self, item: str, default=None) -> str | None:
        return dunder if (dunder := self.format(item)) in self else default


def lined(target, /):
    if isinstance(target, dict):
        target = (f"{k}: {v}" for k, v in target.items())
    return "\n".join(target)


def print_topic(title, content=None, /):
    print(title)
    if content:
        print(content)
    print()


def test_dunder_access():
    dunders: set[str] = {
        "__doc__",
        "__func__",
        "portlinkdocs",
    }
    dict1 = DunderDict(set())
    dset1 = DunderSet(set())
    print_topic("d1 dict", dict1)
    print_topic("d1 set ", dset1)

    dict2 = DunderDict(dunders)
    print_topic("d2", dict2)
    print_topic("d2", lined(dict2))
    print(dict2.get("func"))
    print(dict2.get("funk"))

    dset2 = DunderSet(dunders)
    print_topic("d2", dset2)
    print_topic("d2", lined(dset2))
    print(dset2.get("func"))
    print(dset2.get("funk"))


def test_dunder_format():
    print_topic("DunderDict")
    print(DunderDict.format("call"))
    print(DunderDict.format("_call_"))
    print(DunderDict.format("__call__"))

    print_topic("DunderSet")
    print(DunderSet.format("call"))
    print(DunderSet.format("_call_"))
    print(DunderSet.format("__call__"))


if __name__ == "__main__":
    test_dunder_access()
    test_dunder_format()
