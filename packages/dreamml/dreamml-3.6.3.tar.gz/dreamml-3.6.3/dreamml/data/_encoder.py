import pandas as pd


class BaseEncoder:
    """Base stub encoder class.

    Used when the user does not provide a path to an encoder. In this case, the `transform` method performs an identity transformation.

    """

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """Transforms the input data.

        Args:
            data (pd.DataFrame): The data to be transformed.

        Returns:
            pd.DataFrame: The transformed data.
        """
        return data