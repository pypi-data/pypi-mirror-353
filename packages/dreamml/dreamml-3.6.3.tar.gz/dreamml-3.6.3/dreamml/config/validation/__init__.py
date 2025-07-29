from typing import List, Dict

from pydantic import model_validator

from dreamml.config._base_config import BaseConfig
from dreamml.modeling.metrics import metrics_mapping


class TrafficLightsConfig(BaseConfig):
    value_yellow: float
    value_green: float
    delta_yellow: List[float]
    delta_green: List[float]

    @model_validator(mode="after")
    def _check_deltas(self):
        if len(self.delta_yellow) != 2:
            raise ValueError("`delta_yellow` has to be a list of two values.")

        if len(self.delta_green) != 2:
            raise ValueError("`delta_green` has to be a list of two values.")

        return self


class ValidationConfig(BaseConfig):
    traffic_lights: Dict[str, TrafficLightsConfig]

    @model_validator(mode="after")
    def _check_traffic_lights(self):
        for metric_name in self.traffic_lights:
            if metric_name == "default":
                continue

            if metric_name not in metrics_mapping:
                raise ValueError(
                    f"{metric_name=} is not available for traffic lights. "
                    f"Available metrics: {list(metrics_mapping.keys())}"
                )

        return self
