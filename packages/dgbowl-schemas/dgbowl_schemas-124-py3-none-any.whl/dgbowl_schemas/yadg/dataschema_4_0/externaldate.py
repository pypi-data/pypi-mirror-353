from pydantic.v1 import BaseModel, Extra, Field
from typing import Literal, Optional, Union
import logging

logger = logging.getLogger(__name__)


class ExternalDateFile(BaseModel, extra=Extra.forbid):
    class Content(BaseModel, extra=Extra.forbid):
        path: str
        type: str
        match: Optional[str]

    file: Content


class ExternalDateFilename(BaseModel, extra=Extra.forbid):
    class Content(BaseModel, extra=Extra.forbid):
        format: str
        len: int

    filename: Content


class ExternalDateISOString(BaseModel, extra=Extra.forbid):
    isostring: str


class ExternalDateUTSOffset(BaseModel, extra=Extra.forbid):
    utsoffset: float


class ExternalDate(BaseModel, extra=Extra.forbid, allow_population_by_field_name=True):
    using: Union[
        ExternalDateFile,
        ExternalDateFilename,
        ExternalDateISOString,
        ExternalDateUTSOffset,
    ] = Field(alias="from")
    mode: Literal["add", "replace"] = "add"
