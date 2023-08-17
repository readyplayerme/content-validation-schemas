"""Sub-schemas for animation validation."""
from pydantic import Field, ValidationError, field_validator
from pydantic.dataclasses import dataclass
from pydantic.json_schema import GenerateJsonSchema, JsonSchemaMode, JsonSchemaValue
from pydantic_core import CoreSchema, ErrorDetails

from readyplayerme.asset_validation_schemas.basemodel import remove_keywords_from_properties
from readyplayerme.asset_validation_schemas.validators import CustomValidator, ErrorMsgReturnType

ANIMATION_ERROR = "AnimationError"
ANIMATION_ERROR_MSG = "Animation is currently not supported."


class GenerateAnimationJsonSchema(GenerateJsonSchema):
    """Generate the animation model JSON schema."""

    def generate(self, schema: CoreSchema, mode: JsonSchemaMode = "validation") -> JsonSchemaValue:
        _schema = super().generate(schema, mode)
        remove_keywords_from_properties(_schema, ["title", "default"])
        _schema.pop("title", None)
        return _schema


def error_msg_func(field_name: str, error_details: ErrorDetails) -> ErrorMsgReturnType:  # noqa: ARG001
    """Return a custom error type and message for the animation model."""
    return ANIMATION_ERROR, ANIMATION_ERROR_MSG


@dataclass
class NoAnimation:
    """Empty animation data."""

    properties: list[object] = Field(
        ...,
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
    import json
    import logging
    from pathlib import Path

    from pydantic.json_schema import model_json_schema
    from pydantic_core import PydanticCustomError

    Path(".temp").mkdir(exist_ok=True)
    logging.basicConfig(
        filename=f".temp/{Path(__file__).stem}.log", filemode="w", encoding="utf-8", level=logging.DEBUG
    )
    # Demonstrate alternative way to convert a model to custom JSON schema.
    top_level_schema = model_json_schema(
        NoAnimation, schema_generator=GenerateAnimationJsonSchema  # type: ignore[arg-type]
    )
    logging.debug(json.dumps(top_level_schema, indent=2))

    # Example of validation in Python.
    try:
        # Multiple checks at once. Test non-existent field as well.
        NoAnimation(**{"properties": [1]})  # type: ignore[arg-type]
    except (PydanticCustomError, ValidationError, TypeError) as error:
        logging.error("\nValidation Errors:\n %s", error)
