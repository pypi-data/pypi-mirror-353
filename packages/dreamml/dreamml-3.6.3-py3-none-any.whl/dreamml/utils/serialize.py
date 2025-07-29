import pickle
import sys
from pathlib import Path

import dreamml
from dreamml.logging import get_logger

_logger = get_logger(__name__)


def find_class(class_name):
    """
    Finds and returns the class corresponding to the given class name.

    This function ensures backward compatibility by maintaining conditions for previous class names.
    Imports are executed inside conditional blocks to avoid unnecessary imports and prevent cyclic dependencies.

    Args:
        class_name (str): The name of the class to find.

    Returns:
        type: The class corresponding to the provided class name.

    Raises:
        TypeError: If the class with the specified name cannot be found.
    """
    if class_name == "BaseModel":
        from dreamml.modeling.models.estimators import BaseModel

        cls = BaseModel

    elif class_name == "XGBoostModel":
        from dreamml.modeling.models.estimators import XGBoostModel

        cls = XGBoostModel

    elif class_name == "CatBoostModel":
        from dreamml.modeling.models.estimators import CatBoostModel

        cls = CatBoostModel

    elif class_name == "LightGBMModel":
        from dreamml.modeling.models.estimators import LightGBMModel

        cls = LightGBMModel

    elif class_name == "LinearRegModel":
        from dreamml.modeling.models.estimators import LinearRegModel

        cls = LinearRegModel

    elif class_name == "AMTSModel":
        from dreamml.modeling.models.estimators import AMTSModel

        cls = AMTSModel

    elif class_name == "BertModel":
        from dreamml.modeling.models.estimators import BertModel

        cls = BertModel

    elif class_name == "BERTopicModel":
        from dreamml.modeling.models.estimators import BERTopicModel

        cls = BERTopicModel

    elif class_name == "EnsembeldaModel":
        from dreamml.modeling.models.estimators import EnsembeldaModel

        cls = EnsembeldaModel

    elif class_name == "WBAutoML":
        from dreamml.modeling.models.estimators._lama_v_1_3 import WBAutoML

        cls = WBAutoML

    elif class_name == "LDAModel":
        from dreamml.modeling.models.estimators import LDAModel

        cls = LDAModel

    elif class_name == "LAMA":
        from dreamml.modeling.models.estimators import LAMA

        cls = LAMA

    elif class_name == "LogRegModel":
        from dreamml.modeling.models.estimators import LogRegModel

        cls = LogRegModel

    elif class_name == "LogRegModel":
        from dreamml.modeling.models.estimators import LogRegModel

        cls = LogRegModel

    elif class_name == "OneVsRestClassifierWrapper":
        from dreamml.modeling.models.estimators._multioutput_wrappers import (
            OneVsRestClassifierWrapper,
        )

        cls = OneVsRestClassifierWrapper

    elif class_name == "PyBoostModel":
        from dreamml.modeling.models.estimators import PyBoostModel

        cls = PyBoostModel

    elif class_name == "CategoricalFeaturesTransformer":
        from dreamml.features.categorical import CategoricalFeaturesTransformer

        cls = CategoricalFeaturesTransformer

    elif class_name == "LogTargetTransformer":
        from dreamml.features.feature_extraction import LogTargetTransformer

        cls = LogTargetTransformer

    elif class_name == "AugmentationWrapper":
        from dreamml.features.text.augmentation import AugmentationWrapper

        cls = AugmentationWrapper

    elif class_name == "BaseVectorization":
        from dreamml.features.feature_vectorization._base import BaseVectorization

        cls = BaseVectorization

    elif class_name == "TfidfVectorization":
        from dreamml.features.feature_vectorization import TfidfVectorization

        cls = TfidfVectorization

    elif class_name == "GloveVectorization":
        from dreamml.features.feature_vectorization import GloveVectorization

        cls = GloveVectorization

    elif class_name == "BowVectorization":
        from dreamml.features.feature_vectorization import BowVectorization

        cls = BowVectorization

    elif class_name == "FastTextVectorization":
        from dreamml.features.feature_vectorization import FastTextVectorization

        cls = FastTextVectorization

    elif class_name == "Word2VecVectorization":
        from dreamml.features.feature_vectorization import Word2VecVectorization

        cls = Word2VecVectorization

    elif class_name == "TextFeaturesTransformer":
        from dreamml.features.text import TextFeaturesTransformer

        cls = TextFeaturesTransformer

    elif class_name == "DmlLabelEncoder":
        from dreamml.features.categorical._label_encoder import DmlLabelEncoder

        cls = DmlLabelEncoder

    else:
        raise TypeError(f"Couldn't find class with {class_name=}")

    return cls


def instantiate_serialized_object(data, deprecation_warning=True):
    """
    Instantiates a serialized object from the provided data.

    This function deserializes the data using the SerializedObject class and optionally logs a deprecation warning.

    Args:
        data (dict): The serialized data to deserialize.
        deprecation_warning (bool, optional): Whether to log a deprecation warning. Defaults to True.

    Returns:
        Serializable: The deserialized object.

    Raises:
        Any exceptions raised by the deserialization process.
    """
    instance = SerializedObject(data).deserialize()

    if deprecation_warning:
        _logger.warning(
            f"Loading dreamml_base models with `pickle.load` is deprecated. "
            f"Please use `AutoModel.from_pretrained(path)` for model loading "
            f"or directly use `{type(instance).__name__}.from_pretrained(path)`."
        )

    return instance


def no_warning_instantiate_serialized_object(data):
    """
    Instantiates a serialized object from the provided data without logging a deprecation warning.

    Args:
        data (dict): The serialized data to deserialize.

    Returns:
        Serializable: The deserialized object.
    """
    return instantiate_serialized_object(data, deprecation_warning=False)


class NoDeprecationWarningUnpickler(pickle.Unpickler):
    """
    A custom Unpickler that suppresses deprecation warnings when deserializing objects.

    This class overrides the default `find_class` method to use the `no_warning_instantiate_serialized_object`
    function instead of `instantiate_serialized_object`, thereby avoiding deprecation warnings.

    Attributes:
        _filename (str or None): The name of the file being unpickled, if available.
    """

    def __init__(self, file, *args, **kwargs):
        """
        Initializes the NoDeprecationWarningUnpickler.

        Args:
            file (file-like object): The file from which to unpickle the object.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        self._filename = getattr(file, "name", None)

        if self._filename is not None:
            self._filename = Path(self._filename).name

        super().__init__(file, *args, **kwargs)

    def find_class(self, module, name):
        """
        Finds and returns the class or function specified by module and name.

        Overrides the default `find_class` method to replace 'instantiate_serialized_object'
        with 'no_warning_instantiate_serialized_object' to suppress warnings.

        Args:
            module (str): The module name where the class or function is located.
            name (str): The name of the class or function to find.

        Returns:
            type or function: The class or function corresponding to the provided module and name.

        Raises:
            Any exceptions raised by the superclass's find_class method.
        """
        if (
            module == "dreamml.utils.serialize"
            and name == "instantiate_serialized_object"
        ):
            return no_warning_instantiate_serialized_object
        else:
            cls = super().find_class(module, name)

        if module.startswith("dreamml"):
            # При unpickling'е у объекта не должно быть сохраненных атрибутов из dreamml
            if not isinstance(cls, type) or not issubclass(cls, Serializable):
                _logger.warning(
                    f"While loading '{self._filename}' encountered '{name}' (from {module}) "
                    f"which is not serializable, there could be backward compatibility issues."
                )

        return cls


class SerializedObjectLoader:
    """
    A loader for serialized objects that integrates with Python's pickle mechanism.

    This class implements the `__reduce__` method to facilitate custom deserialization logic.

    Attributes:
        data (dict): The serialized data to load.
    """

    def __init__(self, data):
        """
        Initializes the SerializedObjectLoader with the provided data.

        Args:
            data (dict): The serialized data to load.
        """
        self.data = data

    def __reduce__(self):
        """
        Defines the reduction strategy for pickling.

        Returns:
            tuple: A tuple containing the callable and its arguments for object reconstruction.
        """
        return instantiate_serialized_object, (self.data,)


class SerializedObject:
    """
    Represents a serialized object and provides methods for deserialization.

    Attributes:
        data (dict): The serialized data of the object.
    """

    def __init__(self, data):
        """
        Initializes the SerializedObject with the given data.

        Args:
            data (dict): The serialized data of the object.
        """
        self.data = data

    def deserialize(self):
        """
        Deserializes the stored data into an instance of the original class.

        This method retrieves the class name from the metadata and uses the `find_class`
        function to obtain the corresponding class. It then calls the class's `deserialize` method.

        Returns:
            Serializable: The deserialized instance of the original class.

        Raises:
            KeyError: If the class name is not found in the metadata.
            Any exceptions raised by the class's `deserialize` method.
        """
        class_name = self.data["_metadata"]["class_name"]
        cls: Serializable = find_class(class_name)

        return cls.deserialize(self.data)


class Serializable:
    """
    An abstract base class that provides serialization and deserialization capabilities.

    Subclasses should implement the `_serialize` and `_deserialize` methods to define
    how objects are serialized and deserialized.

    Methods:
        save_pretrained(path): Saves the serialized object to the specified path.
        from_pretrained(path): Loads a serialized object from the specified path.
        serialize(): Serializes the object.
        deserialize(data): Deserializes the object from data.
    """

    def save_pretrained(self, path):
        """
        Saves the serialized representation of the object to the specified path.

        This method serializes the object and writes it to a file using pickle.

        Args:
            path (str): The file path where the serialized object will be saved.

        Raises:
            IOError: If the file cannot be written.
            Any exceptions raised by the serialization process.
        """
        loader = SerializedObjectLoader(self.serialize())

        with open(path, "wb") as f:
            pickle.dump(loader, f)

    @classmethod
    def from_pretrained(cls, path):
        """
        Loads a serialized object from the specified path.

        This method reads the serialized data from a file and deserializes it into an object.

        Args:
            path (str): The file path from which to load the serialized object.

        Returns:
            Serializable: The deserialized object.

        Raises:
            TypeError: If the loaded data cannot be deserialized into the specified class.
            IOError: If the file cannot be read.
            Any exceptions raised by the unpickling or deserialization process.
        """
        with open(path, "rb") as f:
            loaded = NoDeprecationWarningUnpickler(f).load()

        if isinstance(loaded, cls):
            return loaded
        elif isinstance(loaded, dict):
            return SerializedObject(loaded).deserialize()
        else:
            raise TypeError(
                f"Can't deserialize loaded data of type `{type(loaded)}` as {cls} class."
            )

    def serialize(self):
        """
        Serializes the object into a dictionary.

        This method calls the `_serialize` method to obtain the serialized data.

        Returns:
            dict: The serialized representation of the object.

        Raises:
            Any exceptions raised by the `_serialize` method.
        """
        return self._serialize()

    @classmethod
    def deserialize(cls, data):
        """
        Deserializes the object from the provided data.

        This method calls the `_deserialize` method to reconstruct the object from the serialized data.

        Args:
            data (dict): The serialized data from which to deserialize the object.

        Returns:
            Serializable: The deserialized object.

        Raises:
            Any exceptions raised by the `_deserialize` method.
        """
        instance = cls._deserialize(data)

        return instance

    def _serialize(
        self,
        init_data=None,
        additional_data=None,
    ):
        """
        Internal method to serialize the object.

        Subclasses can override this method to customize serialization.

        Args:
            init_data (dict, optional): A dictionary of initialization parameters. Defaults to None.
            additional_data (dict, optional): A dictionary of additional attributes. Defaults to None.

        Returns:
            dict: A dictionary containing serialized data, including metadata.
        """
        if init_data is None:
            init_data = {}
        if additional_data is None:
            additional_data = {}

        metadata = {
            "dml_version": dreamml.__version__,
            "python_version": f"{sys.version_info[0]}.{sys.version_info[1]}.{sys.version_info[2]}",
            "class_name": self.__class__.__name__,
        }

        return {"init": init_data, "additional": additional_data, "_metadata": metadata}

    @classmethod
    def _deserialize(cls, data):
        """
        Internal method to deserialize the object from data.

        Subclasses can override this method to customize deserialization.

        Args:
            data (dict): The serialized data containing initialization parameters and metadata.

        Returns:
            Serializable: The deserialized object instance.

        Raises:
            Any exceptions raised by the class constructor or during deserialization.
        """
        init_data = data["init"]

        return cls(**init_data)