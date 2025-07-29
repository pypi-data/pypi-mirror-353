import numpy as np
import pandas as pd

from dreamml.validation.deepchecks_wrapper import DeepChecksWrapper
from deepchecks.tabular import Dataset

class SimpleModelComparisonTest:

    def __init__(self, estimator):
        self.deepchecks = DeepChecksWrapper(estimator.estimator)

    def transform(self, **data):

        train_dataset = Dataset(data["train"][0], data["train"][1])
        test_dataset = Dataset(data["test"][0], data["test"][1])

        result = self.deepchecks.simple_model_comparison_wrapper(train_dataset, test_dataset)

        df = pd.DataFrame(result["scores"]['F1']).T
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'class'}, inplace=True)

        traffic_light_segment_performance = "None"

        return df, traffic_light_segment_performance