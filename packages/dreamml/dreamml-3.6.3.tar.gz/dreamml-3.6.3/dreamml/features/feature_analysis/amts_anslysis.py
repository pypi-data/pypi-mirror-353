import numpy as np
from statsmodels.tsa.stattools import adfuller, kpss, acf
from statsmodels.tsa.seasonal import STL
from scipy.stats import levene
from dreamml.data._dataset import DataSet


class AMTSAnalysisResult:
    """Stores the results of various time series analyses.

    Attributes:
        kpss_test_dict (dict): Results of the KPSS tests.
        adfuller_test_dict (dict): Results of the Augmented Dickey-Fuller tests.
        stl_dict (dict): Results of the STL decompositions.
        levene_dict (dict): Results of the Levene tests.
        period_dict (dict): Calculated periods for the time series.
    """

    def __init__(self):
        """Initializes a new instance of AMTSAnalysisResult with empty result dictionaries."""
        self.kpss_test_dict = {}
        self.adfuller_test_dict = {}
        self.stl_dict = {}
        self.levene_dict = {}
        self.period_dict = {}


class AMTSAnalysis:
    """Performs various time series analyses on a given dataset.

    This class conducts stationarity tests, STL decomposition, variance homogeneity tests,
    and period calculations on the provided dataset. Results are stored in an AMTSAnalysisResult instance.
    """

    def __init__(self, data_storage: DataSet):
        """Initializes the AMTSAnalysis with the provided dataset.

        Args:
            data_storage (DataSet): The dataset to be analyzed.

        Attributes:
            data_storage (DataSet): The dataset storage containing time series data.
            time_column (str): The name of the time column in the dataset.
            target_name (str): The name of the target variable in the dataset.
            split_by_group (bool): Whether to split the analysis by group.
            group_column (str): The name of the group column in the dataset.
            df (pd.DataFrame): The training dataframe extracted from the dataset.
            p_value_th (float): The p-value threshold for statistical tests.
            analysis_result (AMTSAnalysisResult): The object to store analysis results.
        """
        self.data_storage: DataSet = data_storage
        self.time_column = data_storage.time_column
        self.target_name = data_storage.target_name
        self.split_by_group = data_storage.split_by_group
        self.group_column = data_storage.group_column
        amts_data = self.data_storage.get_eval_set()
        self.df = amts_data["amts_final_data"]["train"][0]
        self.df[self.data_storage.target_name] = amts_data["amts_final_data"]["train"][
            1
        ]

        self.p_value_th = 0.05
        self.analysis_result = AMTSAnalysisResult()

    def analysis(self):
        """Performs the full analysis by executing all analysis methods.

        This method runs KPSS test, Augmented Dickey-Fuller test, calculates periods,
        performs STL decomposition, and conducts Levene's test for variance homogeneity.
        
        Raises:
            Exception: Propagates exceptions raised by any of the analysis methods.
        """
        self.kpss_test(self)
        self.adfuller_test(self)
        self.calculate_period(self)
        self.stl_decomposition(self)
        self.levene_test(self)
        pass

    @staticmethod
    def kpss_test(self):
        """Performs the KPSS test for stationarity on the time series data.

        If the analysis is split by group, the test is conducted for each group separately.
        The results are stored in the analysis_result.kpss_test_dict.

        Args:
            self (AMTSAnalysis): The instance of AMTSAnalysis performing the test.

        Raises:
            Exception: Catches and ignores any exceptions raised during the KPSS test.
        """
        if self.split_by_group:
            for group_name, df_group in self.df.groupby(self.data_storage.group_column):
                try:
                    result = kpss(df_group[self.target_name])
                except Exception as e:
                    pass
                _dict = {
                    f"segment_{group_name}": {
                        "test": "KPSS Test for Stationarity",
                        "test_statistics": None,
                        "p_value": None,
                        "output": None,
                    }
                }
                _dict[f"segment_{group_name}"]["test_statistics"] = result[0]
                _dict[f"segment_{group_name}"]["p_value"] = result[1]
                _dict[f"segment_{group_name}"]["output"] = (
                    "stationary" if result[1] > self.p_value_th else "nonstationary"
                )
                self.analysis_result.kpss_test_dict.update(_dict)
        else:
            result = kpss(self.df[self.target_name])
            _dict = {
                f"segment_0": {
                    "test": "KPSS Test for Stationarity",
                    "test_statistics": result[0],
                    "p_value": result[1],
                    "output": (
                        "stationary" if result[1] > self.p_value_th else "nonstationary"
                    ),
                }
            }
            self.analysis_result.kpss_test_dict.update(_dict)

    @staticmethod
    def adfuller_test(self):
        """Performs the Augmented Dickey-Fuller test for stationarity on the time series data.

        If the analysis is split by group, the test is conducted for each group separately.
        The results are stored in the analysis_result.adfuller_test_dict.

        Args:
            self (AMTSAnalysis): The instance of AMTSAnalysis performing the test.

        Raises:
            Exception: Catches and ignores any exceptions raised during the Augmented Dickey-Fuller test.
        """
        if self.split_by_group:
            for group_name, df_group in self.df.groupby(self.data_storage.group_column):
                try:
                    result = adfuller(df_group[self.target_name])
                except Exception as e:
                    pass
                _dict = {
                    f"segment_{group_name}": {
                        "test": "Augmented Dickey-Fuller Test for Stationarity",
                        "test_statistics": None,
                        "p_value": None,
                        "output": None,
                    }
                }
                _dict[f"segment_{group_name}"]["test_statistics"] = result[0]
                _dict[f"segment_{group_name}"]["p_value"] = result[1]
                _dict[f"segment_{group_name}"]["output"] = (
                    "stationary" if result[1] > self.p_value_th else "nonstationary"
                )
                self.analysis_result.adfuller_test_dict.update(_dict)
        else:
            result = adfuller(self.df[self.target_name])
            _dict = {
                f"segment_0": {
                    "test": "Augmented Dickey-Fuller Test for Stationarity",
                    "test_statistics": result[0],
                    "p_value": result[1],
                    "output": (
                        "stationary" if result[1] > self.p_value_th else "nonstationary"
                    ),
                }
            }
            self.analysis_result.adfuller_test_dict.update(_dict)

    @staticmethod
    def stl_decomposition(self):
        """Performs STL decomposition on the time series data.

        Decomposes the time series into trend, seasonal, and residual components.
        If the analysis is split by group, decomposition is performed for each group separately.
        The results are stored in the analysis_result.stl_dict.

        Args:
            self (AMTSAnalysis): The instance of AMTSAnalysis performing the decomposition.

        Raises:
            KeyError: If the period for a segment is not found in period_dict.
        """
        if self.data_storage.split_by_group:
            for group_name, df_group in self.df.groupby(self.data_storage.group_column):
                _dict = {
                    f"segment_{group_name}": {
                        "timeseries": None,
                        "target": None,
                        "trend": None,
                        "seasonal": None,
                        "resid": None,
                    }
                }
                stl_result = STL(
                    df_group[self.data_storage.target_name],
                    period=self.analysis_result.period_dict[f"segment_{group_name}"][
                        "lag"
                    ],
                ).fit()
                _dict[f"segment_{group_name}"]["timeseries"] = np.array(df_group["ds"])
                _dict[f"segment_{group_name}"]["target"] = np.array(
                    df_group[self.data_storage.target_name]
                )
                _dict[f"segment_{group_name}"]["trend"] = np.array(stl_result.trend)
                _dict[f"segment_{group_name}"]["seasonal"] = np.array(
                    stl_result.seasonal
                )
                _dict[f"segment_{group_name}"]["resid"] = np.array(stl_result.resid)
                self.analysis_result.stl_dict.update(_dict)
        else:
            stl_result = STL(
                self.df[self.target_name],
                period=self.analysis_result.period_dict["segment_0"]["lag"],
            ).fit()

            _dict = {
                f"segment_0": {
                    "timeseries": np.array(self.df["ds"]),
                    "target": np.array(self.df[self.data_storage.target_name]),
                    "trend": np.array(stl_result.trend),
                    "seasonal": np.array(stl_result.seasonal),
                    "resid": np.array(stl_result.resid),
                }
            }
            self.analysis_result.stl_dict.update(_dict)

    @staticmethod
    def levene_test(self):
        """Performs Levene's test for homogeneity of variances on the residuals.

        If the analysis is split by group, the test is conducted for each group separately.
        Residuals are divided into five groups based on their indices for the test.
        The results are stored in the analysis_result.levene_dict.

        Args:
            self (AMTSAnalysis): The instance of AMTSAnalysis performing the test.

        Raises:
            KeyError: If the residuals for a segment are not found in stl_dict.
        """
        if self.data_storage.split_by_group:
            for group_name, df_group in self.df.groupby(self.data_storage.group_column):
                n = len(self.analysis_result.stl_dict[f"segment_{group_name}"]["resid"])
                group_1 = self.analysis_result.stl_dict[f"segment_{group_name}"][
                    "resid"
                ][: int(n * 0.2)]
                group_2 = self.analysis_result.stl_dict[f"segment_{group_name}"][
                    "resid"
                ][int(n * 0.2) : int(n * 0.4)]
                group_3 = self.analysis_result.stl_dict[f"segment_{group_name}"][
                    "resid"
                ][int(n * 0.4) : int(n * 0.6)]
                group_4 = self.analysis_result.stl_dict[f"segment_{group_name}"][
                    "resid"
                ][int(n * 0.6) : int(n * 0.8)]
                group_5 = self.analysis_result.stl_dict[f"segment_{group_name}"][
                    "resid"
                ][int(n * 0.8) : int(n * 1)]

                test_statistics, p_value = levene(
                    group_1, group_2, group_3, group_4, group_5
                )
                _dict = {
                    f"segment_{group_name}": {
                        "test": "Levene's Test for Homogeneity of Residual Variances",
                        "test_statistics": None,
                        "p_value": None,
                        "output": None,
                    }
                }
                _dict[f"segment_{group_name}"]["test_statistics"] = test_statistics
                _dict[f"segment_{group_name}"]["p_value"] = p_value
                _dict[f"segment_{group_name}"]["output"] = (
                    "heteroscedasticity"
                    if p_value > self.p_value_th
                    else "homoscedasticity"
                )
                self.analysis_result.levene_dict.update(_dict)

        else:
            n = len(self.analysis_result.stl_dict["segment_0"]["resid"])
            group_1 = self.analysis_result.stl_dict["segment_0"]["resid"][
                : int(n * 0.2)
            ]
            group_2 = self.analysis_result.stl_dict["segment_0"]["resid"][
                int(n * 0.2) : int(n * 0.4)
            ]
            group_3 = self.analysis_result.stl_dict["segment_0"]["resid"][
                int(n * 0.4) : int(n * 0.6)
            ]
            group_4 = self.analysis_result.stl_dict["segment_0"]["resid"][
                int(n * 0.6) : int(n * 0.8)
            ]
            group_5 = self.analysis_result.stl_dict["segment_0"]["resid"][
                int(n * 0.8) : int(n * 1)
            ]

            test_statistics, p_value = levene(
                group_1, group_2, group_3, group_4, group_5
            )
            _dict = {
                f"segment_0": {
                    "test": "Levene's Test for Homogeneity of Residual Variances",
                    "test_statistics": test_statistics,
                    "p_value": p_value,
                    "output": (
                        "heteroscedasticity"
                        if p_value > self.p_value_th
                        else "homoscedasticity"
                    ),
                }
            }
            self.analysis_result.levene_dict.update(_dict)

    @staticmethod
    def calculate_period(self):
        """Calculates the periodicity of the time series data based on autocorrelation.

        Determines the lag with the highest average autocorrelation over its multiples.
        If the series is short (<=50 data points), a default period is assigned.
        If the analysis is split by group, the calculation is performed for each group separately.
        The results are stored in the analysis_result.period_dict.

        Args:
            self (AMTSAnalysis): The instance of AMTSAnalysis performing the calculation.
        """
        if self.split_by_group:
            for group_name, df_group in self.df.groupby(self.data_storage.group_column):
                if len(df_group[self.target_name]) > 50:
                    acf_result = acf(df_group[self.target_name], nlags=50)
                    max_lag, max_acf = 0, 0
                    for i in range(3, 50):
                        acf_sum, count = 0, 0
                        for j in range(i, 50, i):
                            count += 1
                            acf_sum += acf_result[j]
                            if max_acf < (acf_sum / count):
                                max_lag, max_acf = i, (acf_sum / count)
                else:
                    max_lag = 5
                    max_acf = 5

                _dict = {
                    f"segment_{group_name}": {
                        "test:": "Lag with Highest Autocorrelation",
                        "lag": None,
                        "max_acf": None,
                    }
                }
                _dict[f"segment_{group_name}"]["lag"] = max_lag
                _dict[f"segment_{group_name}"]["max_acf"] = max_acf
                self.analysis_result.period_dict.update(_dict)
        else:
            if len(self.df[self.target_name]) > 50:
                acf_result = acf(self.df[self.target_name], nlags=50)
                max_lag, max_acf = 0, 0
                for i in range(3, 50):
                    acf_sum, count = 0, 0
                    for j in range(i, 50, i):
                        count += 1
                        acf_sum += acf_result[j]
                        if max_acf < (acf_sum / count):
                            max_lag, max_acf = i, (acf_sum / count)
            else:
                max_lag = 5
                max_acf = 5

            _dict = {
                f"segment_0": {
                    "test:": "Lag with Highest Autocorrelation",
                    "lag": max_lag,
                    "max_acf": max_acf,
                }
            }
            self.analysis_result.period_dict.update(_dict)