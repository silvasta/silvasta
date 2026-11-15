"""
Paths for Modules

.
"""

from rich import print
from rich.panel import Panel

from sstcore.brick.color import colorize
from sstcore.port.structures import DotPath, ModulePath

dot1: DotPath = DotPath("my.dot.path")
dot2: DotPath = dot1 / "extends.longer"


mp1: ModulePath = ModulePath.parse("sstcore.port.structures:ModulePath")
mp2: ModulePath = mp1 / "_module"
mp3: ModulePath = mp1 / ":DotPath"
mp4: ModulePath = mp1 / "::import_module"

for target in (dot1, dot2, mp1, mp2, mp3, mp4):
    print(Panel(f"{colorize.modules(target)}\n{target!r}"))
