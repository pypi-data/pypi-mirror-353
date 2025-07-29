from enum import Enum


class FrequencyEnums(Enum):
    """Enumeration of frequency units.

    Attributes:
        SECONDS (str): Represents seconds.
        MINUTES (str): Represents minutes.
        HOURS (str): Represents hours.
        DAYS (str): Represents days.
        WEEKS (str): Represents weeks.
        MONTHS (str): Represents months.
        YEARS (str): Represents years.
    """

    SECONDS = "S"
    MINUTES = "T"
    HOURS = "H"
    DAYS = "D"
    WEEKS = "W"
    MONTHS = "M"
    YEARS = "Y"