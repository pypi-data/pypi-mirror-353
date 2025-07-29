import numpy as np
import pandas as pd

from deepchecks.tabular import Dataset
from dreamml.validation.deepchecks_wrapper import DeepChecksWrapper

class CalibrationScoreTest:

    def __init__(self, estimator):
        self.deepchecks = DeepChecksWrapper(estimator.estimator)

    def transform(self, **data):
        result_dict = {}

        for sample in data.keys():
            x = data[sample][0]
            y_true = data[sample][1]
            dataset = Dataset(x, y_true)
            sample_result = self.deepchecks.calibration_score_wrapper(dataset)
            df = pd.DataFrame(list(sample_result.items()), columns=['class', 'value'])
            result_dict.update({sample: df})

        traffic_light_calibration_score = "None"
        return result_dict, traffic_light_calibration_score