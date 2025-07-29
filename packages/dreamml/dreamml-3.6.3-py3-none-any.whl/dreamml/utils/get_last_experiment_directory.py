import os
from typing import Optional


def get_last_experiment_dir(path_to_results: str = "../results/") -> str:
    """
    Returns the path to the most recent experiment directory for model creation in dreamml_base.

    The latest experiment is determined by the number of directories in the results folder.
    For example, if there are 35 directories, it searches for the experiment with the number
    35 at the end. If no directories are found, it selects the path with the most recent
    modification date, as obtaining the creation date of a directory can be challenging.

    Args:
        path_to_results (str, optional): Path to the folder containing experiment results.
            Defaults to "../results/" for execution from dreamml_base notebooks.

    Returns:
        str: Path to the latest experiment directory.

    Raises:
        Exception: If the last experiment directory cannot be determined. Ensure that the
            path is correct and that experiments exist.
    """
    from dreamml.utils.saver import BaseSaver

    artifact_saver = BaseSaver(path_to_results)
    dml_dirs = artifact_saver.get_dreamml_experiment_dirs()

    last_experiment_dir = None
    last_created_time = 0
    for dml_dir in dml_dirs:
        path = os.path.join(path_to_results, dml_dir, artifact_saver._dml_version_file)

        modified_time = os.path.getmtime(path)

        if modified_time > last_created_time:
            last_created_time = modified_time
            last_experiment_dir = dml_dir

    if last_experiment_dir is None:
        raise Exception(
            "Can't determine last experiment directory. Check that the path is correct and experiments exist."
        )

    return last_experiment_dir


def get_experiment_dir_path(
    results_dir_path: str,
    experiment_dir_name: Optional[str] = None,
    use_last_experiment_directory: bool = False,
    raise_exception: bool = True,
) -> str:
    """
    Retrieves the path to a specific experiment directory or the most recent one.

    If `use_last_experiment_directory` is set to True, the function will determine the
    latest experiment directory using `get_last_experiment_dir`. Otherwise, it will use the
    provided `experiment_dir_name`. If `experiment_dir_name` is not provided and
    `raise_exception` is True, a ValueError is raised. If `raise_exception` is False and
    `experiment_dir_name` is not provided, the directory name defaults to an empty string.

    Args:
        results_dir_path (str): Path to the results directory.
        experiment_dir_name (Optional[str], optional): Name of the experiment directory.
            Defaults to None.
        use_last_experiment_directory (bool, optional): Flag indicating whether to use the
            most recent experiment directory. Defaults to False.
        raise_exception (bool, optional): Flag indicating whether to raise an exception
            if `experiment_dir_name` is not provided. Defaults to True.

    Returns:
        str: Path to the specified experiment directory.

    Raises:
        ValueError: If `use_last_experiment_directory` is False, `experiment_dir_name` is
            not provided, and `raise_exception` is True.
    """
    if use_last_experiment_directory:
        dir_name = get_last_experiment_dir(results_dir_path)
    else:
        if experiment_dir_name is None and raise_exception:
            raise ValueError(
                f"Experiment directory name must be provided when use_last_experiment_directory is {use_last_experiment_directory}."
            )
        elif not raise_exception:
            experiment_dir_name = ""
        dir_name = experiment_dir_name

    experiment_dir_path = os.path.join(results_dir_path, dir_name)

    return experiment_dir_path