from pydantic import BaseModel, Field


class PipelineAdd(BaseModel):
    overwrite: bool = Field(default=False)
