import shutil
import os
import glob
from pathlib import Path

from dreamml.logging import get_logger

_logger = get_logger(__name__)


class TempDirectory:
    """Manages a temporary directory for experiments using the singleton pattern.

    This class ensures that only one temporary directory instance exists throughout
    the application's lifecycle.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Creates or returns the singleton instance of TempDirectory.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            TempDirectory: The singleton instance of TempDirectory.
        """
        if cls._instance is None:
            cls._instance = super(TempDirectory, cls).__new__(cls)
        return cls._instance

    def __init__(self, path="./dml_spark_temp_dir"):
        """Initializes the TempDirectory instance.

        Creates the temporary directory at the specified path after removing any
        existing directories that match the path pattern.

        Args:
            path (str): The filesystem path for the temporary directory.

        Raises:
            OSError: If the directory cannot be created.
            PermissionError: If the program lacks permissions to modify the directory.
        """
        for name in glob.glob(path):
            shutil.rmtree(name)
        self.dir = Path(path)
        self.dir.mkdir()
        self.name = str(self.dir)
        _logger.info(f"Temp directory {self.name} is created.")

    def remove(self):
        """Removes the temporary directory.

        Deletes the temporary directory and all of its contents.

        Raises:
            OSError: If the directory cannot be removed.
            FileNotFoundError: If the directory does not exist.
            PermissionError: If the program lacks permissions to remove the directory.
        """
        shutil.rmtree(self.name, ignore_errors=False)
        _logger.info(f"Temp directory {self.name} is removed.")

    def clear(self):
        """Clears the temporary directory.

        Deletes all contents of the temporary directory and recreates it.

        Raises:
            OSError: If the directory cannot be removed or recreated.
            PermissionError: If the program lacks permissions to modify the directory.
        """
        shutil.rmtree(self.name, ignore_errors=False)
        self.dir.mkdir()
        _logger.info(f"Temp directory {self.name} is cleared.")