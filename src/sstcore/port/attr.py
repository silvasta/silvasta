"""
Define the Shape of Descripors

-
"""

from typing import Any, Protocol


class EventAwareDescriptor(Protocol):
    def attach_bus(self, bus) -> None: ...


### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --
### Implementations
### -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- -- - -- -- --


class _Ideas:
    def __set_name__(self, owner, name):
        self.private_name = f"_{name}"

    def __delete__(self, instance):
        # Instead of deleting, reset to a default or mark as deleted
        setattr(instance, self.private_name, "Guest")

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        if not hasattr(instance, self.private_name):
            raise AttributeError(
                f"Attribute '{self.private_name[1:]}' has been deleted or not set."
            )
        return getattr(instance, self.private_name)


class BaseDescriptor:
    config: dict[str, Any] = {"max_length": 255}

    def __init__(self, config_key):
        self.config_key = config_key

    def __set_name__(self, owner, name):
        self.private_name = f"_{name}"

    def __set__(self, instance, value):
        # 1. Base class handles the config check
        if self.config.get("readonly"):
            raise TypeError("Read only!")

        # 2. Child class handles specific validation
        value = self.validate(value)

        # 3. Base class handles the actual storage
        setattr(instance, self.private_name, value)

        ### SECOND
        limit = self.config.get(self.config_key)
        if limit is not None and len(value) > limit:
            raise ValueError(f"Exceeded {limit}")

    def validate(self, value):
        return value  # Child classes override this


class ValidatingDescriptor(BaseDescriptor):
    def __set__(self, instance, value):
        limit = self.config.get("max_length")


class Forward:
    """A descriptor that forwards method calls to an inner attribute."""

    def __init__(self, target_attr, method_name):
        self.target_attr = target_attr
        self.method_name = method_name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        target = getattr(instance, self.target_attr)
        return getattr(target, self.method_name)


class Worker:
    def __init__(self):
        self._registry = SpecializedListRegistry()

    # Explicitly map the methods you want to expose
    register = Forward("_registry", "register")
    get_task = Forward("_registry", "get")
    clear = Forward("_registry", "clear")


x = Worker()
y = x.get_task


class RegistryField:
    """A descriptor that automatically attaches a registry to an instance."""

    def __init__(self, registry_cls, *args, **kwargs):
        self.registry_cls = registry_cls
        self.args = args  # REMOVE: ?
        self.kwargs = kwargs  # REMOVE: ?

    def __set_name__(self, owner, name):
        self.private_name = f"_{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self

        # Lazy initialization on the host instance
        if not hasattr(instance, self.private_name):
            setattr(
                instance,
                self.private_name,
                self.registry_cls(*self.args, **self.kwargs),
            )
        return getattr(instance, self.private_name)


class PathHandler:
    # Look how clean this attach is! No __init__ required.
    paths = RegistryField(ListRegistry, type=Path)
