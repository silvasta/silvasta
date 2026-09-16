from collections.abc import Callable
from typing import Any, overload

from ._composer import MixinComposer


class MixInjector:
    """Generic Routing Layer for Decorators."""

    def __init__(self, default_composer: MixinComposer):
        self.default_composer = default_composer

    def configure_composer(self, *args: Any, **kwargs: Any) -> MixinComposer:
        """
        OVERRIDE THIS IN SUBCLASSES (like ViewInjector)

        Takes decorator arguments and returns a newly configured MixinComposer.
        For generic usage, it just returns the default.
        """
        return self.default_composer

    @overload
    def __call__(self, target: type, /) -> type: ...
    @overload
    # FIX:
    # FIX:
    # FIX:
    # FIX:
    # FIX:
    # FIX:
    def __call__(
        self, *args: Any, **kwargs: Any
    ) -> Callable[[type], type]: ...

    def __call__(
        self, *args: Any, **kwargs: Any
    ) -> type | Callable[[type], type]:
        # 1. Bare decorator: @injector
        if len(args) == 1 and isinstance(args[0], type) and not kwargs:
            target_cls = args[0]
            return self.default_composer.mix(target_cls)

        # 2. Decorator with arguments: @injector(preset="fast")
        def class_wrapper(target_cls: type) -> type:
            custom_composer = self.configure_composer(*args, **kwargs)
            return custom_composer.mix(target_cls)

        return class_wrapper
