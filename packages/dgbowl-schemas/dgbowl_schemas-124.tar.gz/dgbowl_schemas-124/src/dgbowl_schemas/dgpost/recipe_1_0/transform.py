from pydantic.v1 import BaseModel, Field, Extra
from typing import Sequence, Any, Dict


class Transform(BaseModel, extra=Extra.forbid, allow_population_by_field_name=True):
    table: str
    with_: str = Field(alias="with")
    using: Sequence[Dict[str, Any]]
