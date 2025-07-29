import numpy as np
import pandas as pd

from deepchecks.tabular import Dataset
from dreamml.validation.deepchecks_wrapper import DeepChecksWrapper

class TrainTestPerformanceTest:

    def __init__(self, estimator):
        self.deepchecks = DeepChecksWrapper(estimator.estimator)

    def transform(self, **data):
        train_dataset = Dataset(data["train"][0], data["train"][1])
        test_dataset = Dataset(data["test"][0], data["test"][1])

        result = self.deepchecks.train_test_performance_wrapper(train_dataset, test_dataset)
        traffic_light_train_test_performance = "None"

        return result, traffic_light_train_test_performance