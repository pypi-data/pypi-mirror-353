"""
Formable
Copyright (c) 2025 Juan-Pablo Scaletti
"""

import datetime
import typing as t

from .. import errors as err
from .base import Field


class DateField(Field):
    def __init__(
        self,
        format="%Y-%m-%d",
        *,
        required: bool = True,
        default: datetime.date | str | None = None,
        after_date: datetime.date | str | None = None,
        before_date: datetime.date | str | None = None,
        past_date: bool = False,
        future_date: bool = False,
        offset: int | float = 0,
        _utcnow: datetime.datetime | None = None,
    ):
        """
        A field that represents a date.

        Arguments:

        - format: The format of the date string. Defaults to '%Y-%m-%d'.
        - required: Whether the field is required. Defaults to `True`.
        - default: Default value for the field. Defaults to `None`.
        - after_date: A date that the field value must be after. Defaults to `None`.
        - before_date: A date that the field value must be before. Defaults to `None`.\
        - past_date: Whether the date must be in the past. Defaults to `False`.
        - future_date: Whether the date must be in the future. Defaults to `False`.
        - offset:
            Timezone offset in hours (floats are allowed) for calculating "today" when
            `past_date` or `future_date` are used. Defaults to `0` (UTC timezone).

        """
        self.format = format

        if after_date and isinstance(after_date, str):
            after_date = self.to_python(after_date)
        self.after_date = t.cast(datetime.date | None, after_date)

        if before_date and isinstance(before_date, str):
            before_date = self.to_python(before_date)
        self.before_date = t.cast(datetime.date | None, before_date)

        self.past_date = past_date
        self.future_date = future_date
        self.offset = offset

        # For easier testing
        self._utcnow = _utcnow

        if default is not None and isinstance(default, str):
            default = self.to_python(default)
        super().__init__(required=required, default=default)

    def to_python(self, value: str | datetime.date | None) -> datetime.date | None:
        """
        Convert the value to a Python date.
        The date is expected to be in the format `DateField.format`.
        """
        if value is None:
            return None
        if isinstance(value, datetime.date):
            return value
        return datetime.datetime.strptime(value, self.format).date()

    def validate(self):
        """
        Validate the field value against the defined constraints.
        """
        super().validate()
        if self.error:
            return False

        if self.after_date and self.value <= self.after_date:
            self.error = err.AFTER_DATE
            self.error_args = {"after_date": self.after_date}
            return False
        if self.before_date and self.value >= self.before_date:
            self.error = err.BEFORE_DATE
            self.error_args = {"before_date": self.before_date}
            return False

        now = self._utcnow or datetime.datetime.now(datetime.timezone.utc)
        if self.offset:
            now += datetime.timedelta(hours=self.offset)
        today = now.date()

        if self.past_date and self.value >= today:
            self.error = err.PAST_DATE
            return False
        if self.future_date and self.value <= today:
            self.error = err.FUTURE_DATE
            return False

        return True


class DateTimeField(Field):
    def __init__(
        self,
        format="%Y-%m-%dT%H:%M:%S",
        *,
        required: bool = True,
        default: datetime.datetime | str | None = None,
        after_date: datetime.datetime | str | None = None,
        before_date: datetime.datetime | str | None = None,
        past_date: bool = False,
        future_date: bool = False,
        offset: int | float = 0,
        _utcnow: datetime.datetime | None = None,
    ):
        """
        A field that represents a datetime.

        Arguments:

        - format: The format of the date string. Defaults to '%Y-%m-%d'.
        - required: Whether the field is required. Defaults to `True`.
        - default: Default value for the field. Defaults to `None`.
        - after_date: A date that the field value must be after. Defaults to `None`.
        - before_date: A date that the field value must be before. Defaults to `None`.\
        - past_date: Whether the date must be in the past. Defaults to `False`.
        - future_date: Whether the date must be in the future. Defaults to `False`.
        - offset:
            Timezone offset in hours (floats are allowed) for calculating "now" when
            `past_date` or `future_date` are used. Defaults to `0` (UTC timezone).

        """
        self.format = format

        if after_date and isinstance(after_date, str):
            after_date = self.to_python(after_date)
        self.after_date = t.cast(datetime.date | None, after_date)

        if before_date and isinstance(before_date, str):
            before_date = self.to_python(before_date)
        self.before_date = t.cast(datetime.date | None, before_date)

        self.past_date = past_date
        self.future_date = future_date
        self.offset = offset

        # For easier testing
        self._utcnow = _utcnow

        if default is not None and isinstance(default, str):
            default = self.to_python(default)
        super().__init__(required=required, default=default)

    def to_python(self, value: str | datetime.datetime | None) -> datetime.datetime | None:
        """
        Convert the value to a Python datetime.
        The datetime is expected to be in the format `DateField.format`.
        """
        if value is None:
            return None
        if isinstance(value, datetime.datetime):
            return value
        return datetime.datetime.strptime(value, self.format)

    def validate(self):
        """
        Validate the field value against the defined constraints.
        """
        super().validate()
        if self.error:
            return False
        if self.after_date and self.value <= self.after_date:
            self.error = err.AFTER_DATE
            self.error_args = {"after_date": self.after_date}
            return False
        if self.before_date and self.value >= self.before_date:
            self.error = err.BEFORE_DATE
            self.error_args = {"before_date": self.before_date}
            return False

        now = self._utcnow or datetime.datetime.now(datetime.timezone.utc)
        if self.offset:
            now += datetime.timedelta(hours=self.offset)

        if self.past_date and self.value >= now:
            self.error = err.PAST_DATE
            return False
        if self.future_date and self.value <= now:
            self.error = err.FUTURE_DATE
            return False

        return True
