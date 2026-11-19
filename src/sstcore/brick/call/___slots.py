from typing import Any


def get_slots(target) -> dict[str, Any]:
    result = {}
    for cls in type(target).__mro__:
        slots = cls.__dict__.get("__slots__", ())
        if isinstance(slots, str):
            slots = (slots,)
        for slot in slots:
            if slot in ("__dict__", "__weakref__"):
                continue
            if slot.startswith("__") and not slot.endswith("__"):
                slot = f"_{cls.__name__.lstrip('_')}{slot}"
            if hasattr(target, slot):
                result[slot] = getattr(target, slot)
    return result


def simple_slots(target):
    return {name: getattr(target, name) for name in target.__slots__}
