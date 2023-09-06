"""Reusable field definitions for use in validation schemas."""
from enum import Enum
from typing import Annotated, Any, Literal

from pydantic import Field


def get_const_str_field_type(const: str, error_msg_template: str) -> Any:
    """Return a constant-string field type with custom error messages.

    :param const: The constant string value.
    :param error_msg_template: The error message template. Must contain a {valid_value} and {value} placeholder.
    """
    return Annotated[
        # While this is not really a Literal, since we illegally use a variable, it works as "const" in json schema.
        Literal[const],
        Field(json_schema_extra={"errorMessage": error_msg_template.format(valid_value=const, value="${0}")}),
    ]


def get_enum_field_definitions(field_input: Enum, error_msg_template: str) -> Any:
    """Turn a StrEnum into field types of string-constants.

    :param field_input: The StrEnum to convert to fields.
    :param error_msg_template: The error message template. Must contain a {valid_value} and {value} placeholder.
    :return: A dictionary of field definitions.
    """
    return {
        member.name: (  # Tuple of (type definition, default value).
            get_const_str_field_type(member.value, error_msg_template),
            None,  # Default value.
        )
        for member in field_input  # type: ignore[attr-defined]
    }
