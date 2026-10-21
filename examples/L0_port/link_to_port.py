"""
Test and Show the PortLinker

- Static type check warning on Test 2 and Test 3 must be triggered

"""

from typing import TYPE_CHECKING, Any, Protocol

from sstcore import portlink


class TestProtocol(Protocol):
    """REMOVE: after implementing: @implements decorator"""

    @property
    def side_info(self) -> dict[str, Any]: ...
    @property
    def state(self) -> Any:
        """Task relevant data"""

    def handle(self, order: int) -> str:
        """Transform internal state to text depending on order"""


@portlink(TestProtocol)
class ProperImplementation:
    def __init__(self):
        self.side_info: dict[str, Any] = {}
        self.other = ...

    @property
    def state(self) -> Any:
        _important = self.side_info.get("whatever", None)
        return self._some_process(_important, self.other)

    def _some_process(self, *args, **kwargs):
        raise NotImplementedError(args, kwargs)

    def handle(self, order: int) -> str:
        """Transform internal state to text depending on order"""
        match order:
            # ... fill here
            case _:
                return str(self.state)


g = ProperImplementation()
g.handle(1)
g._some_process()


@portlink(TestProtocol)
class MissingMethodImplementation:
    def __init__(self):
        self.side_info: dict[str, Any] = {}
        self.other = ...

    @property
    def state(self) -> Any:
        raise NotImplementedError


@portlink(TestProtocol)
class TypeFailInSignatureImplementation:
    def __init__(self):
        self.side_info: dict[str, Any] = {}
        self.other = ...

    @property
    def state(self) -> Any:
        raise NotImplementedError

    def handle(self, _order: int) -> list[str]:
        """Transform internal state to text depending on order"""
        raise NotImplementedError


if TYPE_CHECKING:
    _pattern: TestProtocol = ProperImplementation()
    _pattern: TestProtocol = MissingMethodImplementation()
    _pattern: TestProtocol = TypeFailInSignatureImplementation()
