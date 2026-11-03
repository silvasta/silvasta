from pydantic import BaseModel

from sstcore.forge.view import Cli, Log, Repr, Str, view
from sstcore.port.event.dto import LogDTO, PanelDTO
from sstcore.port.represent import (
    CliSerializable,
    LogSerializable,
    is_basemodel,
)


@view(Cli.PANEL, Log.DATA, Str.NAME, Repr.DATA)
class UserModel(BaseModel):
    name: str = "alice"
    score: int = 100


@view.pydantic.plus(Cli.PANEL, Repr.BOX)
class PresetModel(BaseModel):
    x: int
    y: str


def test_pydantic_custom_view():
    """Pydantic models preserve validation, dumping, and injected views."""
    user = UserModel()
    assert is_basemodel(user)
    assert user.model_dump() == {"name": "alice", "score": 100}

    assert isinstance(user, LogSerializable)
    log_dto = user.__log__()
    assert isinstance(log_dto, LogDTO)
    assert log_dto.metrics["name"] == "alice"
    assert log_dto.metrics["score"] == 100

    assert isinstance(user, CliSerializable)
    cli_dto = user.__cli__()
    assert isinstance(cli_dto, PanelDTO)

    assert "alice" in str(user)
    assert "score=100" in repr(user)

    validated = UserModel.model_validate({"name": "bob", "score": 250})
    assert validated.name == "bob"
    assert validated.score == 250
    assert isinstance(validated, CliSerializable)


def test_pydantic_preset_plus():
    """@view.pydantic.plus overrides specific categories while keeping preset."""
    item = PresetModel(x=1, y="a")
    assert is_basemodel(item)

    assert isinstance(item, LogSerializable)
    dto = item.__log__()
    assert dto.metrics["x"] == 1
    assert dto.metrics["y"] == "a"

    assert isinstance(item, CliSerializable)
    panel_dto = item.__cli__()
    assert isinstance(panel_dto, PanelDTO)
    assert "x=1" in repr(item)
