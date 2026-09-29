"""
Reference the Implementations back to their Definitions in the port

- Link and Sync docstrings at import time
  - Use docstring from sstcore.port as Single-Source-of-Truth (SSoT)
  - Append optional local docstring with implementation details

- Provide simple IDE navigation hook like in nvim: 'gd'

- Trigger static type checker warning on implementation mismatch

"""

__all__: list[str] = [
    "portlink",
    "PortLink",
    # "PortLinker",
    # "DocMerger",
]

import typing as _t
from dataclasses import dataclass as _dataclass
from dataclasses import replace as _replace

from .config import LinkSpec, spec
from .data import (
    Docs,
    PortLinkDocs,
    PortLinks,
)
from .define import DocMerger, PortLinker
from .operator import PortOperator
from .process import merger


@_dataclass(frozen=True, slots=True)
class PortLink:
    """Anchor an Implementation to its Protocol"""

    joint: str = "{Implementations}"  # TODO: render config?
    _merge: DocMerger = merger
    spec: LinkSpec = spec  # this as collector for all?

    def merge(self, docs: Docs) -> str:
        return self._merge(docs)

    def new(
        self, *, merge: DocMerger | None = None, joint: str | None = None
    ) -> _t.Self:
        return _replace(
            self,  # TODO:
            joint=self.joint if joint is None else joint,
            _merge=self._merge if merge is None else merge,
        )

    def __call__[C, P](self, protocol: type[P], /) -> PortLinker[C, P]:
        """Merge docstrings and enforce static type check"""

        def portlinker(cls: type[C & P]) -> type[C]:  # ty:ignore (experimental-syntax)

            with PortOperator() as operator:
                # with PortOperator(# IDEA: self.spec) as operator:
                with operator.spawn.reflect(mode="hard") as _reflector:
                    local_data: PortLinkDocs = _reflector.portlinkdocs(cls)

                if protocol in local_data:
                    return cls

                task_data: PortLinks = local_data.edit()
                targets: set[str] = {"", *_t.get_protocol_members(protocol)}

                for attr in targets:
                    with operator.spawn.collect() as _collector:
                        attr_data: PortLinks = _collector(protocol, cls, attr)
                        if (target := _collector.nearest_target) is None:
                            continue
                        if not (attr_doc := self.merge(attr_data[attr])):
                            continue

                    with operator.spawn.inject(mode="soft") as _injector:
                        _injector.doc(target, attr_doc)
                        task_data.absorb(attr_data)

                with operator.spawn.inject(mode="hard") as _injector:
                    final_data: PortLinkDocs = task_data.save()
                    _injector.portlinkdocs(cls, final_data)

            return cls

        return portlinker


portlink = PortLink()  # TARGET: the main object
