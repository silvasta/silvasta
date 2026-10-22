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
from dataclasses import replace as _replace

from ._control import LinkSpec, Tap
from ._define import (
    Doc,
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

tap = Tap()
spec = LinkSpec(emit=tap.emit, printer=tap.printer, merge=schema1)
registry = LinkRegistry()


@_dataclass(frozen=True, slots=True)
class PortLink:
    """Anchor an Implementation to its Protocol"""

    spec: LinkSpec = spec
    tap: Tap = tap
    registry: LinkRegistry = registry

    def __str__(self):
        _id = 4  # LATER: something better
        return f"{type(self).__name__}[{_id}]"

    def print(self):
        self.tap.printer.panel(f"{self}::{self.registry}")
        self.tap.printer.table(dict(self.registry._by_port), False, False)
        self.tap.printer.table(dict(self.registry._by_plug), False, False)

    def evolve(self, **spec_overrides) -> _t.Self:
        return _replace(self, spec=self.spec.derive(**spec_overrides))

    def configure(
        self,
        *,
        env_var: str | None = None,
        toggle: tuple[str, ...] | None = None,
        **spec_overrides: _t.Any,
    ) -> _t.Self:
        """Mutate shared Tap and LinkSpec in-place"""
        if env_var is not None or toggle is not None:
            self.tap.configure(  # TODO: better forwarding
                env_var=env_var or "SST_DEBUG",
                toggle=toggle or (),
            )
        if spec_overrides:
            self.spec.configure(**spec_overrides)
        return self

    def __call__[C, P](self, protocol: type[P], /) -> PortLinker[C, P]:
        """Merge docstrings and enforce static type check"""

        def portlinker(cls: type[C & P]) -> type[C]:  # ty:ignore (experimental-syntax)
            """Catch all __doc__ merge issues and always return original Cls"""

            with Reflector(spec=self.spec) as reflect:
                with reflect.detector(mode="hard") as detect:
                    local_data: PortLinkStore = detect.portlinks(cls)

                if protocol in local_data:
                    return cls

                task_data: PortLinkCollect = local_data.edit()

                for attr in spec.surface(protocol):
                    attr_data: PortLinkCollect = reflect.collector(
                        protocol, cls, attr
                    )
                    target: type | None = reflect.collector.nearest_target
                    attr_doc: str = reflect.redactor(attr_data[attr])

                    if target is None or not attr_doc:
                        continue

                    with reflect.projector.on(mode="soft") as projector:
                        projector.doc(target, attr_doc)
                        task_data.absorb(attr_data)  # absorb on inject success

                with reflect.projector.on(mode="hard") as project:
                    final_data: PortLinkStore = task_data.save()
                    project.portlinks(cls, final_data)

            return tap.trace(cls)

        return portlinker


portlink = PortLink()  # TARGET: the main object
