import numpy as np
import pandas as pd

from deepchecks.tabular import Dataset
from dreamml.validation.deepchecks_wrapper import DeepChecksWrapper

class ConfusionMatrixReportTest:

    def __init__(self, estimator):
        self.deepchecks = DeepChecksWrapper(estimator.estimator)

    def transform(self, **data):
        result_dict = {}

        for sample in data.keys():
            x = data[sample][0]
            y_true = data[sample][1]
            dataset = Dataset(x, y_true)
            sample_result = self.deepchecks.confusion_matrix_report_wrapper(dataset)
            result_dict.update({sample: sample_result})

        traffic_light_confusion_matrix_report = "None"
        return result_dict, traffic_light_confusion_matrix_report