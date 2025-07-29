class MissedColumnError(IndexError):
    """Exception raised for missing expected columns in a pandas DataFrame."""

    pass


class MissedTargetError(Exception):
    """Exception raised when the target column is missing."""

    pass


class ConfigurationError(Exception):
    """Exception raised for errors in the configuration."""

    pass