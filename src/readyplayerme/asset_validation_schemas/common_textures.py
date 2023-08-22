"""Validation models for properties of image textures."""
from collections.abc import Iterable
from enum import Enum
from typing import Annotated, Any, Literal, cast

from pydantic import ConfigDict, Field, ValidationError, field_validator
from pydantic.alias_generators import to_snake
from pydantic_core import ErrorDetails

from readyplayerme.asset_validation_schemas.basemodel import PydanticBaseModel, get_model_config
from readyplayerme.asset_validation_schemas.schema_io import properties_comment
from readyplayerme.asset_validation_schemas.types import create_enum_class, get_enum_length
from readyplayerme.asset_validation_schemas.validators import CustomValidator, ErrorMsgReturnType

MAX_FILE_SIZE = 2  # in MB
MAX_GPU_SIZE = 6  # in MB
# TODO: Figure out how to reference other fields in Python error messages. Maybe use model_validator instead of field_validator
TEXTURE_ERROR = "TextureError"
INSTANCE_ERROR_MSG = "Texture map is unused."
MIMETYPE_ERROR_MSG = "Texture map must be encoded as PNG or JPEG. Found {value} instead."
RESOLUTION_ERROR_MSG = "Image resolution must be a power of 2 and square. Maximum {valid_value}. Found {value} instead."
FILE_SIZE_ERROR_MSG = "Texture map exceeds maximum allowed storage size of {valid_value} MB."
GPU_SIZE_ERROR_MSG = "Texture map exceeds maximum allowed GPU size of {valid_value} MB when fully decompressed."
MIN_MAP_COUNT_ERROR_MSG = (
    "Too few texture maps ({value})! This Asset type must have at least one base color texture map."
)
MAX_MAP_COUNT_ERROR_MSG = "Too many texture maps ({value})! Allowed: {valid_value}."
SLOTS_ERROR_MSG = "This texture can only be used for slots: {valid_value}. Found '{value}' instead."
MIN_SLOTS_ERROR_MSG = (
    "Too few material slots ({value}) occupied by this texture! "
    "It must be used in at least {valid_value} material slots."
)
MAX_SLOTS_ERROR_MSG = "Texture map used for too many slots ({value}). Allowed: {valid_value}."

Resolution: Enum = create_enum_class(
    "resolution",
    {
        f"_{res}": res
        for res in [
            "16x16",
            "32x32",
            "64x64",
            "128x128",
            "256x256",
            "512x512",
            "1024x1024",
        ]
    },
)
# Create enum classes for material slots a texture map can be used in.
texture_slots = {
    to_snake(tex): tex
    for tex in ["normalTexture", "baseColorTexture", "emissiveTexture", "metallicRoughnessTexture", "occlusionTexture"]
}

TextureSlotStandard: Enum = create_enum_class("textureSlotStandard", texture_slots)
TextureSlotNormalOcclusion: Enum = create_enum_class(
    "textureSlotNormalOcclusion", texture_slots, {"normal_texture", "occlusion_texture"}
)


def error_msg_func_common(field_name: str, error_details: ErrorDetails) -> ErrorMsgReturnType:
    """Return a custom error type and message for the texture model."""
    match field_name:
        case "instances":
            return TEXTURE_ERROR, INSTANCE_ERROR_MSG
        case "mime_type":
            return TEXTURE_ERROR, MIMETYPE_ERROR_MSG.format(value=error_details.get("value"))
        case "resolution":
            return (
                TEXTURE_ERROR,
                RESOLUTION_ERROR_MSG.format(
                    valid_value=next(reversed(Resolution)).value,  # type: ignore[call-overload] # Enum is reversible.
                    value=error_details.get("value"),
                ),
            )
        case "size":
            return TEXTURE_ERROR, FILE_SIZE_ERROR_MSG.format(valid_value=MAX_FILE_SIZE)
        case "gpu_size":
            return TEXTURE_ERROR, GPU_SIZE_ERROR_MSG.format(valid_value=MAX_GPU_SIZE)

    return None, None


def error_msg_func_slots(field_name: str, error_details: ErrorDetails) -> ErrorMsgReturnType:  # noqa: ARG001
    """Return a custom error type and message for the texture model."""
    match error_details:
        case {"type": "enum"}:
            expected = error_details.get("ctx", {}).get("expected")
            return TEXTURE_ERROR, SLOTS_ERROR_MSG.format(valid_value=expected, value=error_details.get("input"))
        case {"type": "too_long"}:
            return generate_length_error_msg(error_details, "max_length", MAX_SLOTS_ERROR_MSG)
        case {"type": "too_short"}:
            return generate_length_error_msg(error_details, "min_length", MIN_SLOTS_ERROR_MSG)
    return None, None


def generate_length_error_msg(error_details, length_type, error_msg_template):
    """Generate an error message related to the length of an input value."""
    expected = error_details.get("ctx", {}).get(length_type)
    input_value = error_details.get("input")
    if input_value is not None:
        actual_length = len(input_value)
    return TEXTURE_ERROR, error_msg_template.format(valid_value=expected, value=actual_length)


class CommonTextureProperties(PydanticBaseModel):
    """Validation schema for common properties of texture maps."""

    model_config = ConfigDict(title="Common Texture Map Properties", use_enum_values=True)

    name: str
    uri: str
    instances: int = Field(ge=1, json_schema_extra={"errorMessage": {"minimum": INSTANCE_ERROR_MSG}})
    mime_type: Literal["image/png", "image/jpeg"] = Field(
        json_schema_extra={"errorMessage": MIMETYPE_ERROR_MSG.format(value="${0}")}
    )
    compression: str
    resolution: Annotated[  # type: ignore[valid-type] # Resolution is an Enum, not a regular variable.
        Resolution,
        Field(
            description="Image resolution data used for textures. Power of 2 and square.",
            json_schema_extra={
                "errorMessage": RESOLUTION_ERROR_MSG.format(valid_value=next(reversed(Resolution)).value, value="${0}")
            },
        ),
    ]
    size: int = Field(
        le=MAX_FILE_SIZE * 1024**2,
        json_schema_extra={"errorMessage": {"maximum": FILE_SIZE_ERROR_MSG.format(valid_value=MAX_FILE_SIZE)}},
    )  # Convert to bytes.
    gpu_size: int = Field(
        le=MAX_GPU_SIZE * 1024**2,
        json_schema_extra={"errorMessage": {"maximum": GPU_SIZE_ERROR_MSG.format(valid_value=MAX_GPU_SIZE)}},
    )
    validation_wrapper = field_validator("*", mode="wrap")(
        CustomValidator(error_msg_func_common).custom_error_validator
    )


def get_slot_field(slots: Enum) -> Any:
    """Annotate the slots enumeration itself, which is a single item in the slots array, by a custom error message."""
    valid = ", ".join(cast(Iterable[str], slots))  # Use cast to make type checker happy.
    return Annotated[
        slots,
        Field(json_schema_extra={"errorMessage": SLOTS_ERROR_MSG.format(valid_value=valid, value="${0}")}),
    ]


class TexturePropertiesStandard(CommonTextureProperties):
    """Texture can occupy any material slot supported by the standard PBR shader."""

    # Having an expression in a type hint is considered invalid, but works for now.
    slots: list[get_slot_field(TextureSlotStandard)] = Field(  # type: ignore[valid-type]
        description="Material inputs that this texture is used for.",
        min_length=1,
        max_length=get_enum_length(TextureSlotStandard),
        # Now we add custom errors to the array.
        json_schema_extra={
            "errorMessage": {
                "minItems": MIN_SLOTS_ERROR_MSG.format(valid_value=1, value="${0/length}"),
                "maxItems": MAX_SLOTS_ERROR_MSG.format(
                    valid_value=get_enum_length(TextureSlotStandard), value="${0/length}"
                ),
            }
        },
    )
    validation_wrapper = field_validator("*", mode="wrap")(CustomValidator(error_msg_func_slots).custom_error_validator)


class TextureSchemaStandard(PydanticBaseModel):
    """Texture schema for a single- or multi-mesh asset with standard PBR map support."""

    model_config = get_model_config(
        json_schema_extra={},
        defer_build=True,
    )
    properties: list[TexturePropertiesStandard] = Field(
        min_length=1,
        json_schema_extra={
            "errorMessage": {"minItems": MIN_MAP_COUNT_ERROR_MSG.format(value="${0/length}")},
            "$comment": properties_comment,
        },
    )


class TexturePropertiesNormalOcclusion(CommonTextureProperties):
    """Texture is only allowed to occupy normal and occlusion material slots."""

    # Having an expression in a type hint is considered invalid, but works for now.
    slots: list[get_slot_field(TextureSlotNormalOcclusion)] = Field(  # type: ignore[valid-type]
        description="Material input slots that this texture is used for.",
        min_length=1,
        max_length=get_enum_length(TextureSlotNormalOcclusion),
        # Now we add custom errors to the array.
        json_schema_extra={
            "errorMessage": {
                "minItems": MIN_SLOTS_ERROR_MSG.format(valid_value=1, value="${0/length}"),
                "maxItems": MAX_SLOTS_ERROR_MSG.format(
                    valid_value=get_enum_length(TextureSlotNormalOcclusion), value="${0/length}"
                ),
            }
        },
    )
    validation_wrapper = field_validator("*", mode="wrap")(CustomValidator(error_msg_func_slots).custom_error_validator)


class TextureSchemaNormalOcclusion(PydanticBaseModel):
    """Texture schema for a single-mesh asset with only normal and occlusion map support."""

    properties: list[TexturePropertiesNormalOcclusion] = Field(
        # Assets that use this texture schema (body, hair, beard) only have a single material.
        # So we can't have more textures than we allow slots in a single material.
        max_length=get_enum_length(TextureSlotNormalOcclusion),
        json_schema_extra={
            "errorMessage": {
                "maxItems": MAX_MAP_COUNT_ERROR_MSG.format(
                    valid_value=get_enum_length(TextureSlotNormalOcclusion), value="${0/length}"
                )
            },
            "$comment": properties_comment,
        },
    )


if __name__ == "__main__":
    import logging

    from pydantic.json_schema import models_json_schema

    from readyplayerme.asset_validation_schemas.basemodel import SchemaNoTitleAndDefault
    from readyplayerme.asset_validation_schemas.schema_io import write_json

    logging.basicConfig(encoding="utf-8", level=logging.DEBUG)
    # Convert model to JSON schema.
    _, schema = models_json_schema(
        [(TextureSchemaNormalOcclusion, "validation"), (TextureSchemaStandard, "validation")],
        schema_generator=SchemaNoTitleAndDefault,
    )
    write_json(schema)

    # Example of validation in Python
    try:
        TexturePropertiesNormalOcclusion(
            name="normalmap",
            uri="path/to/normal.png",
            instances=1,
            mime_type="image/png",
            compression="default",
            resolution="1024x1024",
            size=197152,
            gpu_size=1291456,
            slots=[
                "baseColor",
                "test",
                "asd",
                "gasad",
                "normalTexture",
                "normalTexture",
                "normalTexture",
            ],
        )
    except ValidationError as error:
        logging.debug("\nValidation Errors:\n %s" % error)
