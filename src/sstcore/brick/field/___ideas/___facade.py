from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ...port.attach import FieldLoader
    from ...util.path.guard._field import DirField
    from . import Forward, LazyField, RequiredField


class MountFacade:
    """
    Universal descriptor attachment point

    Returning Any is the magic trick that stops the type checker
    from complaining when the user assigns this to a typed variable.

    """

    def lazy(self, loader: FieldLoader, **kwargs) -> Any:
        """Mount a value that loads on first access."""
        return LazyField(loader=loader, **kwargs)

    def required(self, types: type | tuple[type, ...], **kwargs) -> Any:
        """Mount an empty placeholder bound to a type."""
        return RequiredField(types=types, **kwargs)

    def forward(self, target_attr: str, method_name: str) -> Any:
        """Mount a direct proxy to an inner component's method."""
        return Forward(target_attr=target_attr, method_name=method_name)

    def dir(self, logic=None, **kwargs) -> Any:
        """Mount a directory guard."""
        return DirField(target=logic, **kwargs)


mount = MountFacade()


def _calculate_cores() -> Any:
    raise NotImplementedError


class AppSystem:
    # 1. Type checker sees 'str', runtime gets RequiredField
    device: str = mount.required(types=str)

    # 2. Type checker sees 'Path', runtime gets the DirField decorator
    @mount.dir
    def cache_dir(self) -> Path:
        return Path("/var/cache/app")

    # 3. Type checker sees 'int', runtime gets LazyField
    total_cores: int = mount.lazy(loader=lambda _: _calculate_cores())
