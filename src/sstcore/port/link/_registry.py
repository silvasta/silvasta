from collections.abc import Iterator
from dataclasses import dataclass, field
from weakref import WeakKeyDictionary, WeakSet


@dataclass(slots=True)
class PortRegistry:
    """
    Weak M:N topological index of (Protocol <-> Implementation) links.

    Acts as a passive observer now; extensible for retroactive passes later.
    """

    # Maps Protocol -> WeakSet of Implementation classes
    _by_port: WeakKeyDictionary[type, WeakSet[type]] = field(
        default_factory=WeakKeyDictionary, init=False, repr=False
    )

    # LATER: decide if both directions tracked, or 1 is constructed when needed

    # Maps Implementation -> WeakSet of Protocol classes
    _by_plug: WeakKeyDictionary[type, WeakSet[type]] = field(
        default_factory=WeakKeyDictionary, init=False, repr=False
    )

    def register(self, port: type, plug: type) -> None:
        """Record a direct @portlink(port) application on plug."""
        if port not in self._by_port:
            self._by_port[port] = WeakSet()
        self._by_port[port].add(plug)

        if plug not in self._by_plug:
            self._by_plug[plug] = WeakSet()
        self._by_plug[plug].add(port)

    # --- Read-Only Queries & Snapshots (Safe from GC iteration errors) ---

    def ports(self) -> tuple[type, ...]:
        """All currently alive Protocols that have at least one implementation."""
        return tuple(p for p, plugs in self._by_port.items() if len(plugs) > 0)

    def plugs(self) -> tuple[type, ...]:
        """All currently alive decorated Implementation classes."""
        return tuple(c for c, ports in self._by_plug.items() if len(ports) > 0)

    def links(self) -> Iterator[tuple[type, type]]:
        """Yield all active (port, plug) pairs."""
        for port, plugs in list(self._by_port.items()):
            for plug in tuple(plugs):
                yield (port, plug)

    def implementations_of(self, port: type) -> tuple[type, ...]:
        """Return all implementations linked to a specific Protocol."""
        plugs = self._by_port.get(port)
        return tuple(plugs) if plugs is not None else ()

    def protocols_of(self, plug: type) -> tuple[type, ...]:
        """Return all Protocols directly linked to a specific Implementation."""
        ports = self._by_plug.get(plug)
        return tuple(ports) if ports is not None else ()

    def stats(self) -> dict[str, int]:
        """Quick telemetry summary."""
        active_links = sum(len(plugs) for plugs in self._by_port.values())
        return {
            "ports": len(self.ports()),
            "plugs": len(self.plugs()),
            "links": active_links,
        }
