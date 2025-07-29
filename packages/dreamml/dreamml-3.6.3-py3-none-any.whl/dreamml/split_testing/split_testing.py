import pandas as pd
from typing import Dict

from ambrosia.designer import Designer
from ambrosia.splitter import Splitter
from ambrosia.tester import Tester

from dreamml.logging import get_logger

_logger = get_logger(__name__)


class SplitTesting:
    def __init__(self, config: Dict) -> None:
        self.config = config

        self.data = self.load_data()
        self.designer = None
        self.splitter = None

    def load_data(self) -> pd.DataFrame:
        file_path = self.config["file_path"]

        if file_path is None:
            raise ValueError(f"Incorrect path to {file_path} data.")
        elif file_path.rsplit(".", 1)[-1] == "csv":
            data = pd.read_csv(file_path, sep=";")
        elif file_path.rsplit(".", 1)[-1] in {"pkl", "pickle"}:
            data = pd.read_pickle(file_path)
        elif file_path.rsplit(".", 1)[-1] == "parquet":
            data = pd.read_parquet(file_path)
        elif file_path.rsplit(".", 1)[-1] == "xlsx":
            data = pd.read_excel(file_path)
        else:
            raise FileNotFoundError(
                f"dreamml_base supports only formats: .csv, .pkl, .pickle, .parquet \n"
            )

        _logger.info("Data uploaded successfully")
        return data

    def init_designer(self):
        self.designer = Designer(
            dataframe=self.data, metrics=self.config["designer"]["metrics"]
        )

    def init_splitter(self):
        self.splitter = Splitter(
            dataframe=self.data, id_column=self.config["splitter"]["id_column"]
        )

    def init_tester(self):
        self.tester = Tester(
            dataframe=self.data,
            column_groups=self.config["tester"]["column_groups"],
            metrics=self.config["tester"]["metrics"],
            first_type_errors=self.config["tester"]["first_type_errors"],
        )

    def run_tester(
        self,
        effect_type: str,
        method: str = None,
        criterion: str = None,
        alternative: str = "two-sided",
    ) -> pd.DataFrame:

        output = self.tester.run(
            effect_type=effect_type,
            method=method,
            criterion=criterion,
            metrics=self.config["tester"]["metrics"],
            alternative=alternative,
            first_type_errors=self.config["tester"]["first_type_errors"],
        )
        return output

    def run_splitter(self, method: str, groups_number: int = 2) -> pd.DataFrame:
        params = dict(
            method=method,
            groups_size=self.config["splitter"]["groups_size"],
        )

        if method == "hash":
            params["salt"] = self.config["splitter"]["salt"]
        elif method == "metric":
            params["fit_columns"] = self.config["splitter"]["fit_columns"]
            params["groups_number"] = groups_number

        output = self.splitter.run(**params)

        return output

    def run_designer(
        self,
        to_design: str,
        alternative: str = "two-sided",
        groups_ratio: float = 0.1,
    ) -> pd.DataFrame:
        params = dict(
            to_design=to_design,
            method=self.config["designer"]["method"],
            first_type_errors=self.config["designer"]["first_type_errors"],
            second_type_errors=self.config["designer"]["second_type_errors"],
            alternative=alternative,
            groups_ratio=groups_ratio,
        )

        if to_design == "size":
            params["effects"] = self.config["designer"]["effects"]
        elif to_design == "effect":
            params["sizes"] = self.config["designer"]["sizes"]
        elif to_design == "power":
            params["effects"] = self.config["designer"]["effects"]
            params["sizes"] = self.config["designer"]["sizes"]

        output = self.designer.run(**params)

        return output
