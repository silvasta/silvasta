import json
from pathlib import Path
from typing import Self

from pydantic import Field

from sstcore import printer
from sstcore.data import SstFile

PATH: Path = Path.cwd() / "role.txt"

LOAD = True


def main():
    printer.title("Start")
    if LOAD:
        load_role()
    else:
        create_role()


class Role(SstFile):  # REMOVE: is already in Project right?
    local_path: Path | None = None
    path: Path
    content: str
    rating: float = Field(default=5, ge=0, le=10)

    @classmethod
    def load(cls, path: Path) -> Self:
        return cls.model_validate(json.loads(path.read_text(encoding="utf-8")))

    def save(self, json_path: Path | None = None):
        self.json_file(json_path).write_text(self.to_json(), encoding="utf-8")

    def to_json(self) -> str:
        return self.model_dump_json(exclude_defaults=False, indent=2)

    def json_file(self, path: Path | None = None) -> Path:
        if path and path.suffix == ".json":
            return path
        return self.path.with_suffix(".json")

    @classmethod
    def read(cls, path: Path) -> Self:
        return cls(path=path, content=path.read_text())

    def write(self, txt_path: Path | None = None):
        self.txt_file(txt_path).write_text(self.content)

    def txt_file(self, path: Path | None = None) -> Path:
        if path and path.suffix == ".txt":
            return path
        return self.path.with_suffix(".txt")


def create_role():
    role = Role(path=PATH, content="my best role")
    role.path.write_text(role.content)
    role.save()
    printer("saved")


def load_role():
    printer("loading")
    role: Role = Role.load(path=PATH.with_suffix(".json"))
    printer(role)


if __name__ == "__main__":
    main()
