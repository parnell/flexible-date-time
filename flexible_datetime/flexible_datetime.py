import re
from enum import Enum
from typing import ClassVar, Optional

import arrow
from dateutil.parser import parse
from dateutil.parser._parser import ParserError
from pydantic import BaseModel, Field

import flexible_datetime.pydantic_arrow  # Need to import this module to patch arrow.Arrow
from flexible_datetime.time_utils import infer_time_format


class FlexDateTime(BaseModel):
    dt: arrow.Arrow = Field(default_factory=arrow.utcnow)
    mask: dict = Field(
        default_factory=lambda: {
            "year": False,
            "month": False,
            "day": False,
            "hour": False,
            "minute": False,
            "second": False,
            "millisecond": False,
        }
    )

    dt_formats: ClassVar[dict[str, str]] = {
        "YYYY": "year",
        "MM": "month",
        "DD": "day",
        "HH": "hour",
        "mm": "minute",
        "ss": "second",
        "S": "millisecond",
        "SS": "millisecond",
        "SSS": "millisecond",
        "SSSS": "millisecond",
        "SSSSS": "millisecond",
        "SSSSSS": "millisecond",
    }

    @staticmethod
    def infer_format(date_str: str) -> str:
        return infer_time_format(date_str)

    @classmethod
    def from_dict(cls, date_dict: dict[str, int]) -> "FlexDateTime":
        """
        Creates a FlexDateTime instance from a dictionary.
        """
        instance = cls()
        # Extract date components from the dictionary
        year = date_dict.get("year", 1)
        month = date_dict.get("month", 1)
        day = date_dict.get("day", 1)
        hour = date_dict.get("hour", 0)
        minute = date_dict.get("minute", 0)
        second = date_dict.get("second", 0)
        millisecond = date_dict.get("millisecond", 0)

        # Create the Arrow datetime object
        try:
            instance.dt = arrow.get(year, month, day, hour, minute, second, millisecond)
        except (arrow.parser.ParserError, ValueError):
            raise ValueError(f"Invalid date dictionary: {date_dict}")
        ## make date_dict keys lowercase
        date_dict = {k.lower(): v for k, v in date_dict.items()}

        # Update the mask based on which parts were provided
        for part in ["year", "month", "day", "hour", "minute", "second"]:
            instance.mask[part] = part not in date_dict

        return instance

    @classmethod
    def from_str(cls, date_str: str, input_fmt: Optional[str] = None) -> "FlexDateTime":
        """
        Creates an FlexDateTime instance from a string.
        """
        instance = cls()

        try:
            instance.dt = arrow.get(date_str, input_fmt) if input_fmt else arrow.get(date_str)
        except (arrow.parser.ParserError, ValueError):
            raise ValueError(f"Invalid date string: {date_str}")

        input_fmt = input_fmt or cls.infer_format(date_str)

        # Determine which parts were provided by checking the input format
        for fmt, mask_field in cls.dt_formats.items():
            if fmt not in input_fmt:
                instance.mask[mask_field] = True

        return instance

    def apply_mask(self, **kwargs) -> None:
        """
        Updates the mask with the provided keyword arguments.
        """
        self.mask.update(kwargs)

    def clear_mask(self) -> None:
        """
        Clears the mask.
        """
        self.mask = {
            "year": False,
            "month": False,
            "day": False,
            "hour": False,
            "minute": False,
            "second": False,
            "millisecond": False,
        }

    def use_only(self, **kwargs) -> None:
        """
        Use only the specified elements (unmasks them).
        """
        self.clear_mask()
        self.mask.update(kwargs)

    def toggle_mask(self, **kwargs) -> None:
        """
        Toggles the mask for the provided keyword arguments.
        """
        for key in kwargs:
            self.mask[key] = not self.mask[key]

    def to_str(self, output_fmt: Optional[str] = None) -> str:
        """
        Returns the string representation of the datetime, considering the mask.
        Args:
            output_fmt: The format of the output string.
                Defaults to "YYYY-MM-DD HH:mm:ss", but masking will remove parts of the string.

        Returns:
            The string representation of the datetime.
        """
        if not self.dt:
            return "Invalid datetime"
        output_str = output_fmt or "YYYY-MM-DD HH:mm:ss"
        for fmt, part in FlexDateTime.dt_formats.items():
            replacement = (
                (
                    f"{getattr(self.dt, part):02d}"
                    if fmt in ["MM", "DD", "HH", "mm", "ss"]
                    else f"{getattr(self.dt, part)}"
                )
                if not self.mask[part]
                else ""
            )
            output_str = output_str.replace(fmt, replacement).strip()

        # Remove unnecessary separators
        output_str = " ".join(filter(None, output_str.split()))
        output_str = "-".join(filter(None, output_str.split("-")))
        output_str = ":".join(filter(None, output_str.split(":")))

        # Replace dangling whitespace and hyphens
        output_str = re.sub(r"[\s-]+$", "", output_str)
        return output_str

    def __str__(self) -> str:
        """
        Returns the string representation of the datetime, considering the mask.
        """

        output_fmt = "YYYY-MM-DD HH:mm:ss"
        return self.to_str(output_fmt)

    def get_comparable_dt(self) -> arrow.Arrow:
        """
        Creates a comparable datetime that respects the mask.
        """
        return arrow.get(
            self.dt.year if not self.mask["year"] else 1,
            self.dt.month if not self.mask["month"] else 1,
            self.dt.day if not self.mask["day"] else 1,
            self.dt.hour if not self.mask["hour"] else 0,
            self.dt.minute if not self.mask["minute"] else 0,
            self.dt.second if not self.mask["second"] else 0,
        )

    def _ensure_same_mask(self, other: "FlexDateTime") -> None:
        """
        Ensures that the mask of the current instance matches the mask of the other instance.
        """
        if self.mask != other.mask:
            raise ValueError(
                f"Cannot compare FlexDateTime instances with different masks. {self.mask} != {other.mask}"
            )

    def eq(self, other: "FlexDateTime", allow_different_masks: bool = False) -> bool:
        """
        Checks if the current instance is equal to the other instance.
        """
        if not isinstance(other, FlexDateTime):
            return False
        if not allow_different_masks:
            self._ensure_same_mask(other)
        return self.get_comparable_dt() == other.get_comparable_dt()

    def __eq__(self, other) -> bool:
        if not isinstance(other, FlexDateTime):
            return False
        self._ensure_same_mask(other)
        return self.get_comparable_dt() == other.get_comparable_dt()

    def __lt__(self, other) -> bool:
        if not isinstance(other, FlexDateTime):
            return NotImplemented
        self._ensure_same_mask(other)
        return self.get_comparable_dt() < other.get_comparable_dt()

    def __le__(self, other) -> bool:
        if not isinstance(other, FlexDateTime):
            return NotImplemented
        self._ensure_same_mask(other)
        return self.get_comparable_dt() <= other.get_comparable_dt()

    def __gt__(self, other) -> bool:
        if not isinstance(other, FlexDateTime):
            return NotImplemented
        self._ensure_same_mask(other)
        return self.get_comparable_dt() > other.get_comparable_dt()

    def __ge__(self, other) -> bool:
        if not isinstance(other, FlexDateTime):
            return NotImplemented
        self._ensure_same_mask(other)
        return self.get_comparable_dt() >= other.get_comparable_dt()
