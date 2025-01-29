import json
import re
from datetime import date, datetime
from enum import StrEnum
from typing import Any, ClassVar, Optional

import arrow
from dateutil import parser as date_parser
from pydantic import (
    BaseModel,
    Field,
    PrivateAttr,
    field_serializer,
    field_validator,
    model_validator,
)

# Need to import this module to patch arrow.Arrow
import flexible_datetime.pydantic_arrow  # noqa: F401 # Need to import this module to patch arrow.Arrow  
from flexible_datetime.time_utils import infer_time_format


class OutputFormat(StrEnum):
    """
    Enum for the output formats of FlexDateTime.

    minimal_datetime: Serialize as shortest possible datetime format.
        Examples:
            YYYY, YYYY-MM, YYYY-MM-DD, YYYY-MM-DD HH, YYYY-MM-DD HH:mm, YYYY-MM-DD HH:mm:ss

    datetime: Serialize as full datetime format.
        Example: YYYY-MM-DD HH:mm:ss

    flex: Serialize as a dict format with the datetime and mask.
        Example: {"dt": "2023-06-29T12:30:45+00:00", "mask": "0011111"}

    components: Serialize as a dict format with masked components.
        Example: {"year": 2023, "month": 6, "day": 29, "hour": 12, "minute": 30, "second": 45, "millisecond": 0}
    """

    minimal_datetime = "minimal_datetime"
    datetime = "datetime"
    flex = "flex"
    components = "components"


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

    _dt_formats: ClassVar[dict[str, str]] = {
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
    _mask_fields: ClassVar[dict[str, None]] = {
        "year": None,
        "month": None,
        "day": None,
        "hour": None,
        "minute": None,
        "second": None,
        "millisecond": None,
    }
    _default_output_format: ClassVar[OutputFormat] = OutputFormat.minimal_datetime
    _output_format: OutputFormat = PrivateAttr(default=_default_output_format)

    def __init__(self, *args, **kwargs):
        if args and args[0] is None:
            raise ValueError("Cannot parse None as a FlexDateTime.")
        if not args and not kwargs:
            super().__init__(dt=arrow.utcnow())
        if args and isinstance(args[0], dict):
            ## handle dict input
            d = args[0]
            is_dict_format = any(k in d for k in self._mask_fields)
            if "dt" not in kwargs and is_dict_format:
                ## {"year": 2023, "month": 6, "day": 29}
                dt, mask = self._components_from_dict(d)
                super().__init__(dt=dt, mask=mask)
            else:
                ## {"dt": "2023-06-29T12:30:45+00:00", "mask": "0011111"}
                super().__init__(*args, **kwargs)
        elif args and isinstance(args[0], str):
            ## handle string input,"2023", "2023-06-29T12:30:45+00:00"
            dt, mask = self._components_from_str(args[0])
            super().__init__(dt=dt, mask=mask)
        elif args and isinstance(args[0], arrow.Arrow):
            ## handle arrow.Arrow input
            super().__init__(dt=args[0])
        elif args and isinstance(args[0], FlexDateTime):
            ## handle FlexDateTime input
            super().__init__(dt=args[0].dt, mask=args[0].mask)
        elif args and isinstance(args[0], date):
            ## handle datetime input
            super().__init__(
                dt=arrow.get(args[0]),
                mask=self.binary_to_mask("0001111"),
            )
        elif args and isinstance(args[0], datetime):
            ## handle datetime input
            super().__init__(dt=arrow.get(args[0]))
        else:
            ## handle other input
            super().__init__(*args, **kwargs)

    @model_validator(mode="before")
    def custom_validate_before(cls, values):
        if not values:
            return values
        elif isinstance(values, datetime):
            return {"dt": arrow.get(values)}
        elif isinstance(values, arrow.Arrow):
            return {"dt": values}
        elif isinstance(values, str):
            return {"dt": arrow.get(values)}
        elif isinstance(values, FlexDateTime):
            return {"dt": values.dt, "mask": values.mask}

        return values

    def model_dump(self, *args, **kwargs) -> dict[str, Any]:
        if self._default_output_format == OutputFormat.datetime:
            return {"dt": str(self.dt)}
        return super().model_dump(*args, **kwargs)

    def model_dump_json(self, *args, **kwargs):
        if self._default_output_format == OutputFormat.datetime:
            return json.dumps({"dt": str(self.dt)})
        return super().model_dump_json(*args, **kwargs)

    @staticmethod
    def infer_format(date_str: str) -> str:
        return infer_time_format(date_str)

    @classmethod
    def mask_to_binary(cls, mask: dict) -> str:
        return "".join(["1" if mask[field] else "0" for field in cls._mask_fields])

    @classmethod
    def binary_to_mask(cls, binary_str: str) -> dict:
        return {field: bool(int(bit)) for field, bit in zip(cls._mask_fields, binary_str)}

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
        dt, mask = cls._components_from_str(date_str, input_fmt)
        return cls(dt=dt, mask=mask)

    @classmethod
    def from_datetime(cls, dt: datetime) -> "FlexDateTime":
        """
        Creates a FlexDateTime instance from a datetime.
        """
        return cls(dt=dt)

    @classmethod
    def _parse_date_or_datetime(cls, s):
        # If it has "time-like" indicators, we assume user meant a time
        # This set can be as minimal or extensive as you want.
        # e.g. we also match "at 5", "at5", etc. if that is your usage.
        time_pattern = re.compile(r"(\d:\d|am|pm|midnight|noon|\bat\s*\d)", re.IGNORECASE)
        has_time = bool(time_pattern.search(s))

        dt = date_parser.parse(s, fuzzy=True)

        # If dateutil defaults year=1900, maybe fix that:
        if dt.year == 1900:
            dt = dt.replace(year=datetime.now().year)

        return dt if has_time else dt.date()

    @classmethod
    def _components_from_str(cls, date_str: str, input_fmt: Optional[str] = None):
        """
        Creates the components of a FlexDateTime instance from a string.
        """

        try:
            dt = arrow.get(date_str, input_fmt) if input_fmt else arrow.get(date_str)
        except (arrow.parser.ParserError, ValueError):
            try:
                date_time = cls._parse_date_or_datetime(date_str)
                if isinstance(date_time, datetime):
                    ft = cls(date_time)
                    return ft.dt, ft.mask
                else:
                    ft = cls(date_time)
                    return ft.dt, cls.binary_to_mask("0001111")
            except ValueError:
                raise ValueError(f"Invalid date string: {date_str}")
        mask = {field: False for field in cls._mask_fields}

        input_fmt = input_fmt or cls.infer_format(date_str)

        # Determine which parts were provided by checking the input format
        provided_parts = set()
        for fmt in cls._dt_formats:
            if fmt in input_fmt:
                provided_parts.add(cls._dt_formats[fmt])

        for part in cls._mask_fields:
            mask[part] = part not in provided_parts

        return dt, mask

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
        mask = {k: True for k in cls._mask_fields}

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
        nargs = args[0] if args and isinstance(args[0], list) else args
        new_mask = {k: True for k in nargs}
        new_mask.update(kwargs)
        for k in self.mask:
            if k not in new_mask:
                self.mask[k] = True
        # for a in args:
        #     self.mask[a.lower()] = True

    def toggle_mask(self, **kwargs) -> None:
        """
        Toggles the mask for the provided keyword arguments.
        """
        for key in kwargs:
            self.mask[key] = not self.mask[key]

    def to_minimal_datetime(self, output_fmt: Optional[str] = None) -> str:
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
        for fmt, part in FlexDateTime._dt_formats.items():
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

    def to_str(self, output_fmt: Optional[str] = None) -> str:
        return self.to_minimal_datetime(output_fmt)

    def to_components(self, output_fmt: Optional[str] = None) -> dict[str, int]:
        component_json = {
            "year": self.dt.year,
            "month": self.dt.month,
            "day": self.dt.day,
            "hour": self.dt.hour,
            "minute": self.dt.minute,
            "second": self.dt.second,
            "millisecond": self.dt.microsecond // 1000,
        }
        return {k: v for k, v in component_json.items() if not self.mask.get(k, False)}

    def to_flex(self) -> dict[str, str]:
        mask = self.mask_to_binary(self.mask)
        return {"dt": str(self.dt), "mask": mask}

    def to_datetime(self) -> datetime:
        return self.dt.datetime

    def __str__(self) -> str:
        """
        Returns the string representation of the datetime, considering the mask.
        """
        if self._output_format == OutputFormat.datetime:
            return str(self.dt)
        elif self._output_format == OutputFormat.minimal_datetime:
            return self.to_minimal_datetime()
        elif self._output_format == OutputFormat.components:
            return str(self.to_components())
        return str(self.to_flex())

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
