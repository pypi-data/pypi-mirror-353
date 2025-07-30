from pydantic import BaseModel, Field, model_validator, field_validator
from typing import Optional, Any, Dict, Union
import pint


class Task(BaseModel, extra="forbid"):
    """
    The :class:`Task` is a driver/device-independent abstraction describing the
    measurement steps. The driver-specific information for the :class:`Task` can be
    provided via the :obj:`technique_name` and :obj:`task_params` parameters.
    """

    component_role: str
    """role of the pipeline *component* on which this :class:`Task` should run"""

    max_duration: Union[float, str]
    """the maximum duration of this :class:`Task`, in seconds"""

    sampling_interval: Union[float, str]
    """the interval between measurements, in seconds"""

    polling_interval: Optional[Union[float, str]] = None
    """
    the interval between polling for data by the ``tomato-job`` process, in seconds;
    defaults to the value in driver settings
    """

    technique_name: str
    """
    the name of the technique; has to match one of the capabilities of the *component*
    on which this :class:`Task` will be executed
    """

    task_name: Optional[str] = None
    """
    the (optional) name of the current :class:`Task`; can be used for triggering other
    :class:`Task` in parallel to this one via :obj:`start_with_task_name`
    """

    task_params: Optional[Dict[str, Any]] = Field(default_factory=dict)
    """
    a :class:`dict` of any additional parameters required to specify the experimental
    technique; the key-value pairs of this :class:`dict` will be used as attr-val
    pairs by the :func:`set_attr` method of the *component* executing this :class:`Task`
    """

    start_with_task_name: Optional[str] = None
    """
    the :obj:`task_name` of the :class:`Task` that this :class:`Task` should be
    started in parallel with; when set, this :class:`Task` will wait for execution until
    a :class:`Task` with the matching :obj:`task_name` is started
    """

    stop_with_task_name: Optional[str] = None
    """
    the :obj:`task_name` of the :class:`Task` that, when started, will stop the execution
    of this :class:`Task`; when set, this :class:`Task` will execute normally, but if a
    a :class:`Task` with the matching :obj:`task_name` is started, this :class:`Task`
    will be stopped
    """

    @model_validator(mode="after")
    @classmethod
    def task_names_cannot_be_same(cls, task):
        if task.task_name is not None and task.task_name == task.start_with_task_name:
            raise ValueError(
                "A task cannot trigger the start of itself: "
                f"provided task_name={task.task_name!r}, "
                f"provided start_with_task_name={task.start_with_task_name!r}."
            )
        if task.task_name is not None and task.task_name == task.stop_with_task_name:
            raise ValueError(
                "A task cannot trigger the stop of itself: "
                f"provided task_name={task.task_name!r}, "
                f"provided start_with_task_name={task.stop_with_task_name!r}."
            )
        return task

    @field_validator(
        "max_duration", "sampling_interval", "polling_interval", mode="after"
    )
    @classmethod
    def convert_str_to_seconds(cls, v: Union[str, float]) -> float:
        if v is None:
            return v
        elif isinstance(v, str):
            return pint.Quantity(v).to("seconds").m
        else:
            return v
