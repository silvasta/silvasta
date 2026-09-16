"""
Detect (and future) Analyze MRO Inheritance

-
"""

__all__: list[str] = [
    "sort_cls_by_name",  # RENAME: (probably all)
    "all_common_ancestors",
    "closest_common_ancestor",
    "get_all_descendants",
]


#  LINE: -- sort -- -- - -- -- - -- -- - -- -- - -- -- - -- --


# IDEA: sort_by_clsname, or as plugin of clsname???
def sort_cls_by_name(classes: set | list | tuple) -> list[str]:
    # IDEAS: most likely create generics here, assemble in func
    # - select by StrEnum?
    # - inject sort?
    # - a lot of different critera possible...
    #   maybe small config, dto|typeddict combo
    return sorted(cls.__name__ for cls in classes)


#  LINE: -- stammbaum, ftree? -- -- - -- -- - -- -- - -- -- - -- -- - -- --


# IDEA: find or build trees depending on need
# - find routes, nodes, forkes, and do something with that
def all_common_ancestors(cls1, cls2) -> set[type]:
    """Convert MROs to sets and find intersection"""
    # TASK: find ancestor
    # - here is like the maximum
    common: set[type] = set(cls1.__mro__) & set(cls2.__mro__)
    common.discard(object)
    return common


# IDEA: 1 functor that provides entire setup


def closest_common_ancestor(cls1, cls2) -> type | None:
    # TASK: find ancestor
    # - here is like the minimum
    """Iterate cls1 upwards and check if exists in cls2"""

    # AI_QUESTION: Are cls1/cls2 are interchangeable

    cls2_mro: set[type] = set(cls2.__mro__)  # Convert to set for O(1) lookups
    for cls in cls1.__mro__:
        if cls in cls2_mro and cls is not object:
            return cls
    return None


def get_all_descendants(base_cls) -> set[type]:
    # IMPORTANT:
    """Find all classes that inherit from base_cls"""

    descendants: set[type] = set()

    def walk_subclasses(cls):
        for sub_cls in cls.__subclasses__():
            if sub_cls not in descendants:
                descendants.add(sub_cls)
                walk_subclasses(sub_cls)

    walk_subclasses(base_cls)

    return descendants
