"""
Reference the Implementations back to their Definitions in the port

- Link and Sync docstrings at import time
  - Use docstring from sstcore.port as Single-Source-of-Truth (SSoT)
  - Append optional local docstring with implementation details

- Provide simple IDE navigation hook like in nvim: 'gd'

- Trigger static type checker warning on implementation mismatch

"""

from sstcore.port.link.process import MergeMachine

__all__: list[str] = [
    "portlink",
    "PortLink",
    "LinkSpec",
    "PortLinker",
    "DocMerger",
]

import typing as _t
from dataclasses import dataclass as _dataclass
from dataclasses import replace as _replace

from .config import LinkSpec
from .data import (
    PortLinkDocs,
    PortLinks,
)
from .define import DocMerger, PortLinker
from .operator import PortOperator

_x: DocMerger = MergeMachine.Schema1

spec = LinkSpec(merge=MergeMachine.Schema1)


@_dataclass(frozen=True, slots=True)
class PortLink:
    """Anchor an Implementation to its Protocol"""

    spec: LinkSpec = spec

    def create(self, spec: LinkSpec) -> _t.Self:
        return _replace(self, spec=spec)

    def evolve(self, **spec_overrides) -> _t.Self:
        return _replace(self, spec=self.spec.derive(**spec_overrides))

    def __call__[C, P](self, protocol: type[P], /) -> PortLinker[C, P]:
        """Merge docstrings and enforce static type check"""

        def portlinker(cls: type[C & P]) -> type[C]:  # ty:ignore (experimental-syntax)

            with PortOperator(spec=self.spec) as operator:
                with operator.spawn.reflect(mode="hard") as _reflector:
                    local_data: PortLinkDocs = _reflector.portlinkdocs(cls)

                if protocol in local_data:
                    return cls

                task_data: PortLinks = local_data.edit()

                for attr in spec.surface(protocol):
                    with operator.spawn.collect() as _collector:
                        attr_data: PortLinks = _collector(protocol, cls, attr)
                        target: type | None = _collector.nearest_target

                    attr_doc: str = self.spec.merge(docs=attr_data[attr])

                    if target is None or not attr_doc:
                        continue

                    with operator.spawn.inject(mode="soft") as _injector:
                        _injector.doc(target, attr_doc)
                        task_data.absorb(attr_data)  # absorb on inject success

                with operator.spawn.inject(mode="hard") as _injector:
                    final_data: PortLinkDocs = task_data.save()
                    _injector.portlinkdocs(cls, final_data)

            return cls

        return portlinker


portlink = PortLink()  # TARGET: the main object
