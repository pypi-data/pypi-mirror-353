import os
import sys
import shutil
from datetime import datetime
from typing import Optional, List
import logging

from dreamml.logging.formatters import FileFormatter, FormatterWithoutException
from dreamml.logging.handlers import MonitoringHandler
from dreamml.logging import get_root_logger, MONITOR


class DMLLogger(logging.getLoggerClass()):
    """A custom logger class extending the default logging.Logger.

    This logger adds additional functionalities such as custom log levels,
    temporary file handlers, and experiment-specific log file management.

    Attributes:
        _used_warnings (List[str]): A list to track warnings that have been used.
        temp_file_handler (Optional[logging.FileHandler]): Temporary file handler for logging.
        temp_log_path (str): Path to the temporary log file.
        _file_formatter (FileFormatter): Formatter for the log file.
    """

    def __init__(self, name):
        """Initializes the DMLLogger with a given name.

        Creates necessary directories and initializes the temporary log file.

        Args:
            name (str): The name of the logger.
        """
        super().__init__(name)
        self._used_warnings = []

        logging.addLevelName(MONITOR, "MONITOR")

        self.temp_file_handler = None
        os.makedirs(os.path.join(os.getcwd(), ".dml_log"), exist_ok=True)
        current_datetime = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        self.temp_log_path = os.path.join(
            os.getcwd(), ".dml_log", f"run{current_datetime}.log"
        )
        self._file_formatter = FileFormatter(
            fmt="[{asctime}] - {levelname} - {name} - {message}",
            datefmt="%Y-%m-%d %H:%M:%S",
            style="{",
        )

    def start_logging_session(self):
        """Starts a new logging session by adding a temporary file handler.

        If a temporary file handler already exists, it removes and closes it before
        adding a new one.
        """
        if self.temp_file_handler:
            self.removeHandler(self.temp_file_handler)
            self.temp_file_handler.close()

        self.temp_file_handler = logging.FileHandler(self.temp_log_path)
        self.temp_file_handler.setFormatter(self._file_formatter)

        self.addHandler(self.temp_file_handler)

    def set_experiment_log_file(self, log_file_path):
        """Sets the log file for the current experiment.

        Moves the temporary log file to the specified experiment log file path.
        If moving fails due to permissions, it copies the file instead.

        Args:
            log_file_path (str): The destination path for the experiment log file.

        Raises:
            PermissionError: If the file cannot be moved due to permission issues.
            Exception: For any other exceptions that occur during file operations.
        """
        if self.temp_file_handler is not None:
            self.removeHandler(self.temp_file_handler)
            self.temp_file_handler.close()

            if os.path.exists(self.temp_log_path):
                try:
                    shutil.move(self.temp_log_path, log_file_path)
                except PermissionError:
                    shutil.copy(self.temp_log_path, log_file_path)
                except Exception as e:
                    self.warning(
                        f"Couldn't move {self.temp_file_handler} to experiment directory. {e}"
                    )
                    return

        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(self._file_formatter)

        self.debug(f"Saving experiment logs to {log_file_path}")

        self.addHandler(file_handler)

    def monitor(self, msg, *args, **kwargs):
        """Logs a message with severity level 'MONITOR'.

        This method allows logging messages that are specific to monitoring purposes.

        Args:
            msg (str): The message format string.
            *args: Variable length argument list for message formatting.
            **kwargs: Arbitrary keyword arguments for message formatting.

        Example:
            logger.monitor("Houston, we have a %s", "major disaster")
        """
        if self.isEnabledFor(MONITOR):
            self._log(MONITOR, msg, args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """Logs a warning message only once.

        This method ensures that duplicate warning messages are not logged multiple times.

        Args:
            msg (str): The warning message format string.
            *args: Variable length argument list for message formatting.
            **kwargs: Arbitrary keyword arguments for message formatting.
        """
        if msg in self._used_warnings:
            return

        super().warning(msg, *args, **kwargs)
        self._used_warnings.append(msg)


class CombinedLogger:
    """A composite logger that aggregates multiple logger instances.

    Allows logging messages to multiple loggers simultaneously, ensuring that
    each logger handles the message appropriately based on its configuration.

    Attributes:
        loggers (List[logging.Logger]): A list of logger instances to aggregate.
    """

    def __init__(self, loggers: List[logging.Logger]):
        """Initializes the CombinedLogger with a list of logger instances.

        Filters out any None values from the provided list of loggers.

        Args:
            loggers (List[logging.Logger]): The list of logger instances to combine.
        """
        self.loggers = [logger for logger in loggers if logger is not None]

    def log(self, level, msg, *args, **kwargs):
        """Logs a message at the specified level to all aggregated loggers.

        Args:
            level (str): The logging level (e.g., 'info', 'debug').
            msg (str): The message format string.
            *args: Variable length argument list for message formatting.
            **kwargs: Arbitrary keyword arguments for message formatting.

        Raises:
            AttributeError: If any logger does not support the specified logging level.
        """
        for logger in self.loggers:
            if hasattr(logger, level):
                log_method = getattr(logger, level)
                log_method(msg, *args, **kwargs)
            else:
                raise AttributeError(f"Logger '{logger.name}' has no method '{level}'.")

    def __getattr__(self, name: str):
        """Handles dynamic method calls for logging levels.

        Allows calling logging methods like info, debug, error, etc., dynamically.

        Args:
            name (str): The name of the logging level method to call.

        Returns:
            Callable: A wrapper function that logs the message at the specified level.

        Raises:
            AttributeError: If the logging level does not exist.
        """
        if name.upper() in logging._nameToLevel:

            def wrapper(msg, *args, **kwargs):
                self.log(name, msg, *args, **kwargs)

            return wrapper
        else:
            raise AttributeError(f"No such log level: '{name}'.")


def init_logging(name: str, log_file: Optional[str] = None):
    """Initializes the root logger with specified handlers and formatters.

    Sets up the logging configuration, including stream handlers for stdout and stderr,
    file handlers for experiment logs, and a monitoring handler.

    Args:
        name (str): The name of the logger to initialize.
        log_file (Optional[str]): The path to the experiment log file. If provided,
            the logger will save experiment logs to this file.

    Returns:
        logging.Logger: The initialized logger instance.

    Raises:
        RuntimeError: If attempting to initialize a logger that already has handlers.
    """
    logging.setLoggerClass(DMLLogger)

    logger = logging.getLogger(name)
    logger.propagate = False

    logger.setLevel(logging.INFO)

    if logger.handlers:
        raise RuntimeError(
            f"Tried to initialize logger '{name}' the second time. "
            f"This logger already has {len(logger.handlers)} handlers."
        )

    formatter = FormatterWithoutException(
        fmt="[{asctime}] {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        style="{",
    )

    # Instancing loggers for stdout and stderr with filters for message types
    stdout_streamhandler = logging.StreamHandler(stream=sys.stdout)
    stdout_streamhandler.addFilter(lambda record: record.levelno < logging.WARNING)
    stdout_streamhandler.setFormatter(formatter)

    stderr_streamhandler = logging.StreamHandler(stream=sys.stderr)
    stderr_streamhandler.addFilter(lambda record: record.levelno >= logging.WARNING)
    stderr_streamhandler.setFormatter(formatter)

    logger.addHandler(stdout_streamhandler)
    logger.addHandler(stderr_streamhandler)

    if log_file is not None:
        logger.set_experiment_log_file(log_file)

    monitoring_handlder = MonitoringHandler()
    monitoring_handlder.setLevel(MONITOR)

    logger.addHandler(monitoring_handlder)

    return logger


def capture_warnings(capture):
    """Configures the logging of Python warnings.

    Redirects warnings to the specified logger, ensuring that they are handled
    appropriately based on the current logging configuration.

    Args:
        capture (bool): If True, capture warnings and log them. If False, do not capture warnings.
    """
    logger = logging.getLogger("py.warnings")

    root_logger = get_root_logger()

    if not logger.handlers:
        for handler in root_logger.handlers:
            logger.addHandler(handler)

    logger.setLevel(root_logger.level)
    logger.propagate = False

    logging.captureWarnings(capture)