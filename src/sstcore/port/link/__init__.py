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

from typing import Any, Self

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
    PlugDoc,
    PortDoc,
    PortEmit,
    PortLinkCollect,
    PortLinkData,
    PortLinker,
    PortLinkStore,
    PortRegistry,
    SidePolicy,
)
from ._operate import Redactor, Reflector

# IMPORTANT: LingConfig (or its DTO predecessor) will for sure add something here
# - check what can be split from here and LinkSpec to 1 config for both and portlink
tap = Tap()

spec = LinkSpec(merge=Redactor(spec="FAIL"), emit=tap.emit)  # CHECK:

registry = PortRegistry()


@_dataclass(frozen=True, slots=True)
class PortLink:
    """Anchor an Implementation to its Protocol"""

    spec: LinkSpec = spec
    tap: Tap = tap
    registry: PortRegistry = registry

    def evolve(self, **spec_overrides) -> _t.Self:
        return _replace(self, spec=self.spec.derive(**spec_overrides))

    def configure(
        self,
        *,
        env_var: str | None = None,
        toggle: tuple[str, ...] | None = None,
        **spec_overrides: Any,
    ) -> Self:
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
                with reflect.detect(mode="hard") as detector:
                    local_data: PortLinkStore = detector.portlinkdocs(cls)

                if protocol in local_data:
                    return cls

                task_data: PortLinkCollect = local_data.edit()

                for attr in spec.surface(protocol):
                    with reflect.collect(spec="HANDLE THIS INTERN!") as collect:
                        attr_data: PortLinkCollect = collect(
                            protocol, cls, attr
                        )
                        target: type | None = collect.nearest_target

                    # IDEA: just spawn the merger here?
                    # - and find policy that replaces merge, like 1 part of the internal Redactor chain
                    attr_doc: str = self.spec.merge(docs=attr_data[attr])

                    if target is None or not attr_doc:
                        continue

                    with reflect.inject(mode="soft") as projector:
                        projector.doc(target, attr_doc)
                        task_data.absorb(attr_data)  # absorb on inject success

                with reflect.inject(mode="hard") as projector:
                    final_data: PortLinkStore = task_data.save()
                    projector.portlinkdocs(cls, final_data)

            return tap.trace(cls)

        return portlinker


portlink = PortLink()  # TARGET: the main object
