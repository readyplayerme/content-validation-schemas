from typing import Any, Literal, Union

from pydantic import ValidationError, ValidatorFunctionWrapHandler, FieldValidationInfo, field_validator
from pydantic.dataclasses import dataclass
from pydantic_core import PydanticCustomError

from readyplayerme.asset_validation_schemas.basemodel import get_model_config

ERROR_CODE = "MESH_ATTRIBUTES"
ERROR_MSG_UNSKINNED = [
    "Mesh {name} error! Allowed attributes are: NORMAL, POSITION, TEXCOORD_0, TANGENT. Found {wrong_value}",
    "Mesh {name} requires at least 3 vertex attributes: position, normal and 1 UV set. Found {number} attributes: {attributes}.",
]
ERROR_MSG_SKINNED = [
    "Mesh {name} error! Allowed attributes are: JOINTS_0, NORMAL, POSITION, TEXCOORD_0, TANGENT, WEIGHTS_0. Found {wrong_value}",
    "Mesh {name} requires at least 5 vertex attributes: position, normal, 1 UV set, joint influences, and weights. Found {number} attributes: {attributes}.",
]
DOCS_URL = "https://docs.readyplayer.me/asset-creation-guide/validation/validation-checks/"

unskinned_possible_attributes = ["NORMAL:f32", "POSITION:f32", "TEXCOORD_0:f32", "TANGENT:f32"]
skinned_possible_attributes = [
    "JOINTS_0:u8",
    "NORMAL:f32",
    "POSITION:f32",
    "TEXCOORD_0:f32",
    "TANGENT:f32",
    "WEIGHTS_0:f32",
]


def get_error_type_msg_unskinned(field_name: str, attr: str, items: tuple[Literal]) -> tuple[None, None]:
    """Convert the error to a custom error type and message.

    If the error type is not covered, return a None-tuple.
    """
    match field_name:
        case attr if attr in unskinned_possible_attributes:
            return (ERROR_CODE, ERROR_MSG_UNSKINNED[0].format(wrong_value=attr))
        case items if len(items) < 3:
            return (ERROR_CODE, ERROR_MSG_UNSKINNED[1].format(number=len(items), attributes=items))
        case _:
            return None, None


def custom_error_validator_unskinned(
    value: Any, handler: ValidatorFunctionWrapHandler, info: FieldValidationInfo
) -> Any:
    """Simplify the error message to avoid a gross error stemming from exhaustive checking of all union options."""
    try:
        return handler(value)
    except ValidationError as error:
        for err in error.errors():
            error_type, error_msg = get_error_type_msg_unskinned(info.field_name, err["input"], value)
            if error_type and error_msg:
                raise PydanticCustomError(error_type, error_msg) from error
            raise  # We didn't cover this error, so raise default.


def get_error_type_msg_skinned(field_name: str, error: dict[str, Any]) -> tuple[str, str] | tuple[None, None]:
    """Convert the error to a custom error type and message.

    If the error type is not covered, return a None-tuple.
    """
    match field_name, error:
        case "items", _:
            return "RENDER_MODE", ERROR_MSG_SKINNED[0]
        case "contains", _:
            return "PRIMITIVES", ERROR_MSG_SKINNED[1]
        case _:
            return None, None


def custom_error_validator_skinned(value: Any, handler: ValidatorFunctionWrapHandler, info: FieldValidationInfo) -> Any:
    """Simplify the error message to avoid a gross error stemming from exhaustive checking of all union options."""
    try:
        return handler(value)
    except ValidationError as error:
        for err in error.errors():
            error_type, error_msg = get_error_type_msg_skinned(info.field_name, err["input"])
            if error_type and error_msg:
                raise PydanticCustomError(error_type, error_msg) from error
            raise  # We didn't cover this error, so raise default.


@dataclass(config=get_model_config(title="Unskinned Mesh Attributes"))
class Unskinned:
    """Validation schema for unskinned mesh attributes."""

    items: tuple[Literal["NORMAL:f32", "POSITION:f32", "TEXCOORD_0:f32", "TANGENT:f32"], ...] = Field(
        ...,
        json_schema_extra={
            "errorMessage": ERROR_MSG_UNSKINNED[0],
        },
    )
    contains: str = Field(
        pattern=r"NORMAL:f32|POSITION:f32|TEXCOORD_0:f32",
        json_schema_extra={
            "errorMessage": ERROR_MSG_UNSKINNED[1],
        },
    )
    val_wrap = field_validator("*", mode="wrap")(custom_error_validator_unskinned)


@dataclass(config=get_model_config(title="Skinned Mesh Attributes"))
class Skinned:
    """Validation schema for skinned mesh attributes."""

    items: tuple[
        Literal["JOINTS_0:u8", "NORMAL:f32", "POSITION:f32", "TEXCOORD_0:f32", "TANGENT:f32", "WEIGHTS_0:f32"], ...
    ] = Field(
        ...,
        json_schema_extra={
            "errorMessage": ERROR_MSG_SKINNED[0],
        },
    )
    contains: str = Field(
        pattern=r"JOINTS_0:u8|NORMAL:f32|POSITION:f32|TEXCOORD_0:f32|WEIGHTS_0:f32",
        json_schema_extra={
            "errorMessage": ERROR_MSG_UNSKINNED[1],
        },
    )
    val_wrap = field_validator("*", mode="wrap")(custom_error_validator_skinned)


@dataclass(config=get_model_config(title="Mesh Attributes"))
class MeshAttributes:
    """Data attributes for mesh vertices. Includes the vertex position, normal, tangent, texture coordinates, influencing joints, and skin weights."""

    MeshAttributes: Union[Unskinned, Skinned]


if __name__ == "__main__":
    import json
    import logging

    from pydantic import TypeAdapter

    logging.basicConfig(level=logging.DEBUG)
    # Convert model to JSON schema.
    logging.debug(json.dumps(TypeAdapter(MeshAttributes).json_schema(), indent=2))

    try:
        model = MeshAttributes(MeshAttributes=Unskinned(items=("WRONG_ATTR", "TEXCOORD_0:f32")))
    except ValidationError as error:
        print("\nValidation Errors:\n", error)
