"""
First sketch of a meta resolver

-
"""

_meta_cache = {}


def combine_metas(*bases):
    """
    Merge metaclass and prevente multiple inheritance conflicts

    Usage: class MyClass(Base1, Base2, metaclass=combine_metas(Base1, Base2)):
    """
    # 1. Gather all unique metaclasses from the given base classes
    metas = set(type(b) for b in bases)

    # 2. Remove standard 'type' if custom metaclasses exist
    if type in metas and len(metas) > 1:
        metas.remove(type)

    # 3. Prune redundant metaclasses (those that are ancestors of others in the set)
    # This prevents Python from complaining about duplicate base classes.
    needed_metas = []
    for m1 in metas:
        if not any(issubclass(m2, m1) for m2 in metas if m1 is not m2):
            needed_metas.append(m1)

    # Sort by name for stable caching, then convert to tuple for immutability
    needed_metas = tuple(sorted(needed_metas, key=lambda m: m.__name__))

    # 4. If only one valid metaclass remains, return it directly
    if len(needed_metas) == 1:
        return needed_metas[0]

    # 5. Check cache to avoid polluting memory with duplicate metaclasses
    if needed_metas in _meta_cache:
        return _meta_cache[needed_metas]

    # 6. Dynamically generate the new combined metaclass
    meta_name = "DynamicMeta_" + "_".join(m.__name__ for m in needed_metas)

    # type(name, bases, namespace) creates a new class/metaclass on the fly
    combined_meta = type(meta_name, needed_metas, {})

    _meta_cache[needed_metas] = combined_meta
    return combined_meta


#  TEST: -- XXX -- -- - -- -- - -- -- - -- -- - -- -- - -- --


## --- Setup Two Distinct Metaclasses ---
class MetaX(type):
    def __new__(mcs, name, bases, ns):
        ns["x_tagged"] = True
        return super().__new__(mcs, name, bases, ns)


class MetaY(type):
    def __new__(mcs, name, bases, ns):
        ns["y_tagged"] = True
        return super().__new__(mcs, name, bases, ns)


# --- Setup Two Independent Base Classes ---
class BaseX(metaclass=MetaX):
    pass


class BaseY(metaclass=MetaY):
    pass


# --- The Conflict ---
# class Child(BaseX, BaseY): pass
# ^^^ This raises TypeError: metaclass conflict


# --- The Resolution ---
class Child(BaseX, BaseY, metaclass=combine_metas(BaseX, BaseY)):
    pass


# Test it out:
print(type(Child).__name__)  # Output: DynamicMeta_MetaX_MetaY
print(Child.x_tagged)  # Output: True
print(Child.y_tagged)  # Output: True
