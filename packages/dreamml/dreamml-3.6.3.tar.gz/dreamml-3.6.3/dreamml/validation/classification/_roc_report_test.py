import numpy as np
import pandas as pd

from deepchecks.tabular import Dataset
from dreamml.validation.deepchecks_wrapper import DeepChecksWrapper

class RocReportTest:

    def __init__(self, estimator):
        self.deepchecks = DeepChecksWrapper(estimator.estimator)

    def transform(self, **data):
        result_dict = {}

        for sample in data.keys():
            x = data[sample][0]
            y_true = data[sample][1]
            dataset = Dataset(x, y_true)
            sample_result = self.deepchecks.roc_report_wrapper(dataset)

            result_dict.update({sample: [0, "None"]})

        traffic_light_roc_report = "None"
        result = pd.DataFrame(result_dict)
        return result, traffic_light_roc_report