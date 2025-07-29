import json
import os
import uuid
import warnings
from datetime import datetime
from enum import Enum
import socket
from typing import Optional, Type, Dict, Any

from pydantic import BaseModel, field_validator, field_serializer

import dreamml
from dreamml.utils.warnings import DMLWarning

MAX_MESSAGE_LEN = 2**21


class MonitoringPayload(BaseModel):
    """
    Represents a monitoring payload for reporting events.

    Attributes:
        app_id (str): Identifier of the application.
        type_id (str): Identifier of the event type.
        subtype_id (str): Identifier of the event subtype.
        message (str): The message associated with the event.
    """

    app_id: str = "dml-ser-4b14-9a58-8219b60d91d2"
    type_id: str = "Tech"
    subtype_id: str = "INFO"
    message: str


class MonitoringEvent(Enum):
    """
    Enumeration of possible monitoring event types in dreamml_base.

    Attributes:
        Error (int): Represents an error event.
        Warning (int): Represents a warning event.
        PipelineStarted (int): Indicates the start of a pipeline.
        PipelineFinished (int): Indicates the completion of a pipeline.
        StageFinished (int): Indicates the completion of a pipeline stage.
        TrainingFinished (int): Indicates the completion of training.
        DataLoaded (int): Indicates that data has been loaded.
        DataTransformed (int): Indicates that data has been transformed.
        FeaturesGenerated (int): Indicates that features have been generated.
        ReportStarted (int): Indicates the start of report generation.
        ReportFinished (int): Indicates the completion of report generation.
        ValidationTestFinished (int): Indicates the completion of a validation test.
    """

    Error = 0
    Warning = 1
    PipelineStarted = 2
    PipelineFinished = 3
    StageFinished = 4
    TrainingFinished = 5
    DataLoaded = 6
    DataTransformed = 7
    FeaturesGenerated = 8
    ReportStarted = 9
    ReportFinished = 10
    ValidationTestFinished = 11


class MonitoringLogData(BaseModel):
    """
    Base model for monitoring log data.

    Attributes:
        event_id (MonitoringEvent): The type of the monitoring event.
        datetime (str): The timestamp of the event in YYYY-MM-DD HH:MM:SS format.
        hostname (str): The hostname where the event originated.
        user (str): The user who initiated the event.
        dml_version (str): The version of dreamml_base.
        session_id (str): The unique session identifier.
    """

    event_id: MonitoringEvent
    datetime: str
    hostname: str = socket.gethostname()
    user: str = os.environ.get("USER", "Unknown")
    dml_version: str = dreamml.__version__
    session_id: str = uuid.uuid4().hex

    class Config:
        extra = "forbid"

    def __init__(self, /, **data):
        """
        Initializes a MonitoringLogData instance.

        Args:
            **data: Arbitrary keyword arguments corresponding to the model fields.

        Raises:
            DMLWarning: If an event_id is provided during initialization.
        """
        event_id = data.pop("event_id", None)
        if event_id is not None:
            warnings.warn(
                f"Tried to set {event_id=} which should be explicitly defined in {self.__class__.__name__}.",
                DMLWarning,
                stacklevel=2,
            )

        data["datetime"] = data.get("datetime", datetime.now())

        super().__init__(**data)

    @field_validator("datetime", mode="before")
    @classmethod
    def validate_datetime(cls, dt: datetime):
        """
        Validates and formats the datetime field.

        Args:
            dt (datetime): The datetime object to validate.

        Returns:
            str: The formatted datetime string.

        Raises:
            ValueError: If dt is not an instance of datetime.datetime.
        """
        if isinstance(dt, datetime):
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        else:
            raise ValueError(
                f"Datetime passed to {cls.__name__} must be an instance of datetime.datetime"
            )


class ExceptionInfo(BaseModel):
    """
    Represents information about an exception.

    Attributes:
        type (str): The type name of the exception.
        text (str): The exception message.
        line (Optional[int]): The line number where the exception occurred.
        file (Optional[str]): The file name where the exception occurred.
    """

    type: str
    text: str
    line: Optional[int] = None
    file: Optional[str] = None

    @field_validator("type", mode="before")
    @classmethod
    def validate_exception_type(cls, v: Type[Exception]):
        """
        Validates the type of the exception.

        Args:
            v (Type[Exception]): The exception class to validate.

        Returns:
            str: The name of the exception class.

        Raises:
            ValueError: If v is not a subclass of Exception.
        """
        if isinstance(v, type) and issubclass(v, Exception):
            return v.__name__
        else:
            raise ValueError(
                f"Exception passed to {cls.__name__} must be subclass of Exception."
            )


class ErrorLogData(MonitoringLogData):
    """
    Represents log data for error events.

    Attributes:
        event_id (MonitoringEvent): The event type, set to MonitoringEvent.Error.
        exception (Optional[ExceptionInfo]): Information about the exception.
        msg (str): The error message.
    """

    event_id: MonitoringEvent = MonitoringEvent.Error
    exception: Optional[ExceptionInfo] = None
    msg: str


class WarningLogData(MonitoringLogData):
    """
    Represents log data for warning events.

    Attributes:
        event_id (MonitoringEvent): The event type, set to MonitoringEvent.Warning.
        msg (str): The warning message.
    """

    event_id: MonitoringEvent = MonitoringEvent.Warning
    msg: str


class UserConfigLogData(BaseModel):
    """
    Represents user configuration log data.

    Attributes:
        user_config (Dict[str, Any]): The user configuration settings.
    """

    user_config: Dict[str, Any]

    @field_serializer("user_config")
    def serialize_user_config(self, user_config: Dict[str, Any], _info):
        """
        Serializes the user_config field to ensure all values are JSON serializable.

        Args:
            user_config (Dict[str, Any]): The user configuration dictionary.
            _info: Additional information (unused).

        Returns:
            Dict[str, Any]: The serialized user configuration dictionary.
        """
        def safe_serialize(val):
            try:
                json.dumps(val)
                return val
            except (TypeError, OverflowError):
                # If not serializable, convert to str
                return str(val)

        return {key: safe_serialize(value) for key, value in user_config.items()}

    @field_validator("user_config", mode="before")
    @classmethod
    def validate_user_config(cls, d: Dict[str, Any]):
        """
        Validates that user_config is a dictionary with string keys.

        Args:
            d (Dict[str, Any]): The user configuration dictionary.

        Returns:
            Dict[str, Any]: The validated user configuration dictionary.

        Raises:
            ValueError: If d is not a dict or contains non-string keys.
        """
        if not isinstance(d, dict) or any(not isinstance(key, str) for key in d):
            raise ValueError(f"User configuration must be a dict with string keys.")

        return d


class PipelineStartedLogData(MonitoringLogData, UserConfigLogData):
    """
    Represents log data for the start of a pipeline.

    Attributes:
        event_id (MonitoringEvent): The event type, set to MonitoringEvent.PipelineStarted.
        experiment_name (str): The name of the experiment.
        from_checkpoint (bool): Indicates if the pipeline started from a checkpoint.
        user_config (Dict[str, Any]): The user configuration settings.
    """

    event_id: MonitoringEvent = MonitoringEvent.PipelineStarted
    experiment_name: str
    from_checkpoint: bool = False


class PipelineFinishedLogData(MonitoringLogData):
    """
    Represents log data for the completion of a pipeline.

    Attributes:
        event_id (MonitoringEvent): The event type, set to MonitoringEvent.PipelineFinished.
        experiment_name (str): The name of the experiment.
        elapsed_time (float): The time elapsed during the pipeline execution.
    """

    event_id: MonitoringEvent = MonitoringEvent.PipelineFinished
    experiment_name: str
    elapsed_time: float


class StageFinishedLogData(MonitoringLogData):
    """
    Represents log data for the completion of a pipeline stage.

    Attributes:
        event_id (MonitoringEvent): The event type, set to MonitoringEvent.StageFinished.
        experiment_name (str): The name of the experiment.
        stage_name (str): The name of the stage.
        stage_id (str): The identifier of the stage.
        elapsed_time (float): The time elapsed during the stage execution.
    """

    event_id: MonitoringEvent = MonitoringEvent.StageFinished
    experiment_name: str
    stage_name: str
    stage_id: str
    elapsed_time: float


class TrainingFinishedLogData(MonitoringLogData):
    """
    Represents log data for the completion of training.

    Attributes:
        event_id (MonitoringEvent): The event type, set to MonitoringEvent.TrainingFinished.
        model (str): The name or identifier of the trained model.
        metrics (Dict[str, Dict[str, float]]): The performance metrics of the model.
        elapsed_time (float): The time elapsed during training.
    """

    event_id: MonitoringEvent = MonitoringEvent.TrainingFinished
    model: str
    metrics: Dict[str, Dict[str, float]]
    elapsed_time: float


class DataLoadedLogData(MonitoringLogData):
    """
    Represents log data for data loading events.

    Attributes:
        event_id (MonitoringEvent): The event type, set to MonitoringEvent.DataLoaded.
        name (str): The name of the dataset.
        length (int): The number of records loaded.
        features_num (int): The number of features in the dataset.
        nan_count (int): The number of missing values in the dataset.
        elapsed_time (float): The time elapsed during data loading.
    """

    event_id: MonitoringEvent = MonitoringEvent.DataLoaded
    name: str
    length: int
    features_num: int
    nan_count: int
    elapsed_time: float


class DataTransformedLogData(MonitoringLogData):
    """
    Represents log data for data transformation events.

    Attributes:
        event_id (MonitoringEvent): The event type, set to MonitoringEvent.DataTransformed.
        name (str): The name of the transformed dataset.
        length (int): The number of records after transformation.
        features_num (int): The number of features after transformation.
        nan_count (int): The number of missing values after transformation.
        elapsed_time (float): The time elapsed during data transformation.
    """

    event_id: MonitoringEvent = MonitoringEvent.DataTransformed
    name: str
    length: int
    features_num: int
    nan_count: int
    elapsed_time: float


class FeaturesGeneratedLogData(MonitoringLogData):
    """
    Represents log data for feature generation events.

    Attributes:
        event_id (MonitoringEvent): The event type, set to MonitoringEvent.FeaturesGenerated.
        length (int): The number of records for which features were generated.
        features_num (int): The number of features generated.
        nan_count (int): The number of missing values in the generated features.
        elapsed_time (float): The time elapsed during feature generation.
    """

    event_id: MonitoringEvent = MonitoringEvent.FeaturesGenerated
    length: int
    features_num: int
    nan_count: int
    elapsed_time: float


class ReportStartedLogData(MonitoringLogData, UserConfigLogData):
    """
    Represents log data for the start of report generation.

    Attributes:
        event_id (MonitoringEvent): The event type, set to MonitoringEvent.ReportStarted.
        task (str): The task for which the report is being generated.
        development (bool): Indicates if the report is for development purposes.
        custom_model (bool): Indicates if a custom model is used in the report.
        experiment_name (Optional[str]): The name of the experiment related to the report.
        report_id (str): The unique identifier of the report.
        user_config (Dict[str, Any]): The user configuration settings.
    """

    event_id: MonitoringEvent = MonitoringEvent.ReportStarted
    task: str
    development: bool
    custom_model: bool
    experiment_name: Optional[str] = None
    report_id: str


class ReportFinishedLogData(MonitoringLogData):
    """
    Represents log data for the completion of report generation.

    Attributes:
        event_id (MonitoringEvent): The event type, set to MonitoringEvent.ReportFinished.
        report_id (str): The unique identifier of the report.
        elapsed_time (float): The time elapsed during report generation.
    """

    event_id: MonitoringEvent = MonitoringEvent.ReportFinished
    report_id: str
    elapsed_time: float


class ValidationTestFinishedLogData(MonitoringLogData):
    """
    Represents log data for the completion of a validation test.

    Attributes:
        event_id (MonitoringEvent): The event type, set to MonitoringEvent.ValidationTestFinished.
        report_id (str): The unique identifier of the report associated with the test.
        test_name (str): The name of the validation test.
        elapsed_time (float): The time elapsed during the validation test.
    """

    event_id: MonitoringEvent = MonitoringEvent.ValidationTestFinished
    report_id: str
    test_name: str
    elapsed_time: float