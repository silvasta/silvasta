from contextlib import suppress
from enum import StrEnum, auto
from pathlib import Path

from loguru import logger

from ..path import PathGuard
from ..print import printer


def write_summary_file(
    files: list[Path], output_file: Path, local_root: Path | None = None
) -> str:
    """Assemble summary file and write to disk, incremented if needed"""
    data: str = assemble_summary_file(files, output_file, local_root)
    PathGuard.unique(output_file).write_text(data)
    return data


def assemble_summary_file(
    files: list[Path],
    output_file: Path,
    local_root: Path | None = None,
) -> str:
    """
    Get target by output_file path, load files, wrap content, combine.

    - output_file is for identifying target type
    - local_root is for creating the relative paths inside the summary

    """
    files = [file for file in files if file.is_absolute()]

    # FIX: somehow got:
    # ╭─────────────────────────── Selected Files ───────────────────────────╮
    # │ Selected Files: 13                                                   │
    # ╰──────────────────────────────────────────────────────────────────────╯
    # ╭───────────────────────────────────────────────────── Selected Files ─╮
    # │ ./                                                                   │
    # │ /home/silvan/manuals/dot/zsh/custom/aliases.zsh                      │
    # │ /home/silvan/manuals/dot/zsh/custom/completions/                     │
    # │ /home/silvan/manuals/dot/zsh/custom/completions/_alacritty           │
    # │ /home/silvan/manuals/dot/zsh/custom/completions/_btm                 │
    # │ /home/silvan/manuals/dot/zsh/custom/completions/_cargo               │
    # │ /home/silvan/manuals/dot/zsh/custom/completions/_ftdv                │
    # │ /home/silvan/manuals/dot/zsh/custom/completions/_rustup              │
    # │ /home/silvan/manuals/dot/zsh/custom/completions/_sachmis             │
    # │ /home/silvan/manuals/dot/zsh/custom/example.zsh                      │
    # │ /home/silvan/manuals/dot/zsh/custom/functions.zsh                    │
    # │ /home/silvan/manuals/dot/zsh/custom/plugins/example/example.plugin.z │
    # │ sh                                                                   │
    # │ /home/silvan/manuals/dot/zsh/custom/themes/pygmalion-s.zsh-theme     │
    # ╰──────────────────────────────────────────────────────────────────────╯
    # ./
    # /home/silvan/manuals/dot/zsh/custom/aliases.zsh
    # /home/silvan/manuals/dot/zsh/custom/completions/
    # /home/silvan/manuals/dot/zsh/custom/completions/_alacritty
    # /home/silvan/manuals/dot/zsh/custom/completions/_btm
    # /home/silvan/manuals/dot/zsh/custom/completions/_cargo
    # /home/silvan/manuals/dot/zsh/custom/completions/_ftdv
    # /home/silvan/manuals/dot/zsh/custom/completions/_rustup
    # /home/silvan/manuals/dot/zsh/custom/completions/_sachmis
    # /home/silvan/manuals/dot/zsh/custom/example.zsh
    # /home/silvan/manuals/dot/zsh/custom/functions.zsh
    # /home/silvan/manuals/dot/zsh/custom/plugins/example/example.plugin.zsh
    # /home/silvan/manuals/dot/zsh/custom/themes/pygmalion-s.zsh-theme
    # zsh.xml
    # None
    #     #PosixPath('/home/silvan/manuals/dot/zsh/custom/aliases.zsh'), PosixPath('/home/silvan/manuals/dot/zsh/custom...
    #                      │         └ <staticmethod(<function split_read_print_path at 0x78222e107530>)>
    #                      └ <class 'sstcore.utils.path.pathguard.PathGuard'>
    #
    #   File "/home/silvan/.local/share/uv/python/cpython-3.14.5-linux-x86_64-gnu/lib/python3.14/functools.py", line 982, in wrapper
    #     return dispatch(args[0].__class__)(*args, **kw)
    #            │        │                   │       └ {}
    #            │        │                   └ ([PosixPath('.'), PosixPath('/home/silvan/manuals/dot/zsh/custom/aliases.zsh'), PosixPath('/home/silvan/manuals/dot/zsh/custo...
    #            │        └ ([PosixPath('.'), PosixPath('/home/silvan/manuals/dot/zsh/custom/aliases.zsh'), PosixPath('/home/silvan/manuals/dot/zsh/custo...
    #            └ <function singledispatch.<locals>.dispatch at 0x78222e107320>
    #
    #   File "/home/silvan/PolyBox/Code/sstcore/latest/src/sstcore/utils/path/pathguard/_helper.py", line 84, in _
    #     return [split_read_print_path(path, local_root) for path in target]
    #             │                           │                       └ [PosixPath('.'), PosixPath('/home/silvan/manuals/dot/zsh/custom/aliases.zsh'), PosixPath('/home/silvan/manuals/dot/zsh/custom...
    #             │                           └ None
    #             └ <function split_read_print_path at 0x78222e107530>
    #
    #   File "/home/silvan/.local/share/uv/python/cpython-3.14.5-linux-x86_64-gnu/lib/python3.14/functools.py", line 982, in wrapper
    #     return dispatch(args[0].__class__)(*args, **kw)
    #            │        │                   │       └ {}
    #            │        │                   └ (PosixPath('.'), None)
    #            │        └ (PosixPath('.'), None)
    #            └ <function singledispatch.<locals>.dispatch at 0x78222e107320>
    #
    #   File "/home/silvan/PolyBox/Code/sstcore/latest/src/sstcore/utils/path/pathguard/_helper.py", line 99, in _
    #     raise ValueError(msg)
    #                      └ "Relative Path not possible: local_root=None and target=PosixPath('.')"
    #
    # ValueError: Relative Path not possible: local_root=None and target=PosixPath('.')
    summary: SummaryFileBox = SummaryFileBox.type_from_path(output_file)

    parts: list[str] = [summary.start()]

    for path_pair in PathGuard.split_read_print_path(files, local_root):
        read_path, print_path = path_pair

        if read_path.is_file():
            with suppress(UnicodeDecodeError):
                content: str = read_path.read_text(encoding="utf-8")
                parts.append(summary.wrap(content, print_path))

    parts += [summary.end_part()]

    logger.debug(f"assembled {len(parts)=}")

    return "\n\n".join(parts) if parts else "\n\n"


class SummaryFileBox(StrEnum):
    """Provide parts for Summary selection without missing any"""

    MD = auto()
    XML = auto()
    TXT = auto()

    def start(self) -> str:
        """First Line of Summary File"""
        match self:
            case SummaryFileBox.MD:
                return "## Code Base"
            case SummaryFileBox.XML:
                return "<codebase>"
            case SummaryFileBox.TXT:
                return ""

    def wrap(self, content: str, path: Path) -> str:
        """Assemble Main Part with Content"""
        match self:
            case SummaryFileBox.MD:
                return _wrap_for_md(path, content)
            case SummaryFileBox.XML:
                return f'  <file path="{path}">\n{content}\n  </file>'
            case SummaryFileBox.TXT:
                return f"--- file_path: {path} ---\n{content}"

    def end_part(self) -> str:
        """Last Line to close the Context"""
        match self:
            case SummaryFileBox.MD | SummaryFileBox.TXT:
                return ""
            case SummaryFileBox.XML:
                return "</codebase>"

    @classmethod
    def type_from_path(cls, output_file: Path) -> SummaryFileBox:
        """Match the Output file to the available types"""
        try:
            return cls(output_file.suffix.strip("."))
        except ValueError:
            printer.danger(["Unknown file type of output_file:", output_file])
            return SummaryFileBox.TXT


# ------------------------------------------------------------------ #
# Helper for Markdown content wrapper
# ------------------------------------------------------------------ #


def _wrap_for_md(path: Path, content: str) -> str:
    match path.suffix:
        case ".rs":
            return _rust(path, content)
        case ".tex" | ".cls":
            return _tex(path, content)
        case ".py" | ".pyi":
            return _py(path, content)
        case ".lua":
            return _lua(path, content)
        case _:
            return _txt(path, content)


# NOTE: at the next _type attach i will clean this up!


def _py(path, content):
    return f"""
```python
# {path}
{content}
```
"""


def _rust(path, content):
    return f"""
```rust
// {path}
{content}
```
"""


def _lua(path, content):
    return f"""
```lua
-- {path}
{content}
```
"""


def _tex(path, content):
    return f"""
```tex
% {path}
{content}
```
"""


def _txt(path, content):
    return f"""
```
{path}
{content}
```
"""
