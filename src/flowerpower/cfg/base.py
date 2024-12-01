from typing import Any

import yaml
from fsspec import AbstractFileSystem
from munch import Munch, unmunchify
from pydantic import BaseModel, ConfigDict


class BaseConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def to_dict(self) -> dict[str, Any]:
        return unmunchify(self.model_dump())

    def to_yaml(self, path: str, fs: AbstractFileSystem | None = None) -> None:
        try:
            with fs.open(path, "w") as f:
                yaml.dump(self.to_dict(), f, default_flow_style=False)
        except NotImplementedError:
            raise NotImplementedError(
                "The filesystem "
                f"{self.fs.fs.protocol[0] if isinstance(self.fs.fs.protocol, tuple) else self.fs.fs.protocol} "
                "does not support writing files."
            )

    @classmethod
    def from_dict(cls, d: dict[str, Any] | Munch) -> "BaseConfig":
        return cls(**d)

    @classmethod
    def from_yaml(cls, path: str, fs: AbstractFileSystem):
        # if fs is None:
        #    fs = get_filesystem(".", cached=True)
        with fs.open(path) as f:
            return cls.from_dict(yaml.full_load(f))

    def update(self, d: dict[str, Any] | Munch) -> None:
        for k, v in d.items():
            setattr(self, k, v)
