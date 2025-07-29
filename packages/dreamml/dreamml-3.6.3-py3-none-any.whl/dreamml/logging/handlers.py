import logging
import socket
from typing import Optional, Dict

import requests
from requests import RequestException

from dreamml.logging.formatters import MonitoringFormatter
from dreamml.logging import get_logger

_logger = get_logger(__name__)
_defaultMonitoringFormatter = MonitoringFormatter()


class MonitoringHandler(logging.Handler):
    """
    A logging handler that sends log records to a monitoring service via HTTP.

    This handler formats log records and sends them to a specified endpoint.
    If the monitoring service becomes unavailable or times out, the handler
    will disable itself to prevent further attempts.

    Attributes:
        hostname (str): The hostname of the machine running the handler.
        endpoint (Optional[str]): The URL of the monitoring service endpoint.
        headers (Dict[str, str]): HTTP headers to include in the monitoring requests.
        disabled (bool): Flag indicating whether the handler is disabled.
    """

    def __init__(
        self, endpoint: Optional[str] = None, headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize the MonitoringHandler.

        Args:
            endpoint (Optional[str]): The URL of the monitoring service endpoint.
                If not provided, the handler may raise an error or be configured later.
            headers (Optional[Dict[str, str]]): HTTP headers to include in the monitoring
                requests. Defaults to {"Content-Type": "application/json"} if not provided.
        """
        super().__init__()

        self.addFilter(lambda record: getattr(record, "monitoring", True))

        self.disabled = False

        self.hostname = socket.gethostname()
        self._set_endpoint(endpoint)
        self.headers = headers or {"Content-Type": "application/json"}

    def _set_endpoint(self, endpoint: Optional[str] = None):
        """
        Set the endpoint for the monitoring service.

        Args:
            endpoint (Optional[str]): The URL of the monitoring service endpoint.

        Raises:
            ValueError: If the endpoint is not provided.
        """
        if endpoint is not None:
            pass
        else:
            #raise ValueError(f"MonitoringHandler couldn't be initialized without setting endpoint.")
            pass
        
        self.endpoint = endpoint

    def format(self, record):
        """
        Format the specified log record.

        This method determines which formatter to use for the log record.
        If a custom formatter is set, it uses that formatter. Otherwise, it
        uses the default MonitoringFormatter.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: The formatted log record as a string.
        """
        if self.formatter:
            fmt = self.formatter
        else:
            fmt = _defaultMonitoringFormatter

        return fmt.format(record)

    def emit(self, record):
        """
        Emit a log record.

        This method formats the log record and sends it to the monitoring
        service via an HTTP POST request. If the request fails due to a timeout
        or other request exceptions, the handler will log a warning and disable
        itself to prevent further attempts.

        Args:
            record (logging.LogRecord): The log record to emit.

        Raises:
            None
        """
        if self.disabled:
            return

        msg = self.format(record)

        try:
            response = requests.post(
                self.endpoint,
                headers=self.headers,
                data=msg.encode("utf-8"),
                timeout=10,
            )
            response.raise_for_status()
        except requests.Timeout as e:
            _logger.warning(
                "Couldn't establish connection to monitoring service due to timeout. "
                f"Please, contact the cluster administrator. {e}",
                extra={"monitoring": False},
            )
            self.disabled = True
        except RequestException as e:
            _logger.warning(
                "Monitoring service is unavailable.", extra={"monitoring": False}
            )
            _logger.debug(e, extra={"monitoring": False})
            self.disabled = True