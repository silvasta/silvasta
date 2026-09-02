"""
Idea: Detect MRO structure and common ancestors

-
"""


class Mixin:
    pass


class Base:
    pass


class Child(Mixin, Base):
    pass


# print(Child.__mro__)  # results in tuple with classes
# (<class '__main__.Child'>, <class '__main__.Mixin'>, <class '__main__.Base'>, <class 'object'>)


def all_common_ancestors(cls1, cls2) -> set[type]:
    """Convert MROs to sets and find intersection"""
    common: set[type] = set(cls1.__mro__) & set(cls2.__mro__)
    common.discard(object)
    return common


def closest_common_ancestor(cls1, cls2) -> type | None:
    """
    Iterate cls1 upwards and check if exists in cls2

    - Todo: Check if cls1/cls2 are interchangeable
    """
    cls2_mro: set[type] = set(cls2.__mro__)  # Convert to set for O(1) lookups
    for cls in cls1.__mro__:
        if cls in cls2_mro and cls is not object:
            return cls
    return None


def get_all_descendants(base_cls) -> set[type]:
    """Recursively find every class that inherits from base_cls"""
    descendants: set[type] = set()

    def walk_subclasses(cls):
        for sub_cls in cls.__subclasses__():
            if sub_cls not in descendants:
                descendants.add(sub_cls)
                walk_subclasses(sub_cls)

    walk_subclasses(base_cls)
    return descendants


# Example: Find everything that inherits from Exception in Python
error_descendants = get_all_descendants(Exception)
print(len(error_descendants))


def sort_cls_by_name(classes: set | list | tuple) -> list[str]:
    return sorted(cls.__name__ for cls in classes)


def print_lines(items: set | list | tuple) -> None:
    for i in items:
        print(i)


# TODO: check when internal SstErrors are loaded
# print_lines(sort_cls_by_name(get_all_descendants(base_cls=Exception)))


def load_error():
    from sstcore.port.error import Error as Error


load_error()

sst_error_descendants = get_all_descendants(Exception)

print(len(sst_error_descendants))

print_lines(sort_cls_by_name(sst_error_descendants - error_descendants))
