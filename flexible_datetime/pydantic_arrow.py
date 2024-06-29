import os
from typing import Any

import arrow
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema


class PyArrow(arrow.Arrow):
    """
    A subclass of arrow.Arrow that provides Pydantic V2 serialization.
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        """
        Defines the Pydantic core schema for PyArrow.
        """
        def validate_by_arrow(value) -> arrow.Arrow:
            if isinstance(value, arrow.Arrow):
                return value
            try:
                return arrow.get(value)
            except Exception:
                raise ValueError(f"Arrow cannot parse {value}")

        def arrow_serialization(value: arrow.Arrow, _, info) -> str:
            return value.for_json()

        return core_schema.no_info_after_validator_function(
            function=validate_by_arrow,
            schema=core_schema.str_schema(),
            serialization=core_schema.wrap_serializer_function_ser_schema(
                arrow_serialization, info_arg=True
            ),
        )


if not os.environ.get("SKIP_ARROW_PATCH"):
    # Patch arrow.Arrow to allow Pydantic V2 serialization
    setattr(
        arrow.Arrow, "__get_pydantic_core_schema__", PyArrow.__get_pydantic_core_schema__
    )
