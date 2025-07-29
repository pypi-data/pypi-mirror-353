import sys
from pathlib import Path
from typing import Optional, Union, List

import nbformat
from nbformat.reader import NotJSONError

import dreamml
from dreamml.logging import get_logger

_logger = get_logger(__name__)


def update_notebooks(notebooks: List[Path], version=None):
    """
    Update a list of Jupyter notebooks to use the specified mpack kernel version.

    Args:
        notebooks (List[Path]): A list of Path objects pointing to notebook files.
        version (Optional[str], optional): The version to update the kernel to.
            If None, the version from dreamml.__version__ is used. Defaults to None.
    """
    for notebook_path in notebooks:
        try:
            update_notebook_mpack_kernel(notebook_path, version)
        except NotJSONError as e:
            _logger.exception(e)


def gather_notebooks(path: Union[Path, str]):
    """
    Gather all Jupyter notebook paths from the specified directory, excluding hidden
    directories and notebooks that start with an underscore.

    Args:
        path (Union[Path, str]): The directory path to search for notebook files.

    Returns:
        List[Path]: A list of Path objects pointing to the found notebook files.
    """
    path = Path(path)

    notebook_paths = [
        notebook_path
        for notebook_path in path.glob("**/*.ipynb")
        if not any(
            part.startswith(".") for part in notebook_path.relative_to(path).parts
        )
        and not notebook_path.stem.startswith("_")
    ]

    return notebook_paths


def update_notebook_mpack_kernel(notebook_path, version=None):
    """
    Update the kernel specification of a Jupyter notebook to use the mpack kernel.

    This function reads the notebook file, updates its kernel specification to the
    specified mpack kernel version, and writes the changes back to the file.

    Args:
        notebook_path (Path): The path to the notebook file to update.
        version (Optional[str], optional): The version to set for the kernel.
            If None, the version from dreamml.__version__ is used. Defaults to None.

    Raises:
        FileNotFoundError: If the notebook file does not exist.
        nbformat.reader.NotJSONError: If the notebook file is not a valid JSON.
    """
    # Read the notebook content
    with open(notebook_path, "r", encoding="utf-8") as notebook_file:
        notebook_node = nbformat.read(notebook_file, as_version=4)

    if version is None:
        version = dreamml.__version__

    kernelspec = get_mpack_kernelspec_by_version(version)

    notebook_node["metadata"]["kernelspec"]["display_name"] = kernelspec["display_name"]
    notebook_node["metadata"]["kernelspec"]["name"] = kernelspec["name"]

    with open(notebook_path, "w", encoding="utf-8") as notebook_file:
        nbformat.write(notebook_node, notebook_file)


def get_mpack_kernelspec_by_version(version: str):
    """
    Generate the mpack kernel specification dictionary based on the provided version.

    The kernel name incorporates the version without dots, and the display name
    includes the current Python version, kernel name, and version.

    Args:
        version (str): The version string to generate the kernel specification for.

    Returns:
        dict: A dictionary containing the kernel specification with keys:
            - "display_name": The display name of the kernel.
            - "language": The programming language of the kernel (always "python").
            - "name": The internal name of the kernel.
    """
    version_joined = version.replace(".", "")

    kernelname = f"dmlmpack{version_joined}"

    python_string = f"py{sys.version_info[0]}.{sys.version_info[1]}"

    kernelspec = {
        "display_name": f"{python_string}_{kernelname}_{version}",
        "language": "python",
        "name": kernelname,
    }

    return kernelspec