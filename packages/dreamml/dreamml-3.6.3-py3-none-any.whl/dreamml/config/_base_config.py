from pydantic import BaseModel, Extra, ConfigDict


# FIXME: remove Extra.allow after the end of configs development
class BaseConfig(BaseModel, extra=Extra.allow):
    """Base configuration class.

    This class serves as a foundational configuration model, extending Pydantic's BaseModel.
    It allows for additional attributes beyond those explicitly defined.

    Attributes:
        model_config (ConfigDict): Configuration dictionary with protected namespaces.
    """

    model_config = ConfigDict(protected_namespaces=())

    def __getitem__(self, item):
        """Retrieve an attribute by name.

        Args:
            item (str): The name of the attribute to retrieve.

        Returns:
            Any: The value of the specified attribute.

        Raises:
            AttributeError: If the attribute does not exist.
        """
        # FIXME: remove all usages and then delete this method
        return getattr(self, item)

    def __setitem__(self, key, value):
        """Set an attribute by name.

        Args:
            key (str): The name of the attribute to set.
            value (Any): The value to assign to the attribute.

        Raises:
            AttributeError: If the attribute cannot be set.
        """
        # FIXME: remove all usages and then delete this method
        setattr(self, key, value)

    def get(self, name: str, default=None):
        """Get an attribute value with a default fallback.

        Args:
            name (str): The name of the attribute to retrieve.
            default (Any, optional): The default value to return if the attribute does not exist. Defaults to None.

        Returns:
            Any: The value of the attribute if it exists, otherwise the default value.
        """
        return getattr(self, name, default)

    def set(self, name: str, value):
        """Set an attribute value.

        Args:
            name (str): The name of the attribute to set.
            value (Any): The value to assign to the attribute.
        """
        setattr(self, name, value)