import numpy as np
import pandas as pd

class GiniTest:
    """
    Performs Gini coefficient based testing using a provided estimator and metric.

    Attributes:
        estimator: The estimator used to make predictions.
        metric: The metric function to evaluate predictions.
    """

    def __init__(self, estimator, metric):
        """
        Initializes the GiniTest with an estimator and a metric.

        Args:
            estimator: The estimator used to make predictions.
            metric: The metric function to evaluate predictions.
        """
        self.estimator = estimator
        self.metric = metric

    def transform(self, **data):
        """
        Transforms the input data by applying the estimator and metric, and calculates Gini degradation.

        Args:
            **data: Arbitrary keyword arguments representing samples.
                   Each key is a sample name, and each value is a tuple where the first element
                   is the input data and the second element is the true labels.

        Returns:
            tuple: A pandas DataFrame containing the metric and traffic light status for each sample,
                   and a string indicating the traffic light status for Gini degradation.

        Raises:
            KeyError: If 'train' or 'test' keys are missing in the input data.
        """
        result_dict = {}

        for sample in data.keys():
            y_true = data[sample][1]
            y_pred = self.estimator.transform(data[sample][0])
            metric = self.metric(y_true, y_pred)

            traffic_light = "red"
            if metric >= 0.4:
                traffic_light = "yellow"
            if metric >= 0.6:
                traffic_light = "green"
            result_dict.update({sample: [metric, traffic_light]})

        gini_degradation = (result_dict["train"][0] - result_dict["test"][0]) / result_dict["test"][0]
        traffic_light_gini_degradation = "red"
        if gini_degradation <= 0.3:
            traffic_light_gini_degradation = "yellow"
        if gini_degradation <= 0.1:
            traffic_light_gini_degradation = "green"
        result_dict.update({"gini_degradation": [gini_degradation, traffic_light_gini_degradation]})

        result = pd.DataFrame(result_dict)
        return result, traffic_light_gini_degradation