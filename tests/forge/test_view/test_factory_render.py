from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from sstcore.brick.color.box import Colors
from sstcore.forge.view.factory import TableViewDTO, dto_factory
from sstcore.forge.view.render import DtoRenderHub
from sstcore.util.print import Boxes as Boxes  # needed to fill registry


def test_dto_factory_producers():
    """dto_factory produces properly typed EventDTO instances."""
    log_dto = dto_factory.log("system booted", level="INFO", metrics={"ms": 12})
    assert log_dto.name == "log"
    assert log_dto.metainfo() == {"ms": 12}

    panel_dto = dto_factory.panel("hello", "world", topic="Status")
    assert panel_dto.name == "panel"
    assert panel_dto.frame.topic == "Status"

    md_dto = dto_factory.md("## Header", maxlen=120)
    assert md_dto.name == "markdown"
    assert md_dto.maxlen == 120

    line_dto = dto_factory.line("first", "second")
    assert line_dto.name == "line"
    assert line_dto.content == ("first", "second")


def test_dto_factory_table_builders():
    """TableDtoProducer builds TableViewDTOs from all supported shapes."""
    t_matrix = dto_factory.table.matrix([["a", "b"], ["c", "d"]])
    assert isinstance(t_matrix, TableViewDTO)
    assert t_matrix.content == (("a", "b"), ("c", "d"))

    t_kv = dto_factory.table.kv({"host": "localhost", "port": 8080})
    assert t_kv.col_names == ("Key", "Value")
    assert t_kv.content == (("host", "localhost"), ("port", 8080))

    t_cols = dto_factory.table.cols({"id": [1, 2], "tag": ["x", "y"]})
    assert t_cols.col_names == ("id", "tag")
    assert t_cols.content == ((1, "x"), (2, "y"))

    t_records = dto_factory.table.records([{"a": 1, "b": 2}, {"a": 3, "b": 4}])
    assert t_records.col_names == ("a", "b")
    assert t_records.content == (("1", "2"), ("3", "4"))


def test_dto_render_hub_dispatch():
    """DtoRenderHub dispatches EventDTOs to their Rich visualizers."""
    hub = DtoRenderHub(colors=Colors())

    log_render = hub(dto_factory.log("ok", metrics={"k": 1}))
    assert isinstance(log_render, (Text, Tree))

    panel_render = hub(dto_factory.panel("body"))
    assert isinstance(panel_render, Panel)

    md_render = hub(dto_factory.md("# Title"))
    assert isinstance(md_render, Markdown)

    table_render = hub(dto_factory.table.kv({"a": "b"}))
    assert isinstance(table_render, Table)
