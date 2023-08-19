"""Sub-schemas for animation validation."""
from pydantic import Field, ValidationError, field_validator
from pydantic.dataclasses import dataclass
from pydantic_core import ErrorDetails

from readyplayerme.asset_validation_schemas.validators import CustomValidator, ErrorMsgReturnType

ANIMATION_ERROR = "AnimationError"
ANIMATION_ERROR_MSG = "Animation is currently not supported."


def error_msg_func(field_name: str, error_details: ErrorDetails) -> ErrorMsgReturnType:  # noqa: ARG001
    """Return a custom error type and message for the animation model."""
    return ANIMATION_ERROR, ANIMATION_ERROR_MSG


@dataclass
class NoAnimation:
    """Empty animation data."""

    properties: list[object] = Field(
        max_length=0,
        description="List of animations.",
        json_schema_extra={
            "errorMessage": ANIMATION_ERROR_MSG,
            "$comment": (
                "gltf-transform's inspect() creates a 'properties' object. "
                "Do not confuse with the 'properties' keyword."
            ),
        },
    )
    validation_wrapper = field_validator("*", mode="wrap")(CustomValidator(error_msg_func).custom_error_validator)


if __name__ == "__main__":
    import logging

    from pydantic.json_schema import model_json_schema
    from pydantic_core import PydanticCustomError

    from readyplayerme.asset_validation_schemas.basemodel import SchemaNoTitleAndDefault
    from readyplayerme.asset_validation_schemas.schema_io import write_json

    logging.basicConfig(encoding="utf-8", level=logging.DEBUG)

    # Demonstrate alternative way to convert a model to custom JSON schema.
    top_level_schema = model_json_schema(
        NoAnimation, schema_generator=SchemaNoTitleAndDefault  # type: ignore[arg-type]
    )
    write_json(top_level_schema)

    # Example of validation in Python.
    try:
        # Multiple checks at once. Test non-existent field as well.
        NoAnimation(**{"properties": [1]})  # type: ignore[arg-type]
    except (PydanticCustomError, ValidationError, TypeError) as error:
        logging.error("\nValidation Errors:\n %s", error)
