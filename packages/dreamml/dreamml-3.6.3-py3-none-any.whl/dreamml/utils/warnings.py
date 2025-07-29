import warnings
import logging

# Preserve the original warnings format to maintain consistency across libraries
# shap versions >0.44.1 should resolve related formatting issues
from tqdm import TqdmExperimentalWarning

default_formatwarning = warnings.formatwarning

warnings.filterwarnings(
    "ignore",
    message="etna.*is not available.*",
)
warnings.filterwarnings(
    "ignore",
    message="wandb.*is not available.*",
)
warnings.filterwarnings(
    "ignore",
    message=".*package isn't installed.*",
)
warnings.filterwarnings(
    "ignore",
    message=".*package isn't installed.*",
)
warnings.filterwarnings(
    "ignore",
    message=".*tqdm.autonotebook.tqdm.*",
)
warnings.filterwarnings(
    "ignore",
    message='"is" with a literal.*',
)
warnings.filterwarnings(
    "ignore",
    message="No Nvidia GPU detected!.*",
)
warnings.filterwarnings(
    "ignore",
    message="LightGBM binary classifier with TreeExplainer shap values output.*",
)
warnings.filterwarnings(
    "ignore",
    message="The frame.append method is deprecated and will be removed.*",
)
warnings.filterwarnings(
    "ignore",
    message="Attempting to set identical low and high xlims makes.*",
)

import shap  # Pre-import shap to fix formatting issues

warnings.formatwarning = default_formatwarning

import lightgbm
import lightautoml.utils.installation

logging.getLogger("lightautoml.utils.installation").setLevel(logging.ERROR)

# Overwrite to prevent dummy console outputs
lightgbm.basic._DummyLogger.info = lambda self, msg: None
lightgbm.basic._DummyLogger.warning = lambda self, msg: None


class DMLWarning(Warning):
    """
    Base class for all warnings related to dreamml_base functionality.

    This warning serves as the foundational class for issuing warnings specific to the dreamml_base library.
    It allows users to differentiate between general warnings and those that are specific to dreamml_base operations.
    """
    pass