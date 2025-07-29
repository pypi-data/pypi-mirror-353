import pandas as pd
from sklearn.metrics import mutual_info_score


class CIECTest:
    """Performs CIEC (Conditional Information Entropy Coefficient) tests using a provided estimator.

    This class uses the given estimator to transform input data and calculates the CIEC
    for each sample. It also determines a traffic light status based on the CIEC value.

    Args:
        estimator: An estimator object that must have a `transform` method. This method
            is used to obtain prediction probabilities for the input data.

    """

    def __init__(self, estimator):
        self.estimator = estimator

    def transform(self, **data):
        """Transforms the input data using the estimator and computes CIEC metrics.

        For each sample in the input data, the method calculates the mutual information
        between the true labels and the predicted labels derived from the estimator's
        predictions. Based on the CIEC value, it assigns a traffic light color:
        - "red" if CIEC < 0.4
        - "yellow" if 0.4 ≤ CIEC < 0.6
        - "green" if CIEC ≥ 0.6

        Additionally, it determines an overall traffic light status based on individual
        sample statuses.

        Args:
            **data: Arbitrary keyword arguments where each key represents a sample name and
                its value is a tuple or list containing:
                - The input features for the estimator.
                - The true labels as a pandas Series or DataFrame.

        Returns:
            tuple:
                - pd.DataFrame: A DataFrame where each column corresponds to a sample and
                  contains a list with the CIEC value and the associated traffic light color.
                - str: The overall traffic light status, which is "green", "yellow", or "red"
                  based on the individual sample statuses.

        Raises:
            KeyError: If a sample does not contain the expected data structure with at least
                two elements (features and true labels).
            AttributeError: If the estimator does not have a `transform` method.
            ValueError: If the true labels are not in a valid format for mutual_info_score
                computation.

        """
        result_dict = {}

        for sample in data.keys():
            y_true = data[sample][1].values
            y_pred_proba = self.estimator.transform(data[sample][0])
            y_pred = [1 if pred >= 0.5 else 0 for pred in y_pred_proba]

            total_entropy = mutual_info_score(y_true, y_pred)
            entropy_y = mutual_info_score(y_true, y_true)
            ciec = (total_entropy / entropy_y)

            traffic_light = "red"
            if 0.4 <= ciec < 0.6:
                traffic_light = "yellow"
            if ciec >= 0.6:
                traffic_light = "green"
            result_dict.update({sample: [ciec, traffic_light]})

        result_traffic_light = "green"
        for key, value in result_dict.items():
            if value[1] == "yellow":
                result_traffic_light = "yellow"
            if value[1] == "red":
                result_traffic_light = "red"
                break

        result = pd.DataFrame(result_dict)
        return result, result_traffic_light