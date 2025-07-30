from pydantic import BaseModel, Field, model_validator, field_validator
from typing import Sequence, Literal
from .settings import Settings
from .sample import Sample
from .task import Task

from pathlib import Path
import yaml
import json


class Payload(BaseModel, extra="forbid"):
    version: Literal["2.1"]
    settings: Settings = Field(default_factory=Settings)
    """Additional configuration options for tomato."""

    sample: Sample
    """Specification of the experimental sample."""

    method: Sequence[Task]
    """A sequence of the experimental :class:`Tasks`."""

    @model_validator(mode="before")
    @classmethod
    def extract_samplefile(cls, values):
        """
        If ``samplefile`` is provided in ``values``, parse the file as ``sample``.
        """
        if "samplefile" in values:
            sf = Path(values.pop("samplefile"))
            assert sf.exists()
            with sf.open() as f:
                if sf.suffix in {".yml", ".yaml"}:
                    sample = yaml.safe_load(f)
                elif sf.suffix in {".json"}:
                    sample = json.load(f)
                else:
                    raise ValueError(f"Incorrect suffix of samplefile: '{sf}'")
            assert "sample" in sample
            values["sample"] = sample["sample"]
        return values

    @model_validator(mode="before")
    @classmethod
    def extract_methodfile(cls, values):
        """
        If ``methodfile`` is provided in ``values``, parse the file as ``method``.
        """
        if "methodfile" in values:
            mf = Path(values.pop("methodfile"))
            assert mf.exists()
            with mf.open() as f:
                if mf.suffix in {".yml", ".yaml"}:
                    method = yaml.safe_load(f)
                elif mf.suffix in {".json"}:
                    method = json.load(f)
                else:
                    raise ValueError(f"Incorrect suffix of methodfile: '{mf}'")
            assert "method" in method
            values["method"] = method["method"]
        return values

    @field_validator("method", mode="after")
    @classmethod
    def validate_task_names(cls, method):
        req_names = set()
        prov_names = set()
        for task in method:
            if task.task_name is not None:
                prov_names.add(task.task_name)
            if task.start_with_task_name is not None:
                req_names.add(task.start_with_task_name)
            if task.stop_with_task_name is not None:
                req_names.add(task.stop_with_task_name)
        if prov_names.intersection(req_names) == req_names:
            return method
        else:
            raise ValueError(
                "Not all required task_names were provided: "
                f"required = {req_names}, provided = {prov_names}"
            )
