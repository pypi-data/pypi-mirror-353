from dreamml.utils.serialize import Serializable


class AutoModel:
    """
    AutoModel provides functionalities to automatically handle model operations.

    Attributes:
        from_pretrained (Callable): Method to load a pretrained model from Serializable.
    """

    from_pretrained = Serializable.from_pretrained