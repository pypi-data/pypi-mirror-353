import json
import os
from pathlib import Path
from typing import Union

import pandas as pd
from pandas import Timestamp
from workalendar.europe import Russia

from dreamml.logging import get_logger

_logger = get_logger(__name__)


class RusProductionCalendar:
    """
    A calendar class for managing Russian production holidays and weekends.

    This class loads holiday data from a specified JSON file and provides methods
    to determine if a given date is a holiday, pre-holiday, or weekend based on the
    loaded calendar data or the default Russia calendar from the workalendar package.
    """

    def __init__(self, calendars_path: Union[Path, str]):
        """
        Initializes the RusProductionCalendar with the path to the calendars JSON file.

        Args:
            calendars_path (Union[Path, str]): The file path to the calendars JSON file.

        Raises:
            ValueError: If the provided calendars_path does not exist.
        """
        self.calendars_path = calendars_path

        if os.path.exists(self.calendars_path):
            with open(calendars_path, "r") as f:
                self.calendars = json.load(f)
        else:
            raise ValueError(f'Path "{self.calendars_path}" doesn`t exist.')

        self.worcalendar = Russia()
        self.years = []
        for year, _ in self.calendars.items():
            self.years.append(int(year))

    def _check_date_in_calendar(self, row: Timestamp):
        """
        Checks if the year of the given date is present in the loaded calendars.

        Args:
            row (Timestamp): The date to check.

        Returns:
            bool: True if the year is in the calendars, False otherwise.
        """
        if int(row.year) in self.years:
            return True
        return False

    def check_date_is_holiday(self, row: Timestamp):
        """
        Determines if the given date is a holiday.

        Args:
            row (Timestamp): The date to check.

        Returns:
            int: 1 if the date is a holiday, 0 otherwise.
        """
        if self._check_date_in_calendar(row):
            calendar_year_month = self.calendars[str(row.year)][str(row.month)]
            if int(row.day) in calendar_year_month["holidays"]:
                return 1
            return 0
        else:
            if self.worcalendar.is_holiday(row):
                return 1
            return 0

    def check_date_is_pre_holiday(self, row: Timestamp):
        """
        Determines if the given date is a pre-holiday.

        A pre-holiday is typically the day before a holiday.

        Args:
            row (Timestamp): The date to check.

        Returns:
            int: 1 if the date is a pre-holiday, 0 otherwise.
        """
        if self._check_date_in_calendar(row) is True:
            calendar_year_month = self.calendars[str(row.year)][str(row.month)]
            if int(row.day) in calendar_year_month["pre_holidays"]:
                return 1
            return 0
        else:
            if self.worcalendar.is_working_day(row) and self.worcalendar.is_holiday(
                row + pd.DateOffset(days=1)
            ):
                return 1
            return 0

    def check_date_is_weekend(self, row: Timestamp):
        """
        Determines if the given date falls on a weekend.

        Args:
            row (Timestamp): The date to check.

        Returns:
            int: 1 if the date is a weekend, 0 otherwise.
        """
        if self._check_date_in_calendar(row) is True:
            calendar_year_month = self.calendars[str(row.year)][str(row.month)]
            if int(row.day) in calendar_year_month["weekends"]:
                return 1
            return 0
        else:
            if row.day_of_week in [5, 6]:
                return 1
            return 0