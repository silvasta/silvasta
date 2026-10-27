"""
Reference the Implementations back to their Definitions in the port

- Link and Sync docstrings at import time
  - Use docstring from sstcore.port as Single-Source-of-Truth (SSoT)
  - Append optional local docstring with implementation details

- Provide simple IDE navigation hook like in nvim: 'gd'

- Trigger static type checker warning on implementation mismatch

                                    DependencyLevel.sstcore.port[4]
"""

__all__: list[str] = [
    "PortLink",
    "portlink",
    "Tap",
    "tap",
    "LinkSpec",
    "spec",
    # definitions
    "Reflecting",
    "Detecting",
    "Collecting",
    "Projecting",
    "Redacting",
    "DocMerging",
    # rendering
    "PortPrinter",
    "PortEmit",
    "RenderTheme",
    "DefaultTheme",
    "LinkInput",
    "Param",
    # data
    "Doc",
    "PortDoc",
    "PlugDoc",
    "Side",
    "PortLinkStore",
    "PortLinkCollect",
    "PortLinkData",
    "LinkRegistry",
]


import dataclasses as _dc
import typing as _t

from ..empty import VOID, MayBe
from ._control import LinkSpec, Tap
from ._define import (
    Collecting,
    DefaultTheme,
    Detecting,
    Doc,
    DocMerging,
    LinkInput,
    LinkRegistry,
    Param,
    PlugDoc,
    PortDoc,
    PortEmit,
    PortLinkCollect,
    PortLinkData,
    PortLinker,
    PortLinkStore,
    Projecting,
    Redacting,
    Reflecting,
    RenderTheme,
    Side,
)
from ._operate import Reflector, schema1


@_dc.dataclass(frozen=True, slots=True)
class PortLink:
    """Anchor an Implementation to its Protocol"""

    tap: Tap
    registry: LinkRegistry

    @classmethod
    def boot(
        cls, tap: MayBe[Tap] = VOID, registry: MayBe[LinkRegistry] = VOID
    ) -> _t.Self:
        """Launch empty with Defaults"""
        return cls(
            tap=Tap(LinkSpec(merge=schema1)) if tap is VOID else tap,
            registry=LinkRegistry() if registry is VOID else registry,
        )

    @property
    def spec(self) -> LinkSpec:
        """Always read the active frozen LinkSpec directly from Tap."""
        return self.tap.spec

    def __str__(self):
        return f"{type(self).__name__}[4.1]"

    def show(self):
        """Display Registry Overview if active Printer in Tap"""
        self.tap.printer.overview(self, self.registry)

    def evolve(self, **changes: _t.Unpack[LinkInput]) -> _t.Self:
        """Spawn new PortLink with isolated derived Tap"""
        return _dc.replace(self, tap=self.tap.spawn(**changes))

    def __call__[C, P](self, protocol: type[P], /) -> PortLinker[C, P]:
        """Merge docstrings and enforce static type check"""

        def portlinker(cls: type[C & P]) -> type[C]:  # ty:ignore (experimental-syntax)
            """Catch all __doc__ merge issues and always return original Cls"""

            with Reflector(config=self.tap) as reflect:
                self.tap.printer.panel("Start of Reflector")
                self.tap.printer(protocol)
                self.tap.printer(cls)
                with reflect.detector.on(mode="hard") as detect:
                    local_data: PortLinkStore = (
                        detect.portlinks(cls) or PortLinkStore()
                    )

                if protocol in local_data:
                    return cls

                task_data: PortLinkCollect = local_data.edit()

                for attr in self.spec.surface(protocol):
                    attr_data: PortLinkCollect = reflect.collector(
                        protocol, cls, attr
                    )
                    target: type | None = reflect.collector.nearest_target
                    attr_doc: str = reflect.redactor(attr_data[attr])

                    if target is None or not attr_doc:
                        continue

                    with reflect.projector.on(mode="soft") as project:
                        project.doc(target, attr_doc)
                        task_data.absorb(attr_data)  # absorb on inject success

                with reflect.projector.on(mode="hard") as project:
                    final_data: PortLinkStore = task_data.save()
                    project.portlinks(cls, final_data)
                    self.registry.register(port=protocol, plug=cls)

            return self.tap.trace(cls)

        return portlinker


portlink: PortLink = PortLink.boot()  # TARGET: the main object

tap: Tap = portlink.tap  # TARGET: debug probe without protocol matching
