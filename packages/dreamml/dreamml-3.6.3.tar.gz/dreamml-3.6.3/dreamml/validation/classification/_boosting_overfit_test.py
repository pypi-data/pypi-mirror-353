import numpy as np
import pandas as pd

from deepchecks.tabular import Dataset
from dreamml.validation.deepchecks_wrapper import DeepChecksWrapper

class BoostingOverfitTest:

    def __init__(self, estimator):
        self.deepchecks = DeepChecksWrapper(estimator.estimator)

    def transform(self, **data):
        result_dict = {}

        train_dataset = Dataset(data["train"][0], data["train"][1])
        test_dataset = Dataset(data["test"][0], data["test"][1])

        result = self.deepchecks.boosting_overfit_wrapper(train_dataset, test_dataset)
        traffic_light_boosting_overfit = "None"

        result = pd.DataFrame(result_dict)
        return result, traffic_light_boosting_overfit