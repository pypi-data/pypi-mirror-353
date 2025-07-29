import pandas as pd

class FTest:
    """FTest class for evaluating estimator performance using a specified metric.

    This class takes an estimator and a metric function to evaluate the performance
    of the estimator on provided datasets. It computes metrics for each sample and
    assigns a traffic light status based on the metric value.

    Attributes:
        estimator: An object that has a `transform` method to generate predictions.
        metric: A function that takes true values and predicted values to compute a metric.
    """

    def __init__(self, estimator, metric):
        """Initializes the FTest with an estimator and a metric.

        Args:
            estimator: An object that implements a `transform` method for making predictions.
            metric: A function that computes a metric given true and predicted values.
        """
        self.estimator = estimator
        self.metric = metric

    def transform(self, **data):
        """Transforms the input data using the estimator and evaluates with the metric.

        For each sample in the provided data, this method performs the following:
        - Uses the estimator to predict values.
        - Computes the metric between the true and predicted values.
        - Assigns a traffic light status based on the metric value:
            - "red" if metric < 0.6
            - "yellow" if 0.6 <= metric < 0.8
            - "green" if metric >= 0.8

        After evaluating all samples, it determines an overall traffic light status:
            - "red" if any sample is "red".
            - "yellow" if any sample is "yellow" and none are "red".
            - "green" if all samples are "green".

        Args:
            **data: Arbitrary keyword arguments where each key represents a sample name and
                   each value is a tuple or list containing input data and true values.

        Returns:
            tuple: A pandas DataFrame containing the metric and traffic light status for each sample,
                   and a string representing the overall traffic light status.

        Raises:
            AttributeError: If the estimator does not have a `transform` method.
            TypeError: If the metric function is not callable.
            KeyError: If the provided data does not contain expected keys.
            Exception: For any other exceptions raised during transformation or metric computation.
        """
        result_dict = {}

        for sample in data.keys():
            y_true = data[sample][1]
            y_pred = self.estimator.transform(data[sample][0])
            metric_value = self.metric(y_true, y_pred)

            traffic_light = "red"
            if metric_value >= 0.6:
                traffic_light = "yellow"
            if metric_value >= 0.8:
                traffic_light = "green"
            result_dict.update({sample: [metric_value, traffic_light]})

        result_traffic_light = "green"
        for key, value in result_dict.items():
            if value[1] == "yellow":
                result_traffic_light = "yellow"
            if value[1] == "red":
                result_traffic_light = "red"
                break

        result = pd.DataFrame(result_dict)
        return result, result_traffic_light