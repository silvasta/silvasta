from pydantic import BaseModel

from sstcore.utils.view import Log, Str, ViewBuilder, view


@view(ViewBuilder(log=Log.DEFAULT, str=Str.DEFAULT))
class P(BaseModel):
    x: int
    y: str


def test_pydantic_profile():
    p = P(x=1, y="a")
    dto = p.__log__()  #  ty:ignore
    assert dto.metrics["x"] == 1
    assert dto.metrics["y"] == "a"
    assert p.model_dump()["x"] == 1  # Pydantic не должен сломаться
