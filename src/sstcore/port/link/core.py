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


def merger(source: str, target: str, /, joint: str = "") -> str:  # TODO: adapt
    return f"""{source}{joint}{target}"""


@_dataclass(frozen=True, slots=True)
class PortLink:
    """Anchor an Implementation to its Protocol"""

    joint: str = "{Implementations}"  # TODO: render config?
    _merge: DocMerger = merger  # CHECK: where, when and how to inject
    spec: LinkSpec = spec

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
                with operator.spawn("reflector")(mode="hard") as _reflect:
                    local_data: PortLinkDocs = _reflect.portlinkdocs(cls)
                # TEST: remove later on
                with operator.spown.reflector(mode="hard") as _reflect:
                    local_data: PortLinkDocs = _reflect.portlinkdocs(cls)

                if protocol in local_data:
                    return cls

                update_data: list[Doc] = local_data.as_list
                port_docs: list[PortDoc] = _detect(protocol, "")
                plug_docs: list[PlugDoc] = _detect(cls, "")
                class_doc: str = self.merge(port_docs, plug_docs)

                with operator.spawn("injector")(mode="hard") as _inject:
                    _inject.portlinkdocs(cls, class_doc)

                update_data.extend(port_docs + plug_docs)

                for attr in _t.get_protocol_members(protocol):
                    target: _t.Any = _find_attr_value(cls, attr)
                    port_docs: list[PortDoc] = _detect(protocol, attr)
                    plug_docs: list[PlugDoc] = _detect(cls, attr)
                    attr_doc: str = self.merge(port_docs, plug_docs)
                    _inject(target, attr_doc)
                    doc_links |= set(port_docs + plug_docs)  # WARN: order!

                with operator.spawn("injector")(mode="hard") as _inject:
                    injector.portlinkdocs(cls, update_data)

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
