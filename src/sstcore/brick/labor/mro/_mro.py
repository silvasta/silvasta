"""
Detect (and future) Analyze MRO Inheritance

-
"""

__all__: list[str] = [
    "sort_cls_by_name",
    "all_common_ancestors",
    "closest_common_ancestor",
    "get_all_descendants",
]


def sort_cls_by_name(classes: set | list | tuple) -> list[str]:
    # TODO: sort the list[type] not the str representations!
    return sorted(cls.__name__ for cls in classes)


def all_common_ancestors(cls1, cls2) -> set[type]:
    """Convert MROs to sets and find intersection"""
    common: set[type] = set(cls1.__mro__) & set(cls2.__mro__)
    common.discard(object)
    return common


def closest_common_ancestor(cls1: type, cls2: type) -> type | None:
    """Find common ancestor nearest intersection point (interchangeable)"""
    if not (common := all_common_ancestors(cls1, cls2)):
        return None
    return min(
        common, key=lambda c: cls1.__mro__.index(c) + cls2.__mro__.index(c)
    )


def get_all_descendants(base_cls) -> set[type]:
    """Find all classes that inherit from base_cls"""

    descendants: set[type] = set()

    # CHECK: if that adds undesired behaviour or safes from cycles
    # Защита от циклов, хотя в Python MRO их быть не должно
    _idea_visited: set[type] = set()

    def walk_subclasses(cls):
        if cls in _idea_visited:
            return
        _idea_visited.add(cls)
        for sub_cls in cls.__subclasses__():
            if sub_cls not in descendants:
                descendants.add(sub_cls)
                walk_subclasses(sub_cls)

    walk_subclasses(base_cls)

    return descendants
