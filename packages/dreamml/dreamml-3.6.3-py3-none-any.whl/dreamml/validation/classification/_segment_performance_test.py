import os
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from dreamml.validation.deepchecks_wrapper import DeepChecksWrapper
from deepchecks.tabular import Dataset

class SegmentPerformanceTest:

    def __init__(self, estimator, images_dir_path):
        self.deepchecks = DeepChecksWrapper(estimator.estimator)
        self.images_dir_path = images_dir_path

    def transform(self, **data):
        result_dict = {}

        for sample in data.keys():
            x = data[sample][0]
            y_true = data[sample][1]
            dataset = Dataset(x, y_true)
            sample_result = self.deepchecks.segment_performance_wrapper(dataset)

            scores = np.array(sample_result['scores'], dtype=np.float64)

            fig, axes = plt.subplots(1, 2, figsize=(12, 5))
            # Heatmap для scores
            sns.heatmap(scores, annot=True, cmap="coolwarm", cbar=True, ax=axes[0])
            axes[0].set_title(f"{sample}: Scores ({sample_result['feature_1']} vs {sample_result['feature_2']})")
            axes[0].set_xlabel(sample_result['feature_2'])
            axes[0].set_ylabel(sample_result['feature_1'])

            # Heatmap для counts
            sns.heatmap(sample_result['counts'], annot=True, cmap="Blues", cbar=True, ax=axes[1])
            axes[1].set_title("Counts")
            axes[1].set_xlabel(sample_result['feature_2'])
            axes[1].set_ylabel(sample_result['feature_1'])

            plt.savefig(
                os.path.join(self.images_dir_path, f"{sample}_segment_performance_heatmap.png"),
                bbox_inches="tight",
                pad_inches=0.1,
            )
            plt.close()


            result_dict.update({sample: [0, "None"]})

        traffic_light_segment_performance = "None"
        result = pd.DataFrame(result_dict)
        return result, traffic_light_segment_performance