import re
from typing import ClassVar, Optional

import arrow
from pydantic import (
    BaseModel,
    Field,
    field_serializer,
    field_validator,
    model_validator,
)

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
    mask_fields: ClassVar[dict[str, int]] = {
        "year": 1,
        "month": 1,
        "day": 1,
        "hour": 1,
        "minute": 1,
        "second": 1,
        "millisecond": 1,
    }

    def __init__(self, **data):
        is_dict_format = any(k in data for k in self.mask_fields)
        if "dt" not in data and is_dict_format:
            dt, mask = self._components_from_dict(data)
            super().__init__(dt=dt, mask=mask)
        else:
            super().__init__(**data)

    @model_validator(mode="before")
    def custom_validate_before(cls, values):
        if not values:
            return values
        return values

    @staticmethod
    def infer_format(date_str: str) -> str:
        return infer_time_format(date_str)

    @classmethod
    def mask_to_binary(cls, mask: dict) -> str:
        return "".join(["1" if mask[field] else "0" for field in cls.mask_fields])

    @classmethod
    def binary_to_mask(cls, binary_str: str) -> dict:
        return {field: bool(int(bit)) for field, bit in zip(cls.mask_fields, binary_str)}

    @field_serializer("mask")
    def serialize_mask(self, mask: dict) -> str:
        return self.mask_to_binary(mask)

    @field_validator("mask", mode="before")
    def deserialize_mask(cls, value):
        if isinstance(value, str):
            return cls.binary_to_mask(value)
        return value

    @classmethod
    def from_str(cls, date_str: str, input_fmt: Optional[str] = None) -> "FlexDateTime":
        """
        Creates a FlexDateTime instance from a string.
        """
        instance = cls()  # Use construct to avoid validation

        try:
            instance.dt = arrow.get(date_str, input_fmt) if input_fmt else arrow.get(date_str)
        except (arrow.parser.ParserError, ValueError):
            raise ValueError(f"Invalid date string: {date_str}")
        instance.mask = {field: False for field in cls.mask_fields}

        input_fmt = input_fmt or cls.infer_format(date_str)

        # Determine which parts were provided by checking the input format
        provided_parts = set()
        for fmt in cls.dt_formats:
            if fmt in input_fmt:
                provided_parts.add(cls.dt_formats[fmt])

        for part in cls.mask_fields:
            instance.mask[part] = part not in provided_parts

        return instance

    @classmethod
    def _components_from_dict(cls, datetime_dict):
        # Provide default values for missing keys
        components = {
            "year": 1970,
            "month": 1,
            "day": 1,
            "hour": 0,
            "minute": 0,
            "second": 0,
            "microsecond": 0,
            "tzinfo": "UTC",
        }
        mask = {k: True for k in cls.mask_fields}

        # Convert milliseconds to microseconds if present
        if "millisecond" in datetime_dict:
            datetime_dict["microsecond"] = datetime_dict.pop("millisecond") * 1000

        # Update components with provided values
        components.update(datetime_dict)

        # Apply mask
        for k in datetime_dict:
            mask[k] = False

        ## handle microseconds
        if "microsecond" in datetime_dict:
            mask["millisecond"] = False

        dt = arrow.Arrow(**components)
        return dt, mask

    @classmethod
    def from_dict(cls, datetime_dict):
        dt, mask = cls._components_from_dict(datetime_dict)
        return cls(dt=dt, mask=mask)

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

    def use_only(self, *args, **kwargs) -> None:
        """
        Use only the specified elements (unmasks them).
        """
        self.clear_mask()
        self.mask.update(kwargs)
        for a in args:
            self.mask[a.lower()] = True

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

        # Handle each part
        for fmt, part in FlexDateTime.dt_formats.items():
            if part == "millisecond":
                # Format milliseconds/microseconds correctly
                microseconds = self.dt.microsecond
                if "SSSSSS" in output_str:
                    replacement = f"{microseconds:06d}"
                elif "SSSSS" in output_str:
                    replacement = f"{microseconds:06d}"[:5]
                elif "SSSS" in output_str:
                    replacement = f"{microseconds:06d}"[:4]
                elif "SSS" in output_str:
                    replacement = f"{microseconds:06d}"[:3]
                elif "SS" in output_str:
                    replacement = f"{microseconds // 1000:03d}"[:2]
                elif "S" in output_str:
                    replacement = f"{microseconds // 1000:03d}"[:1]
                else:
                    replacement = ""
                if self.mask[part]:
                    replacement = ""
                output_str = re.sub(r"S{1,6}", replacement, output_str)
            else:
                value = getattr(self.dt, part)
                replacement = (
                    f"{value:02d}" if fmt in ["MM", "DD", "HH", "mm", "ss"] else str(value)
                )
                replacement = replacement if not self.mask[part] else ""
                output_str = output_str.replace(fmt, replacement)

        # Remove unnecessary separators while preserving date and time structure
        output_str = re.sub(r"(?<=\d)(\s|-|:)(?=\d)", r"\1", output_str)
        output_str = re.sub(r"\s+", " ", output_str).strip()
        output_str = re.sub(r"-+", "-", output_str)
        output_str = re.sub(r":+", ":", output_str)

        # Remove all non-digits at the beginning and end of string
        output_str = re.sub(r"^\D+|\D+$", "", output_str)

        return output_str

    def __str__(self) -> str:
        """
        Returns the string representation of the datetime, considering the mask.
        """

        output_fmt = "YYYY-MM-DD HH:mm:ss"
        return self.to_str(output_fmt)

    def __repr__(self) -> str:
        return self.model_dump_json()

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
