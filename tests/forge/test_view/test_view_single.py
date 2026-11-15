from pathlib import Path

from sstcore.forge.view import Cli, Log, Repr, Rich, Str, view
from sstcore.port.event.dto import (
    LineDTO,
    LogDTO,
    MarkdownDTO,
    PanelDTO,
    TableDTO,
)
from sstcore.port.represent import (
    CliSerializable,
    LogSerializable,
    RichView,
)


def test_single_cli_panel():
    @view(Cli.PANEL)
    class Boxed:
        name = "test_panel"

    obj = Boxed()
    assert isinstance(obj, CliSerializable)
    dto = obj.__cli__()
    assert isinstance(dto, PanelDTO)
    assert any("test_panel" in str(item) for item in dto.content)


def test_single_cli_markdown():
    @view(Cli.MARKDOWN)
    class DocItem:
        _markdown_text = "# Hello Markdown"

    obj = DocItem()
    assert isinstance(obj, CliSerializable)
    dto = obj.__cli__()
    assert isinstance(dto, MarkdownDTO)
    assert dto.content == "# Hello Markdown"


def test_single_cli_paths(tmp_path: Path):
    @view(Cli.PATHS)
    class PathHolder:
        @property
        def _panel_paths(self) -> list[Path]:
            return [tmp_path]

    obj = PathHolder()
    assert isinstance(obj, CliSerializable)
    dto = obj.__cli__()
    assert isinstance(dto, PanelDTO)
    assert len(dto.content) == 1


def test_single_cli_line():
    """Exposes LineMixin bug if LineDTO is called with unexpected 'style' kwarg."""

    @view(Cli.LINE, Str.SHORT)
    class LineItem:
        pass

    obj = LineItem()
    assert isinstance(obj, CliSerializable)
    dto = obj.__cli__()
    assert isinstance(dto, LineDTO)


def test_single_cli_table():
    """Exposes TableMixin bug if TableDTO.from_row_dicts is missing."""

    @view(Cli.TABLE)
    class TableItem:
        col = "val"

    obj = TableItem()
    assert isinstance(obj, CliSerializable)
    dto = obj.__cli__()
    assert isinstance(dto, TableDTO)


def test_single_str_variants():
    @view(Str.SHORT)
    class ShortStr:
        name = "ignored"

    @view(Str.NAME)
    class NamedStr:
        name = "chosen"

    @view(Str.MODULE)
    class ModStr:
        pass

    assert str(ShortStr()) == "ShortStrView"
    assert str(NamedStr()) == "NamedStrView[chosen]"
    assert str(ModStr()) == __name__


def test_single_repr_variants():
    @view(Repr.BOX)
    class BoxRepr:
        a = 1

    @view(Repr.DATA)
    class DataRepr:
        a = 1

    @view(Repr.DEBUG)
    class DebugRepr:
        def __init__(self) -> None:
            self._secret = 42

    assert repr(BoxRepr()) == "BoxReprView[a=1]"
    assert repr(DataRepr()) == "DataReprView(a=1)"
    assert "_secret=42" in repr(DebugRepr())


def test_single_rich_variants():
    @view(Rich.SHORT)
    class RichShort:
        pass

    @view(Rich.NAME)
    class RichNamed:
        name = "sparkle"

    short_obj = RichShort()
    named_obj = RichNamed()
    assert isinstance(short_obj, RichView)
    assert isinstance(named_obj, RichView)
    assert "RichShortView" in str(short_obj.__rich__())
    assert named_obj.__rich__() == "RichNamedView[sparkle]"


def test_single_log_variants():
    @view(Log.DATA, Str.SHORT)
    class LogDataEntity:
        metric_a = 10

    @view(Log.DEBUG, Str.SHORT)
    class LogDebugEntity:
        def __init__(self) -> None:
            self.runtime_val = 99

    data_obj = LogDataEntity()
    assert isinstance(data_obj, LogSerializable)
    data_dto = data_obj.__log__()
    assert isinstance(data_dto, LogDTO)
    assert data_dto.metrics == {"metric_a": 10}

    debug_obj = LogDebugEntity()
    assert isinstance(debug_obj, LogSerializable)
    debug_dto = debug_obj.__log__()
    assert isinstance(debug_dto, LogDTO)
    assert debug_dto.metrics == {"runtime_val": 99}
