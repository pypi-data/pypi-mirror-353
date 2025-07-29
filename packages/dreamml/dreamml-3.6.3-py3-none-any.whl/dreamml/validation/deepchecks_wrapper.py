import numpy as np
import pandas as pd
from typing import Dict

from deepchecks.tabular import Dataset
from deepchecks.tabular.checks import (
    SegmentPerformance, SimpleModelComparison, ModelInferenceTime, SingleDatasetPerformance,
    TrainTestPerformance, RocReport, ConfusionMatrixReport, BoostingOverfit, PredictionDrift,
    CalibrationScore
)

class DeepChecksWrapper:
    def __init__(self, model):
        self.model = model

    def segment_performance_wrapper(self, dataset: Dataset) -> Dict:
        test = SegmentPerformance()

        test_run_params = {
            "dataset": dataset,
            "model": self.model,
            "with_display": False,
        }

        result = test.run(**test_run_params).value
        return result

    def simple_model_comparison_wrapper(self, train_dataset: Dataset, test_dataset: Dataset) -> Dict:
        test_params = {
            "strategy": "tree",
            "max_depth": 5,
        }
        test = SimpleModelComparison(**test_params)

        test_run_params = {
            "train_dataset": train_dataset,
            "test_dataset": test_dataset,
            "model": self.model,
            "with_display": False,
        }
        result = test.run(**test_run_params).value
        return result

    def model_inference_time_wrapper(self, dataset: Dataset) -> Dict:
        test = ModelInferenceTime()
        test_run_params = {
            "dataset": dataset,
            "model": self.model,
            "with_display": False,
        }
        result = test.run(**test_run_params).value
        return result

    def single_dataset_performance_wrapper(self, dataset: Dataset) -> Dict:
        test_params = {
            "scorers": ["recall_per_class", "precision_per_class", "f1_macro", "f1_micro"]
        }
        test = SingleDatasetPerformance(**test_params)

        test_run_params = {
            "dataset": dataset,
            "model": self.model,
            "with_display": False,
        }
        result = test.run(**test_run_params).value
        return result

    def train_test_performance_wrapper(self, train_dataset: Dataset, test_dataset: Dataset) -> Dict:
        test_params = {
            "scorers": ["recall_per_class", "precision_per_class", "f1_macro", "f1_micro"]
        }
        test = TrainTestPerformance(**test_params)

        test_run_params = {
            "train_dataset": train_dataset,
            "test_dataset": test_dataset,
            "model": self.model,
            "with_display": False,
        }
        result = test.run(**test_run_params).value
        return result

    def roc_report_wrapper(self, dataset: Dataset) -> Dict:
        check = RocReport()

        test_run_params = {
            "dataset": dataset,
            "model": self.model,
            "with_display": False,
        }
        result = check.run(**test_run_params).value
        return result

    def confusion_matrix_report_wrapper(self, dataset: Dataset) -> Dict:
        test = ConfusionMatrixReport()

        test_run_params = {
            "dataset": dataset,
            "model": self.model,
            "with_display": False,
        }
        result = test.run(**test_run_params).value
        return result

    def boosting_overfit_wrapper(self, train_dataset: Dataset, test_dataset: Dataset) -> Dict:
        test = BoostingOverfit()

        test_run_params = {
            "train_dataset": train_dataset,
            "test_dataset": test_dataset,
            "model": self.model,
            "with_display": False,
        }
        result = test.run(**test_run_params).value
        return result

    def prediction_drift_wrapper(self, train_dataset: Dataset, test_dataset: Dataset) -> Dict:
        test = PredictionDrift()

        test_run_params = {
            "train_dataset": train_dataset,
            "test_dataset": test_dataset,
            "model": self.model,
            "with_display": False,
        }
        result = test.run(**test_run_params).value
        return result

    def calibration_score_wrapper(self, dataset: Dataset) -> Dict:
        test = CalibrationScore()

        test_run_params = {
            "dataset": dataset,
            "model": self.model,
            "with_display": False,
        }
        result = test.run(**test_run_params).value
        return result
















