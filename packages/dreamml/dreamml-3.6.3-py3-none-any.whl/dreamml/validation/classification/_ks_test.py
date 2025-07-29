from scipy import stats
import pandas as pd

class KSTest:
    """Performs Kolmogorov-Smirnov tests on prediction results.

    This class uses an estimator to transform input data and then
    conducts the Kolmogorov-Smirnov statistical test to compare the
    distribution of predicted values for positive and negative classes.
    It also assigns a traffic light status based on the p-value of the test.

    Attributes:
        estimator: An object with a `transform` method used to process input data.
    """

    def __init__(self, estimator):
        """Initializes the KSTest with the given estimator.

        Args:
            estimator: An object that has a `transform` method to process input data.
        """
        self.estimator = estimator

    def transform(self, **data):
        """Transforms input data and performs Kolmogorov-Smirnov tests.

        For each sample in the input data, this method transforms the input features
        using the estimator, separates the predictions based on the true labels,
        performs the Kolmogorov-Smirnov test between positive and negative predictions,
        and assigns a traffic light status based on the p-value.

        Args:
            **data: Variable keyword arguments where each key represents
                a sample name and the value is a tuple or list containing:
                    - The input features for transformation.
                    - The true labels as a pandas Series or similar structure.

        Returns:
            tuple:
                - pd.DataFrame: A DataFrame where each column corresponds to a sample
                  and contains the KS statistic and traffic light status.
                - str: The overall traffic light status based on individual sample results.

        Raises:
            ValueError: If the input data is not in the expected format.
            Exception: If an error occurs during data transformation or statistical testing.
        """
        result_dict = {}

        for sample in data.keys():
            y_true = data[sample][1].values
            y_pred = self.estimator.transform(data[sample][0])

            y_pred_pos = [y_pred[i] for i in range(len(y_true)) if y_true[i] == 1]
            y_pred_neg = [y_pred[i] for i in range(len(y_true)) if y_true[i] == 0]
            ks_stat, p_value = stats.ks_2samp(y_pred_pos, y_pred_neg)

            traffic_light = "red"
            if 0.01 <= p_value <= 0.05:
                traffic_light = "yellow"
            if p_value < 0.01:
                traffic_light = "green"
            result_dict.update({sample: [ks_stat, traffic_light]})

        result_traffic_light = "green"
        for key, value in result_dict.items():
            if value[1] == "yellow":
                result_traffic_light = "yellow"
            if value[1] == "red":
                result_traffic_light = "red"
                break

        result = pd.DataFrame(result_dict)
        return result, result_traffic_light