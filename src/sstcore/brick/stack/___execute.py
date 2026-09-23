"""
DERIVE EXAMPLE USAGE HERE

- Temporary until ready to move to proper place

"""

from typing import Any

from sstcore.brick.stack.___define import StackingLayer

from . import ___data as data
from . import ___define as port
from . import _stack as stack


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


ansi_stack: stack.StackCore[[str, Any], str, str] = stack.StackCore(
    stack.StackLayer(
        data.ANSI_COLORS,
        mode=port.LayerMode.SINGLE,
        name="color",
    ),
    stack.StackLayer(
        data.ANSI_MODIFIERS,
        mode=port.LayerMode.MULTI,
        name="modifiers",
    ),
    name="colorize",
    executor=color_executor,
)


def dto_applicator(
    state: dict[str, Any], target: str, context: Any = None
) -> str:
    string = f"{target} says {state.get('greeting')} to Peter"
    for _ in range(state.get("repeats", 1)):
        print(string)
    if state.get("formatter"):
        string = state["formatter"](string)
    return string


layers: tuple[port.StackingLayer, ...] = (
    stack.StackLayer(data.ATTR1, "repeats"),
    stack.StackLayer(data.ATTR2, "greeting"),
    stack.StackLayer(data.ATTR3, "formatter"),
)


class DtoStack(stack.StackCore):
    # FIX: self.state
    def __call__(self, target: str, context: Any = None) -> str:
        string = f"{target} says {self.state.get('greeting')} to Peter"
        for _ in range(self.state.get("repeats", 1)):
            print(string)
        if self.state.get("formatter"):
            string = self.state["formatter"](string)
        return string


dto_stack: port.StackingCore = DtoStack(*layers)


def pipeline_applicator(state: dict, text: str, context: Any = None) -> str:
    result = text
    for transform in state.get("transforms", ()):
        result = transform(result)
    return result


type Stack = StackingLayer[str]

sanitizers: Stack = stack.StackLayer(data.SANITIZERS, "sanitize")
normalizers: Stack = stack.StackLayer(data.NORMALIZERS, "normalize")
formatters: Stack = stack.StackLayer(data.FORMATTERS, "format")
colorizers: Stack = stack.StackLayer(data.ANSI_COLORS, "color")

string_pipeline: port.StackingCore = stack.StackCore(
    sanitizers,
    normalizers,
    formatters,
    colorizers,
    name="string_pipeline",
    executor=pipeline_applicator,
)
