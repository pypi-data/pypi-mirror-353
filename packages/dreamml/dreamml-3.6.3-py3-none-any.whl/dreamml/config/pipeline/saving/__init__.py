from typing import Optional

from pydantic import model_validator

from dreamml.config._base_config import BaseConfig


class PersistentStorageSavingConfig(BaseConfig):
    storage_name: Optional[str] = None
    table_name: Optional[str] = None
    prefix: str
    suffix: str
    model_id: str


class SavingConfig(BaseConfig):
    path: str
    feature_threshold: int
    save_to_ps: bool
    persistent_storage: PersistentStorageSavingConfig

    @model_validator(mode="after")
    def _check_persistent_storage_config(self):
        if self.save_to_ps:
            if self.persistent_storage.storage_name is None:
                raise ValueError(
                    "`storage_name` has to be specified for saving to persistent storage."
                )

            if self.persistent_storage.table_name is None:
                raise ValueError(
                    "`table_name` has to be specified for saving to persistent storage."
                )

        return self
