from typing import Optional
from colorama import Style


class ANSIColoringMixin:
    """Mixin class that provides ANSI color functionality for strings.

    Attributes:
        use_colors (bool): Flag indicating whether to apply ANSI colors.
    """

    use_colors: bool

    def _add_ansi_color(self, s: str, color: Optional[str] = None):
        """Adds ANSI color codes to a given string if color usage is enabled.

        Args:
            s (str): The string to which ANSI color codes will be added.
            color (Optional[str], optional): The ANSI color code to apply. Defaults to None.

        Returns:
            str: The colored string if `use_colors` is True and `color` is provided;
                 otherwise, returns the original string.
        """
        if self.use_colors and color is not None:
            return f"{color}{s}{Style.RESET_ALL}"
        else:
            return s