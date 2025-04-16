import msgspec
import yaml
from fsspec import AbstractFileSystem
from hamilton.function_modifiers import source, value
from munch import Munch, munchify

from ..base import BaseConfig
from .run import PipelineRunConfig
from .schedule import PipelineScheduleConfig
from .tracker import PipelineTrackerConfig


class PipelineConfig(BaseConfig):
    name: str | None = None
    run: PipelineRunConfig = msgspec.field(default_factory=PipelineRunConfig)
    schedule: PipelineScheduleConfig = msgspec.field(
        default_factory=PipelineScheduleConfig
    )
    params: dict = msgspec.field(default_factory=dict)
    tracker: PipelineTrackerConfig = msgspec.field(
        default_factory=PipelineTrackerConfig
    )
    h_params: dict = msgspec.field(default_factory=dict)

    def __post_init__(self):
        if isinstance(self.params, dict):
            self.h_params = munchify(self.to_h_params(self.params))
            self.params = munchify(self.params)

    def to_yaml(self, path: str, fs: AbstractFileSystem):
        try:
            fs.makedirs(fs._parent(path), exist_ok=True)
            with fs.open(path, "w") as f:
                d = self.to_dict()
                d.pop("name")
                d.pop("h_params")
                yaml.dump(d, f, default_flow_style=False)
        except NotImplementedError:
            raise NotImplementedError(
                "The filesystem "
                f"{self.fs.fs.protocol[0] if isinstance(self.fs.fs.protocol, tuple) else self.fs.fs.protocol} "
                "does not support writing files."
            )

    @classmethod
    def from_dict(cls, name: str, data: dict | Munch):
        data.update({"name": name})
        return msgspec.convert(data, cls)

    @classmethod
    def from_yaml(cls, name: str, path: str, fs: AbstractFileSystem):
        with fs.open(path) as f:
            data = yaml.full_load(f)
            return cls.from_dict(name=name, data=data)

    def update(self, d: dict | Munch):
        for k, v in d.items():
            eval(f"self.{k}.update({v})")
            if k == "params":
                self.params.update(munchify(v))
                self.h_params = munchify(self.to_h_params(self.params))
                # self.params = munchify(self.params)
        if "params" in d:
            self.h_params = munchify(self.to_h_params(self.params))
            self.params = munchify(self.params)

    @staticmethod
    def to_h_params(d: dict) -> dict:
        """Converts a dictionary of function arguments to Hamilton function parameters"""

        def transform_recursive(val, original_dict, depth=1):
            if isinstance(val, dict):
                # If we're at depth 3, wrap the entire dictionary in value()
                if depth == 3:
                    return value(val)
                # Otherwise, continue recursing
                return {
                    k: transform_recursive(v, original_dict, depth + 1)
                    for k, v in val.items()
                }
            # If it's a string and matches a key in the original dictionary
            elif isinstance(val, str) and val in original_dict:
                return source(val)
            # For non-dictionary values at depth 3
            elif depth == 3:
                return value(val)
            # For all other values
            return val

        # Step 1: Replace each value with a dictionary containing key and value
        result = {k: {k: d[k]} for k in d}

        # Step 2: Transform all values recursively
        return {k: transform_recursive(v, d) for k, v in result.items()}
