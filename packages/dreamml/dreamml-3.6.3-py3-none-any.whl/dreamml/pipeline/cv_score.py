import dataclasses


# TODO добавить хранение названия метрики, для которой считался cv_score,
#  чтобы можно было выводить в отчёт gini и разные метрики для регерссии.
@dataclasses.dataclass
class CVScores:
    """Stores cross-validation score metrics for main and other models.

    Attributes:
        stage_models (dict): A dictionary containing CV scores for the primary models.
        other_models (dict): A dictionary containing CV scores for the other models.
    """

    stage_models: dict = dataclasses.field(default_factory=dict)
    other_models: dict = dataclasses.field(default_factory=dict)

    @property
    def is_full(self):
        """Checks if the CV scores dictionaries are populated.

        Returns:
            bool: True if either stage_models or other_models contains CV scores, False otherwise.
        """
        return self.stage_models or self.other_models