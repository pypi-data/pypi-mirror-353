import subprocess
import sys
import platform
import os
import shutil
import site
import warnings
import zipfile
from glob import glob
from pathlib import Path
from pyspark.sql import SparkSession

# name of archive for pyspark to copy on other nodes
from dreamml.logging import get_logger
from dreamml.utils.warnings import DMLWarning

pyspark_venv_name = "pyspark_venv"
archived_venv_path_for_pyspark = os.path.join(sys.prefix, f"{pyspark_venv_name}.zip")

# name of temp dir to copy current virtual env and editable packages
tmp_dir_for_copy_name = "archive_venv_tmp_dir"

# directory name which will be used for copying editable packages in temp dir
tmp_dir_editable_packages_dir_name = "editable_packages"

# contains paths to editable packages (because of using `pip install -e ...`)
editable_packages_pth_name = "easy-install.pth"

_logger = get_logger(__name__)


def _get_current_venv_path() -> str:
    """Get the current virtual environment path.

    Returns:
        str: The path to the current virtual environment.
    """
    return sys.prefix


def is_inheritable_venv():
    """Check if the current virtual environment is inheritable.

    Determines whether the current virtual environment can be inherited by checking for the existence of 'parent.pth' in site-packages directories.

    Returns:
        bool: True if the virtual environment is inheritable, False otherwise.
    """
    for site_packages_path in site.getsitepackages():
        pth_path = os.path.join(site_packages_path, "parent.pth")

        if os.path.exists(pth_path):
            return True

    return False


def get_editable_packages(sitepackages_dirs):
    """Retrieve editable packages from the given site-packages directories.

    Scans the specified site-packages directories for editable packages listed in 'easy-install.pth'.

    Args:
        sitepackages_dirs (list): A list of paths to site-packages directories.

    Returns:
        set: A set of paths to editable packages.
    """
    editable_packages = set()
    for sp_path in sitepackages_dirs:
        to_copy_pth_path = os.path.join(sp_path, editable_packages_pth_name)
        if os.path.exists(to_copy_pth_path):
            with open(to_copy_pth_path, "r") as f:
                packages_in_pth = [p for p in f.read().split("\n") if os.path.exists(p)]
                editable_packages.update(packages_in_pth)

    return editable_packages


def copy_package_sdist(pkg_root_path, destination):
    """Create a source distribution of a package and copy it to the destination.

    Generates a source distribution (sdist) in ZIP format using setup.py, extracts it, and copies the package to the specified destination directory.

    Args:
        pkg_root_path (str or Path): The root path of the package.
        destination (str or Path): The destination directory where the package will be copied.

    Raises:
        Exception: If 'setup.py' is not found or if the source distribution cannot be created or located.
    """
    pkg_root_path = Path(pkg_root_path)

    is_src_layout = pkg_root_path.name == "src"

    setup_dir_path = pkg_root_path.name if is_src_layout else pkg_root_path
    if not (setup_dir_path / "setup.py").exists():
        raise Exception("Can't find setup.py for making sdist")

    dist_dir_name = "dist_for_pyspark_dreamml"

    shutil.rmtree(setup_dir_path / dist_dir_name, ignore_errors=True)

    subprocess.check_call(
        [
            sys.executable,
            "setup.py",
            "sdist",
            f"--dist-dir={dist_dir_name}",
            "--formats=zip",
        ],
        cwd=setup_dir_path,
    )

    sdists = list((setup_dir_path / dist_dir_name).glob("*-[0-9]*.zip"))
    if len(sdists) != 1:
        raise Exception("Can't find sdist after setup.py")

    sdist_archive_path = sdists[0]

    with zipfile.ZipFile(sdist_archive_path, "r") as zip_ref:
        zip_ref.extractall(sdist_archive_path.parent)

    sdist_path = sdist_archive_path.parent / sdist_archive_path.stem

    if is_src_layout:
        sdist_path /= "src"

    shutil.copytree(sdist_path, destination, dirs_exist_ok=True)

    shutil.rmtree(setup_dir_path / dist_dir_name, ignore_errors=True)


def copy_package(pkg_root_path, destination):
    """Copy a package to the destination, preferring source distribution.

    Attempts to create a source distribution of the package and copy it to the destination. If it fails, copies the package directory directly.

    Args:
        pkg_root_path (str or Path): The root path of the package.
        destination (str or Path): The destination directory where the package will be copied.
    """
    pkg_root_path = Path(pkg_root_path)

    try:
        copy_package_sdist(pkg_root_path, destination)

    except Exception as e:
        _logger.exception(e)

        shutil.copytree(pkg_root_path, destination, dirs_exist_ok=True)


def transfer_packages_to_venv(pkgs_to_copy, sitepackages_dir):
    """Transfer editable packages to the virtual environment's site-packages directory.

    Copies the specified editable packages to a temporary directory within site-packages and updates the corresponding '.pth' file.

    Args:
        pkgs_to_copy (iterable): An iterable of paths to the packages to be copied.
        sitepackages_dir (str): The path to the site-packages directory where packages will be transferred.
    """
    editable_packages_path = os.path.join(
        sitepackages_dir, tmp_dir_editable_packages_dir_name
    )

    os.makedirs(editable_packages_path, exist_ok=True)

    new_pth_paths = []
    for pkg in pkgs_to_copy:
        pkg_name = Path(pkg).name

        pkg_dst = os.path.join(editable_packages_path, pkg_name)

        copy_package(pkg, pkg_dst)

        new_pth_paths.append(os.path.join(tmp_dir_editable_packages_dir_name, pkg_name))

    new_pth_content = "\n".join(new_pth_paths)

    with open(
        os.path.join(sitepackages_dir, f"{tmp_dir_editable_packages_dir_name}.pth"), "w"
    ) as f:
        f.write(new_pth_content)


def _copy_current_venv_to_tmp_dir(tmp_dir_path):
    """Copy the current virtual environment to a temporary directory excluding unnecessary files.

    Traverses the current virtual environment directory and copies its contents to the specified temporary directory, omitting certain directories and files.

    Args:
        tmp_dir_path (str or Path): The path to the temporary directory where the virtual environment will be copied.
    """
    venv_path = _get_current_venv_path()
    tmp_dir_path = Path(tmp_dir_path)

    # Используем os.walk, так как он не заходит в ссылку lib64 на lib
    for dirpath, dirnames, filenames in os.walk(venv_path):
        dirpath = Path(dirpath)

        if (
            dirpath.name.endswith(".dist-info")
            or dirpath.name == "__pycache__"
            or dirpath.name == tmp_dir_for_copy_name
        ):
            continue

        filenames = [name for name in filenames if name != f"{pyspark_venv_name}.zip"]

        dir_relative_path = dirpath.relative_to(venv_path)

        dirpath_in_tmp = tmp_dir_path / dir_relative_path
        os.makedirs(dirpath_in_tmp, exist_ok=True)

        for filename in filenames:
            shutil.copy(dirpath / filename, dirpath_in_tmp / filename)


def _add_editable_packages_to_venv(path):
    """Add editable packages to the virtual environment.

    Finds editable packages in the given path and transfers them to the virtual environment's site-packages directory. Removes existing '.pth' files for editable packages after transfer.

    Args:
        path (str or Path): The path to the virtual environment directory.
    """
    sitepackages_paths = site.getsitepackages([path])

    paths_withous_symlink = [path for path in sitepackages_paths if "lib64" not in path]
    if len(paths_withous_symlink) == 1:
        sitepackages_paths = paths_withous_symlink

    pkgs_to_copy = get_editable_packages(sitepackages_paths)

    transfer_packages_to_venv(pkgs_to_copy, sitepackages_paths[0])

    for sp_path in sitepackages_paths:
        to_copy_pth_path = os.path.join(sp_path, editable_packages_pth_name)

        if os.path.exists(to_copy_pth_path):
            os.remove(to_copy_pth_path)


def archive_current_venv():
    """Archive the current virtual environment for use with PySpark on other nodes.

    Copies the current virtual environment to a temporary directory, adds editable packages, creates a ZIP archive of the environment, and cleans up the temporary files.

    Raises:
        Exception: If an error occurs during the archiving process.
    """
    tmp_dir_path = os.path.join(_get_current_venv_path(), tmp_dir_for_copy_name)
    _copy_current_venv_to_tmp_dir(tmp_dir_path)
    _add_editable_packages_to_venv(tmp_dir_path)

    try:
        # FIXME: удалять архив после завершения работы
        shutil.make_archive(
            archived_venv_path_for_pyspark.split(".zip")[0],
            "zip",
            root_dir=tmp_dir_path,
            base_dir="",
        )
        shutil.rmtree(tmp_dir_path, ignore_errors=True)
    except Exception as e:
        shutil.rmtree(tmp_dir_path, ignore_errors=True)
        raise e


def init_spark_env(libraries_required=False):
    """Initialize the Spark environment.

    Sets up environment variables and paths required for Spark to operate correctly. Archives the current virtual environment if necessary and configures PySpark with the appropriate Python interpreter. Ensures that the correct versions of PySpark and Py4J are loaded.

    Args:
        libraries_required (bool, optional): Whether libraries are required for Spark. Defaults to False.

    Raises:
        RuntimeError: If the operating system is Windows.
    """
    # TODO: init only once per session

    if platform.system() == "Windows":
        raise RuntimeError("Can't initialize Spark on Windows")

    if "user-venvs" not in sys.executable:
        if is_inheritable_venv() and libraries_required:
            _logger.info(
                "Архивация текущего виртуального окружения для использования спарком на других узлах..."
            )
            archive_current_venv()

        if os.path.exists(archived_venv_path_for_pyspark) and libraries_required:
            python_path = f"./{pyspark_venv_name}/bin/python"
            os.environ["PYSPARK_DRIVER_PYTHON"] = python_path
            os.environ["PYSPARK_PYTHON"] = python_path
        else:
            python_path = sys.executable  # use same python as in current notebook
            os.environ["PYSPARK_DRIVER_PYTHON"] = os.environ.get(
                "PYSPARK_DRIVER_PYTHON", python_path
            )
            os.environ["PYSPARK_PYTHON"] = os.environ.get("PYSPARK_PYTHON", python_path)

        os.environ["SPARK_MAJOR_VERSION"] = "3"
        spark_home = "/usr/sdp/current/spark3-client"
        os.environ["SPARK_HOME"] = spark_home

        os.environ["LD_LIBRARY_PATH"] = "/opt/python/virtualenv/jupyter/lib"

        cluster_spark_python_location = os.path.join(spark_home, "python")

        py4j_version_pattern = os.path.join(
            cluster_spark_python_location, "lib/py4j-*.zip"
        )

        py4j = glob(py4j_version_pattern)
        if len(py4j) > 0:
            cluster_py4j_location = py4j[0]
        else:
            warnings.warn(
                f"Spark distribution is not found in {cluster_spark_python_location}",
                DMLWarning,
                stacklevel=2,
            )
            return

        # Замена версии pyspark на версию из сборки кластера
        sys.path.insert(0, cluster_spark_python_location)
        sys.path.insert(0, cluster_py4j_location)

        _check_pyspark_module_location(
            cluster_spark_python_location, cluster_py4j_location
        )


def _check_pyspark_module_location(
    cluster_spark_python_location, cluster_py4j_location
):
    """Reloads the 'pyspark' and 'py4j' modules from specified cluster paths if they are already imported.

    Ensures that the 'pyspark' and 'py4j' modules are loaded from the expected locations on the cluster by resetting them if necessary.

    Args:
        cluster_spark_python_location (str): The path to the Spark Python directory on the cluster.
        cluster_py4j_location (str): The path to the Py4J library on the cluster.
    """
    pyspark_expected_location = os.path.join(cluster_spark_python_location, "pyspark")
    py4j_expected_location = os.path.join(cluster_py4j_location, "py4j")

    import pyspark
    import py4j

    if len(pyspark.__path__) == 1:
        pyspark_location = pyspark.__path__[0]
        py4j_location = py4j.__path__[0]

        if (
            pyspark_location == pyspark_expected_location
            and py4j_location == py4j_expected_location
        ):
            return

        # Удаляем закэшированные модули, импортировнные по неправильному пути
        modules_to_del = []
        for module_name in sys.modules:
            if module_name.startswith("pyspark.") or module_name == "pyspark":
                modules_to_del.append(module_name)
            if module_name.startswith("py4j.") or module_name == "py4j":
                modules_to_del.append(module_name)

        for module_name in modules_to_del:
            del sys.modules[module_name]

        # Заново импортируем модули и проверяем, что пути соответствуют указанным
        import pyspark
        import py4j

        if pyspark.__path__[0] == pyspark_expected_location:
            _logger.debug(
                f"Module `pyspark` ({pyspark_location}) is reloaded from ({pyspark.__path__[0]})."
            )
        else:
            _logger.warning(
                f"Module `pyspark` is not found under expected location: {pyspark_expected_location}",
            )

        if py4j.__path__[0] == py4j_expected_location:
            _logger.debug(
                f"Module `py4j` ({py4j_location}) is reloaded from ({py4j.__path__[0]})."
            )
        else:
            _logger.warning(
                f"Module `py4j` is not found under expected location: {py4j_expected_location}",
            )
    else:
        warnings.warn(
            f"Unexpected pyspark.__path__ size: {pyspark.__path__}",
            DMLWarning,
            stacklevel=3,
        )