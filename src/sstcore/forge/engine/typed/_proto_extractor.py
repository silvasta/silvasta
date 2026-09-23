import inspect
from typing import get_type_hints

from ....port.annotate import MethodDTO, ParamDTO, StubJobDTO


class ProtoExtractor:
    """Extracts structural metadata from Python types/protocols."""

    @classmethod
    def extract(cls, target: type, name: str | None = None) -> StubJobDTO:
        name = name or target.__name__.replace("Protocol", "Stub")
        hints = get_type_hints(target)

        attributes = {}
        methods = []

        # 1. Extract Properties & Attributes
        for attr, typ in hints.items():
            if attr.startswith("__"):
                continue
            if not callable(typ):
                attributes[attr] = (
                    typ.__name__ if hasattr(typ, "__name__") else str(typ)
                )

        # 2. Extract Methods
        for m_name, func in inspect.getmembers(target, inspect.isfunction):
            if m_name.startswith("__"):
                continue
            sig = inspect.signature(func)

            params = [
                ParamDTO(p.name, str(p.annotation).replace("~", ""))
                for p in sig.parameters.values()
                if p.name != "self"
            ]

            methods.append(
                MethodDTO(
                    name=m_name,
                    params=params,
                    return_type=str(sig.return_annotation),
                )
            )

        # This returns PURE DATA, easy to pass to a bus or registry
        return StubJobDTO(
            target_module=target.__module__,
            class_name=name,
            methods=methods,
            attributes=attributes,
        )
