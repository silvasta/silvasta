"""
DERIVE EXAMPLE USAGE HERE

- Temporary until ready to move to proper place

"""

__all__: list[str] = [
    "dto_stack",
]


from typing import Any

from ...port.stacking import LayerMode, StackingCore, StackingLayer
from . import _test_data as data
from ._stack import StackCore, StackLayer


def color_executor(text: str, color: Any) -> str:
    """Example Application, ColorBox will look different"""
    codes = list(color.modifiers)
    if color:
        # Simplified for example
        clean_code = color[2:-1]
        codes.append(clean_code)

    if not codes:
        return text

    prefix = f"\033[{';'.join(codes)}m"
    return f"{prefix}{text}\033[0m"


ansi_stack: StackCore = StackCore(
    StackLayer(
        data.ANSI_COLORS,
        mode=LayerMode.SINGLE,
        name="color",
    ),
    StackLayer(
        data.ANSI_MODIFIERS,
        mode=LayerMode.MULTI,
        name="modifiers",
    ),
    name="colorize",
    call=color_executor,
)


def dto_applicator(
    state: dict[str, Any],
    target: str,
) -> str:
    string = f"{target} says {state.get('greeting')} to Peter"
    for _ in range(state.get("repeats", 1)):
        print(string)
    if state.get("formatter"):
        string = state["formatter"](string)
    return string


layers: tuple[StackingLayer, ...] = (
    StackLayer(data.ATTR1, "repeats"),
    StackLayer(data.ATTR2, "greeting"),
    StackLayer(data.ATTR3, "formatter"),
)


class DtoStack(StackCore):
    """Waiting for __call__"""

    # FIX: pipeline with call/__call__
    # def __call__(self, target: str, context: Any = None) -> str:
    #     string = f"{target} says {self.state.get('greeting')} to Peter"
    #     for _ in range(self.state.get("repeats", 1)):
    #         print(string)
    #     if self.state.get("formatter"):
    #         string = self.state["formatter"](string)
    #     return string


dto_stack: StackingCore = DtoStack(*layers, name="dto", call=dto_applicator)


def pipeline_applicator(state: dict, text: str, context: Any = None) -> str:
    result = text
    for transform in state.get("transforms", ()):
        result = transform(result)
    return result


type Stack = StackingLayer[str]

sanitizers: StackingLayer = StackLayer(data.SANITIZERS, "sanitize")
normalizers: StackingLayer = StackLayer(data.NORMALIZERS, "normalize")
formatters: StackingLayer = StackLayer(data.FORMATTERS, "format")
colorizers: StackingLayer = StackLayer(data.ANSI_COLORS, "color")

string_pipeline: StackingCore = StackCore(
    sanitizers,
    normalizers,
    formatters,
    colorizers,
    name="string_pipeline",
    call=pipeline_applicator,
)
