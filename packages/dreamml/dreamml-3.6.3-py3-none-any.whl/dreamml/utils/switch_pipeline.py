from itertools import islice
from sklearn.pipeline import Pipeline
from collections import defaultdict


class SwitchPipeline(Pipeline):
    """
    A custom Pipeline that allows enabling or disabling specific steps dynamically.

    This class extends scikit-learn's Pipeline to provide the functionality to toggle
    individual pipeline steps on or off using the `enabled_steps` parameter.
    """

    _required_parameters = ["steps"]

    def __init__(self, steps, *, memory=None, verbose=False, enabled_steps=None):
        """
        Initialize the SwitchPipeline.

        Args:
            steps (list of tuples): List of (name, transform) tuples that are chained in the pipeline.
            memory (str or object, optional): Used to cache the fitted transformers of the pipeline.
                Defaults to None.
            verbose (bool, optional): If True, the pipeline prints progress messages. Defaults to False.
            enabled_steps (dict, optional): Dictionary mapping step names to booleans indicating
                whether each step is enabled. If None, all steps are enabled by default.
                Defaults to None.

        Raises:
            ValueError: If the steps parameter is not properly defined.
        """
        self.enabled_steps = enabled_steps
        if self.enabled_steps is None:
            self.enabled_steps = {name: True for name, _ in steps}
        super().__init__(steps, memory=memory, verbose=verbose)

    def get_params(self, deep=True):
        """
        Get parameters for this pipeline.

        Args:
            deep (bool, optional): If True, will return the parameters for this pipeline and
                contained subobjects that are estimators. Defaults to True.

        Returns:
            dict: Parameter names mapped to their values, including the enabled status of each step.
        """
        out = {}
        if deep:
            out = {
                f"{name}__enabled": enabled
                for name, enabled in self.enabled_steps.items()
            }
        return {**self._get_params("steps", deep=deep), **out}

    def set_params(self, **kwargs):
        """
        Set the parameters of this pipeline.

        Args:
            **kwargs: Dictionary of parameter names mapped to their new values.

        Returns:
            self: This pipeline instance.

        Raises:
            ValueError: If an invalid parameter name is provided.
        """
        valid_params = self.get_params(deep=True)

        params = kwargs.copy()
        nested_params = defaultdict(dict)
        for full_key, value in params.items():
            key, delim, sub_key = full_key.partition("__")
            if sub_key == "enabled" and key in valid_params and delim:
                self.enabled_steps[key] = value
            else:
                nested_params[full_key] = value

        self._set_params("steps", **nested_params)
        return self

    def _iter(self, with_final=True, filter_passthrough=True):
        """
        Iterate over the pipeline steps.

        Args:
            with_final (bool, optional): If False, excludes the final estimator from the iteration.
                Defaults to True.
            filter_passthrough (bool, optional): If True, filters out steps that are 'passthrough'
                or None transformers. Defaults to True.

        Yields:
            tuple: A tuple containing the index, name, and transformer of each enabled step.
        """
        stop = len(self.steps)
        if not with_final:
            stop -= 1

        for idx, (name, trans) in enumerate(islice(self.steps, 0, stop)):
            if self.enabled_steps[name]:
                if not filter_passthrough:
                    yield idx, name, trans
                elif trans is not None and trans != "passthrough":
                    yield idx, name, trans