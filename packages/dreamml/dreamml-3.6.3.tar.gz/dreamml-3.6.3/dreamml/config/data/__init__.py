from typing import Optional, List, Union

from pydantic import model_validator

from dreamml.config._base_config import BaseConfig


class ColumnsConfig(BaseConfig):
    target_name: Optional[Union[str, List[str]]] = None
    drop_features: List[str]
    remaining_features: List[str]
    never_used_features: List[str]
    categorical_features: List[str]
    text_features: List[str]
    text_features_preprocessed: List[str]
    group_column: Optional[Union[str, List[str]]] = None
    time_column: Optional[str] = None
    time_column_format: Optional[str] = None
    time_column_period: Optional[str] = None
    weights_column: Optional[str] = None

    @model_validator(mode="after")
    def _check_categorical_in_never_used_features(self):
        for feature in self.categorical_features:
            if feature in self.never_used_features:
                raise ValueError(
                    f"'{feature}' column is found in `never_used_features`. "
                    f"Please remove '{feature}' column from "
                    f"`categorical_features` or `never_used_features`."
                )

        return self


class SparkConfig(BaseConfig):
    temp_dir_path: str


class ValidationParamsConfig(BaseConfig):
    cv_params: dict


class SplittingConfig(BaseConfig):
    shuffle: bool
    stratify: bool
    split_params: List[float]
    oot_split_test: bool
    oot_split_valid: bool
    split_oot_from_dev: bool
    oot_split_n_values: int
    split_by_group: bool
    split_by_time_period: bool
    time_series_split: bool
    time_series_window_split: bool
    time_series_split_test_size: Optional[int] = None
    time_series_split_gap: int
    cv_n_folds: int
    validation_params: ValidationParamsConfig
    custom_cv: bool


class AugmentationConfig(BaseConfig):
    text_augmentations: List
    aug_p: float
    additional_stopwords: List[str]
    aug_balance_classes: bool


class DataConfig(BaseConfig):

    dev_path: Optional[str] = None
    oot_path: Optional[str] = None
    train_path: Optional[str] = None
    valid_path: Optional[str] = None
    test_path: Optional[str] = None
    use_compression: bool
    spark: SparkConfig
    columns: ColumnsConfig
    use_sampling: bool
    splitting: SplittingConfig
    augmentation: AugmentationConfig

    @model_validator(mode="after")
    def _check_time_column_provided(self):
        if self.columns.time_column is None:
            if (
                self.splitting.oot_split_test
                or self.splitting.oot_split_valid
                or self.splitting.time_series_split
                or self.splitting.time_series_window_split
                or self.splitting.split_by_time_period
            ):
                raise ValueError("`time_column` is not selected for splitting.")

        return self

    @model_validator(mode="after")
    def _check_group_column_provided(self):
        if self.columns.group_column is None and self.splitting.split_by_group:
            raise ValueError("`group_column` is not selected for splitting.")

        return self
