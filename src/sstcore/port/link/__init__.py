"""
Reference the Implementations back to their Definitions in the port

- Link and Sync docstrings at import time
  - Use docstring from sstcore.port as Single-Source-of-Truth (SSoT)
  - Append optional local docstring with implementation details

- Provide simple IDE navigation hook like in nvim: 'gd'

- Trigger static type checker warning on implementation mismatch

                                    DependencyLevel.sstcore.port[4]
                                    (drop to 1? remove enums would be enough)
"""

__all__: list[str] = [
    "portlink",
    "PortLink",
    "LinkSpec",
    "spec",
    "tap",
    "Tap",
    # definitions
    "PortLinker",
    "Reflecting",
    "Injecting",
    "Collecting",
    "PortEmit",
    "DocMerger",
    # rendering
    "MergeMachine",
    # __doc__
    "PortLinkStore",
    "PortLinkCollect",
    "PortLinkData",
    "SidePolicy",
    # dto
    "Doc",
    "PortDoc",
    "PlugDoc",
]


import typing as _t
from dataclasses import dataclass as _dataclass
from dataclasses import field as _field
from dataclasses import replace as _replace

from ._control import LinkSpec, Tap
from ._define import (
    Doc,
    LinkInput,
    LinkRegistry,
    PlugDoc,
    PortDoc,
    PortEmit,
    PortLinkCollect,
    PortLinkData,
    PortLinker,
    PortLinkStore,
    SidePolicy,
)
from ._operate import Reflector, schema1

spec = LinkSpec(merge=schema1)
tap = Tap(spec=spec)
registry = LinkRegistry()


@_dataclass(frozen=True, slots=True)
class PortLink:
    """Anchor an Implementation to its Protocol"""

    spec: LinkSpec = _field(default_factory=lambda: spec)
    tap: Tap = _field(default_factory=lambda: tap)
    registry: LinkRegistry = _field(default_factory=lambda: registry)

    def __str__(self):
        return f"{type(self).__name__}[4]"

    def show(self):
        """Display Registry Overview if active Printer in Spec"""
        self.spec.printer.overview(self, self.registry)

    def evolve(self, **changes: _t.Unpack[LinkInput]) -> _t.Self:
        """Spawn a new PortLink with a derived LinkSpec and bound Tap."""
        new_spec: LinkSpec = self.spec.derive(**changes)
        return _replace(self, spec=new_spec, tap=Tap(spec=new_spec))

    def configure(self, **changes: _t.Unpack[LinkInput]) -> _t.Self:
        """Mutate shared LinkSpec (and Tap) in-place."""
        self.spec.configure(**changes)
        return self

    def __call__[C, P](self, protocol: type[P], /) -> PortLinker[C, P]:
        """Merge docstrings and enforce static type check"""

        def portlinker(cls: type[C & P]) -> type[C]:  # ty:ignore (experimental-syntax)
            """Catch all __doc__ merge issues and always return original Cls"""

            with Reflector(spec=self.spec) as reflect:
                self.spec.printer.panel("Start of Reflector")
                self.spec.printer(protocol)
                self.spec.printer(cls)
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


portlink = PortLink()  # TARGET: the main object
