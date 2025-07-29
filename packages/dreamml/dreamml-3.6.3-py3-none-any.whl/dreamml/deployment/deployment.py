import os

import bentoml
from omegaconf import DictConfig

from dreamml.configs.config_storage import ConfigStorage
from dreamml.modeling import AutoModel
from dreamml.utils.get_last_experiment_directory import get_experiment_dir_path


SERVICE_FILE_TEMPLATE = """import numpy as np
import pandas as pd
import bentoml

@bentoml.service(
    resources={resources},
    traffic={traffic},
)
class DreammlModel:
    # Retrieve the latest version of the model from the BentoML Model Store
    bento_model = bentoml.models.get("{image}:{image_version}")

    def __init__(self):
        self.model = bentoml.picklable_model.load_model(self.bento_model)

    @bentoml.api
    def predict(self, data: dict) -> np.ndarray:
        data = pd.DataFrame(data)

        return self.model.transform(data)
"""

BENTOFILE_CONTENT = """service: "service:DreammlModel"
labels:
  owner: dreamml-team
  stage: demo
include:
  - "*.py"
python:
  packages:
    - dreamml"""


class Deployment:
    def __init__(self, config: dict):
        self.config = config

        self.experiment_dir_path = get_experiment_dir_path(
            config["results_path"],
            experiment_dir_name=config["dir_name"],
            use_last_experiment_directory=config.get(
                "use_last_experiment_directory", False
            ),
        )
        self.experiment_config = ConfigStorage.from_pretrained(f"{self.experiment_dir_path}/config")

        self.deploy_dir = os.path.join(self.experiment_dir_path, "deploy")
        self.model_name = self.config["model_name"]

        self.model_name = (
            self.model_name[:-4]
            if self.model_name.endswith(".pkl")
            else self.model_name
        )

        self.model_deploy_dir = os.path.join(self.deploy_dir, self.model_name)

        self.image_name = self.config["image_name"]
        self.image_version = "latest"

    def serve(self):
        print(
            f"To deploy model with bentoml run command `bentoml serve` in '{self.model_deploy_dir}' directory."
        )

    def prepare_artifacts(self):
        os.makedirs(self.deploy_dir, exist_ok=True)

        os.makedirs(self.model_deploy_dir, exist_ok=True)

        model = self._get_model()

        # Specify the model name and the model to be saved
        bentoml.picklable_model.save_model(self.image_name, model)

        self._create_service_file()
        self._create_bentofile_yaml()

    def _create_service_file(self):

        path = os.path.join(self.model_deploy_dir, "service.py")

        bento_config = self._get_bento_cofnig()

        service_file_content = SERVICE_FILE_TEMPLATE.format(
            resources=bento_config["resources"],
            traffic=bento_config["traffic"],
            image=self.image_name,
            image_version=self.image_version,
        )

        with open(path, "w") as f:
            f.write(service_file_content)

    def _create_bentofile_yaml(self):
        path = os.path.join(self.model_deploy_dir, "bentofile.yaml")

        with open(path, "w") as f:
            f.write(BENTOFILE_CONTENT)

    def _get_model(self):
        """
        Loads the model from the experiment directory.

        Returns:
            BaseModel: The loaded model.

        Raises:
            None
        """
        path = os.path.join(
            self.experiment_dir_path, "models", f"{self.model_name}.pkl"
        )
        model = AutoModel.from_pretrained(path)

        return model

    def _get_bento_cofnig(self):
        # Извлекаем настройки ресурсов из конфига
        resources = self._parse_bento_resources(self.experiment_config.pipeline.bentoml_service.resources)

        # Настройки трафика остаются без изменений
        traffic = {"timeout": int(self.experiment_config.pipeline.bentoml_service.traffic.timeout)}

        return {"resources": resources, "traffic": traffic}

    def _parse_bento_resources(self, resources_config: DictConfig):
        # Если заданы параметры для GPU (gpu или gpu_type не равны None),
        # то используем их, иначе используем CPU
        cpu = resources_config.get("cpu")
        gpu = resources_config.get("gpu")
        gpu_type = resources_config.get("gpu_type")

        if gpu is not None or gpu_type is not None:
            resources = {}
            if gpu is not None:
                resources["gpu"] = int(gpu)

            if gpu_type is not None:
                resources["gpu_type"] = gpu_type

            return resources
        else:
            resources = {"cpu": int(cpu)}

        return resources

