class TopicModelingData:
    """Stores and manages data relevant to topic modeling.

    Attributes:
        _base_model (Any): The base model used for topic modeling.
        _model_type (str): The type of the model.
        _docs (List[str]): The original documents.
        _tokenized_docs (List[List[str]]): The tokenized version of the documents.
        _dictionary (Any): The dictionary mapping of the tokens.
        _corpus (Any): The corpus in a format suitable for the model.
        _pred_topics (Any): The predicted topics from the model.
    """

    def __init__(self):
        """Initializes a new instance of TopicModelingData.

        Initializes all attributes to their default values.
        """
        self._base_model = None
        self._model_type = None
        self._docs = None
        self._tokenized_docs = None
        self._dictionary = None
        self._corpus = None
        self._pred_topics = None

    @property
    def base_model(self):
        """Gets the base model used for topic modeling.

        Returns:
            Any: The base model.
        """
        return self._base_model

    @base_model.setter
    def base_model(self, value):
        """Sets the base model used for topic modeling.

        Args:
            value (Any): The base model to set.
        """
        self._base_model = value

    @property
    def model_type(self):
        """Gets the type of the model.

        Returns:
            str: The type of the model.
        """
        return self._model_type

    @model_type.setter
    def model_type(self, value):
        """Sets the type of the model.

        Args:
            value (str): The model type to set.
        """
        self._model_type = value

    @property
    def tokenized_docs(self):
        """Gets the tokenized documents.

        Returns:
            List[List[str]]: The tokenized documents.
        """
        return self._tokenized_docs

    @tokenized_docs.setter
    def tokenized_docs(self, value):
        """Sets the tokenized documents.

        Args:
            value (List[List[str]]): The tokenized documents to set.
        """
        self._tokenized_docs = value

    @property
    def dictionary(self):
        """Gets the dictionary mapping of tokens.

        Returns:
            Any: The dictionary.
        """
        return self._dictionary

    @dictionary.setter
    def dictionary(self, value):
        """Sets the dictionary mapping of tokens.

        Args:
            value (Any): The dictionary to set.
        """
        self._dictionary = value

    @property
    def corpus(self):
        """Gets the corpus suitable for the model.

        Returns:
            Any: The corpus.
        """
        return self._corpus

    @corpus.setter
    def corpus(self, value):
        """Sets the corpus suitable for the model.

        Args:
            value (Any): The corpus to set.
        """
        self._corpus = value

    @property
    def pred_topics(self):
        """Gets the predicted topics from the model.

        Returns:
            Any: The predicted topics.
        """
        return self._pred_topics

    @pred_topics.setter
    def pred_topics(self, value):
        """Sets the predicted topics from the model.

        Args:
            value (Any): The predicted topics to set.
        """
        self._pred_topics = value

    @property
    def docs(self):
        """Gets the original documents.

        Returns:
            List[str]: The original documents.
        """
        return self._docs

    @docs.setter
    def docs(self, value):
        """Sets the original documents.

        Args:
            value (List[str]): The documents to set.
        """
        self._docs = value