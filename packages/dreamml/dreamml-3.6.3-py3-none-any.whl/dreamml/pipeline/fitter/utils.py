from typing import Optional, Type

from dreamml.configs.config_storage import ConfigStorage
from dreamml.logging import get_logger
from dreamml.modeling.cv import BaseCrossValidator
from dreamml.pipeline.fitter._cv import _get_cv
from dreamml.pipeline.fitter import *
from dreamml.utils import ValidationType


_logger = get_logger(__name__)


def choose_validation_type_by_data_size(size: int) -> ValidationType:
    """
    Determines the validation type based on the size of the training dataset.

    Args:
        size (int): The size of the training dataset.

    Returns:
        ValidationType: The selected validation type.
            - ValidationType.CV: Cross-validation will be used.
            - ValidationType.HOLDOUT: Hold-out validation will be used.
    """
    return ValidationType.CV if size < 250000 else ValidationType.HOLDOUT


def get_fitter(
    config: ConfigStorage,
    data_size: Optional[int] = None,
    custom_cv: Optional[Type[BaseCrossValidator]] = None,
    vectorization_name: Optional[str] = None,
    algo: str = None,
) -> FitterBase:
    """
    Selects and returns the appropriate fitter based on the configuration and parameters.

    Args:
        config (ConfigStorage): The configuration storage.
        data_size (Optional[int], optional): The size of the data. Defaults to None.
        custom_cv (Optional[Type[BaseCrossValidator]], optional): A custom cross-validator class. Defaults to None.
        vectorization_name (Optional[str], optional): The name of the vectorization method. Defaults to None.
        algo (str, optional): The algorithm name. Defaults to None.

    Returns:
        FitterBase: An instance of the appropriate fitter.

    Raises:
        ValueError: If `data_size` is None when `validation_type` is set to 'auto'.
        ValueError: If an unsupported validation type is provided.
    """
    if vectorization_name == "bert":
        return FitterHO()
    if config.pipeline.task == "anomaly_detection":
        if algo == "iforest":
            return FitterIsolationForest()
        return FitterHO()

    if config.pipeline.validation_type == "auto":
        if data_size is None:
            raise ValueError("Can't get fitter automatically without data_size")

        validation = choose_validation_type_by_data_size(data_size)
    else:
        validation = config.pipeline.validation_type

    validation = ValidationType(validation)

    if config.pipeline.task == "amts_ad":
        if custom_cv is not None:
            _logger.warning(
                "Передан класс `custom_cv` для кастомной кросс-валидации, который не поддерживается для amts_ad задачи."
            )
        return FitterAMTSab()

    if config.pipeline.task == "amts":
        if custom_cv is not None:
            _logger.warning(
                "Передан класс `custom_cv` для кастомной кросс-валидации, который не поддерживается для amts задачи."
            )
        return FitterAMTS()

    if config.pipeline.task == "topic_modeling":
        if custom_cv is not None:
            _logger.warning(
                "Передан класс `custom_cv` для кастомной кросс-валидации, который не поддерживается для topic_modeling задачи."
            )
        return FitterClustering()

    if validation == ValidationType.CV:
        cv = _get_cv(config, custom_cv=custom_cv)

        return FitterCV(cv)
    elif validation == ValidationType.HOLDOUT:
        if custom_cv is not None:
            _logger.warning(
                "Передан класс `custom_cv` для кастомной кросс-валидации, но тип валидации `validation_type` выбран не cv."
            )

        return FitterHO()
    else:
        raise ValueError(f"Can't get fitter for validation type = {validation.value}.")