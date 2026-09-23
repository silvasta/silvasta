"""
DERIVE EXAMPLE USAGE HERE

- Temporary until ready to move to proper place

"""

__all__: list[str] = [
    "ANSI_STACK",
    "DTO_STACK",
    "STRING_STACK",
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


ANSI_STACK: StackCore = StackCore(
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
    greeting = state.get("greeting", [""])[0]
    repeats = state.get("repeats", [1])[0]

    string = f"{target} says {greeting} to Peter"
    for _ in range(repeats):
        print(string)

    if formatter_list := state.get("formatter"):
        string = formatter_list[0](string)

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


DTO_STACK: StackingCore = DtoStack(*layers, name="random", call=dto_applicator)


def pipeline_applicator(state: dict, text: str) -> str:
    result = text
    for transform in state.get("transforms", ()):
        result = transform(result)
    return result


sanitizers: StackingLayer = StackLayer(data.SANITIZERS, "sanitize")
normalizers: StackingLayer = StackLayer(data.NORMALIZERS, "normalize")
formatters: StackingLayer = StackLayer(data.FORMATTERS, "format")
colorizers: StackingLayer = StackLayer(data.ANSI_COLORS, "color")

STRING_STACK: StackingCore = StackCore(
    sanitizers,
    normalizers,
    formatters,
    colorizers,
    name="string_pipeline",
    call=pipeline_applicator,
)
