import logging
import warnings

from dreamml.logging.monitoring import (
    ErrorLogData,
    MonitoringPayload,
    MonitoringLogData,
    ExceptionInfo,
    WarningLogData,
)
from dreamml.utils.styling import ANSIColoringMixin
from dreamml.utils.warnings import DMLWarning


class FileFormatter(logging.Formatter):
    """Custom logging formatter that handles ANSI-colored messages.

    This formatter checks if the log message uses ANSI coloring and preserves
    the color settings during formatting.

    Methods:
        format(record): Formats the log record, handling ANSI colors if present.
    """

    def format(self, record):
        """Format the specified log record, handling ANSI-colored messages if present.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: The formatted log message.
        """
        if isinstance(record.msg, ANSIColoringMixin):
            use_colors = record.msg.use_colors

            s = super().format(record)

            record.msg.use_colors = use_colors

        else:
            s = super().format(record)

        return s


class MonitoringFormatter(logging.Formatter):
    """Logging formatter for monitoring purposes, converting log records into monitoring payloads.

    This formatter processes log records to create structured monitoring data,
    including handling exceptions and warnings. It generates JSON payloads suitable
    for monitoring systems.

    Methods:
        formatException(exc_info): Formats exception information from exc_info.
        format(record): Formats the log record into a JSON string for monitoring.
    """

    def formatException(self, exc_info):
        """Format exception information from exc_info.

        Args:
            exc_info (tuple): Exception information as returned by sys.exc_info().

        Returns:
            ExceptionInfo: A structured representation of the exception.
        """
        tb = exc_info[2]
        if tb is not None:
            filename, lineno = tb.tb_frame.f_code.co_filename, tb.tb_lineno
        else:
            filename, lineno = None, None

        exc_log_data = ExceptionInfo(
            type=exc_info[0],
            text=str(exc_info[1]),
            line=lineno,
            file=filename,
        )

        return exc_log_data

    def format(self, record):
        """Format the specified log record into a JSON string for monitoring.

        This method converts the log record into a structured JSON payload suitable
        for monitoring systems. It handles different log levels, attaches exception
        information if present, and issues warnings if required log data is missing
        or invalid.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: A JSON string representing the monitoring payload.

        Raises:
            DMLWarning: If log_data is missing or not an instance of MonitoringLogData.
        """
        if record.exc_info:
            # Cache the exception log data to avoid converting it multiple times
            if not hasattr(record, "exc_log_data") or not record.exc_log_data:
                record.exc_log_data = self.formatException(record.exc_info)

        if not hasattr(record, "log_data"):
            if record.levelno >= logging.ERROR:
                exc_log_data = getattr(record, "exc_log_data")
                record.log_data = ErrorLogData(
                    exception=exc_log_data, msg=record.getMessage()
                )
            elif record.levelno >= logging.WARNING:
                record.log_data = WarningLogData(msg=record.getMessage())

        if not hasattr(record, "log_data"):
            warnings.warn(
                "Couldn't gather log_data for monitoring. Instance of LogRecord has no `log_data` attribute. "
                "You probably need to pass `extra` argument to your monitoring logger: "
                '`logger.monitor(msg, extra={"log_data": LogData})` where LogData is subclass of MonitoringLogData.',
                DMLWarning,
                stacklevel=9,  # stacklevel to show where log function is called
            )
            return

        if not isinstance(record.log_data, MonitoringLogData):
            warnings.warn(
                f"Couldn't gather log_data for monitoring. Expected `log_data` to be "
                f"an instance of `{MonitoringLogData.__name__}`, but got {type(record.log_data)}",
                DMLWarning,
                stacklevel=9,  # stacklevel to show where log function is called
            )
            return

        payload = MonitoringPayload(message=record.log_data.model_dump_json())

        msg = payload.model_dump_json()

        return msg


class FormatterWithoutException(logging.Formatter):
    """Logging formatter that formats log records without including exception information.

    This formatter generates a simple log message containing the formatted message
    and the timestamp, excluding any exception details.

    Methods:
        format(record): Formats the log record into a text message without exception details.
    """

    def format(self, record):
        """Format the specified log record into a text message without exception details.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: The formatted log message.
        """
        record.message = record.getMessage()
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        s = self.formatMessage(record)

        return s