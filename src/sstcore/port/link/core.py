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

from .data import (
    Doc,
    LinkSpec,
    PlugDoc,
    PlugDocs,
    PortDoc,
    PortDocs,
    PortLinkDocs,
    spec,
)
from .define import DocMerger, PortLinker
from .operator import PortOperator
from .process import concat_merger as merger


@_dataclass(frozen=True, slots=True)
class PortLink:
    """Anchor an Implementation to its Protocol"""

    joint: str = "{Implementations}"  # TODO: render config?
    _merge: DocMerger = merger
    spec: LinkSpec = spec  # this as collector for all?

    def merge(self, ports: PortDocs, plugs: PlugDocs, /) -> str:
        return self._merge(ports, plugs)

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
                with operator.spawn.reflect(mode="hard") as _reflector:
                    local_data: PortLinkDocs = _reflector.portlinkdocs(cls)

                if protocol in local_data:
                    return cls

                update_data: list[Doc] = local_data.as_list

                port_docs: list[PortDoc] = _detect(protocol, "")
                plug_docs: list[PlugDoc] = _detect(cls, "")

                update_data.extend(port_docs + plug_docs)
                class_doc: str = self.merge(port_docs, plug_docs)

                with operator.spawn.inject(mode="soft") as _injector:
                    _injector.doc(cls, class_doc)

                for attr in _t.get_protocol_members(protocol):
                    target: _t.Any = _find_attr_value(cls, attr)
                    port_docs: list[PortDoc] = _detect(protocol, attr)
                    plug_docs: list[PlugDoc] = _detect(cls, attr)
                    update_data.extend(port_docs + plug_docs)
                    # TASK: better routing/injection:
                    # - first collect all, then merge and find target
                    # -> insert at first occurence of mro-upwards.__dict__[attr]
                    # - insert __doc__ for sure, __portlinkdocs__ as well, skip them here
                    attr_doc: str = self.merge(port_docs, plug_docs)
                    _inject(target, attr_doc)

                with operator.spawn.inject(mode="hard") as _injector:
                    _injector.portlinkdocs(cls, PortLinkDocs(update_data))

            return cls

        return portlinker


portlink = PortLink()  # TARGET: the main object

# AI: Info: the following functions are placeholder
# - most of single parts are already implemented in the PortOperator family
# - as soon as the core structure in PortLink.__call__ stands, they will be assembled


def _extract(*args, **kwargs):
    raise NotImplementedError


def _inject(*args, **kwargs):
    raise NotImplementedError


def _find_attr_value(*args, **kwargs):
    raise NotImplementedError


def _reflect(*args, **kwargs):
    raise NotImplementedError


def _detect(*args, **kwargs):
    raise NotImplementedError
