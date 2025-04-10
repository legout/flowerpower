import msgspec
from typing import Any
from fsspec import AbstractFileSystem, filesystem


class BaseConfig(msgspec.Struct, kw_only=True):
    def to_dict(self) -> dict[str, Any]:
        return msgspec.to_builtins(self)
    
    def to_yaml(self, path: str, fs: AbstractFileSystem | None = None) -> None:
        if fs is None:
            fs = filesystem("file")
        try:
            with fs.open(path, "wb") as f:
                f.write(msgspec.yaml.encode(self, order="deterministic"))
                #yaml.dump(self.to_dict(), f, default_flow_style=False)
        except NotImplementedError:
            raise NotImplementedError(
                "The filesystem does not support writing files."
            )

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "BaseConfig":
        return msgspec.convert(d, cls)

    @classmethod
    def from_yaml(cls, path: str, fs: AbstractFileSystem|None=None) -> "BaseConfig":
        if fs is None:
            fs = filesystem("file")
        with fs.open(path) as f:
            #data = yaml.full_load(f)
            #return cls.from_dict(data)
            return msgspec.yaml.decode(f.read(), type=cls, strict=False)

    def update(self, d: dict[str, Any]) -> None:
        for k, v in d.items():
            setattr(self, k, v)
