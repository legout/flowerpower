# from ..cli.utils import parse_dict_or_list_param
from pydantic import BaseModel, ValidationError as PydandticValidationError
from sanic_ext.exceptions import ValidationError

from typing import Any


async def deserialize_and_validate(
    type_: BaseModel,
    body: dict | None = None,
    query: list[tuple[str, Any]] | None = None,
):
    try:
        if query:
            return type_(**dict(query) or {})
        return type_(**body or {})
    except (TypeError, PydandticValidationError) as e:
        raise ValidationError(e)
