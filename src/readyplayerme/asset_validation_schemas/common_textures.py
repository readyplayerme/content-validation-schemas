"""
Common Texture Validation Schema.

This module defines a Pydantic model for validating common properties of texture maps. It includes error messages
for validation failures and provides a JSON schema for the model.

Author: Daniel-Ionut Rancea <TechyDaniel@users.noreply.github.com>
Co-authored-by: Olaf Haag <Olaf-Wolf3D@users.noreply.github.com>
Co-authored-by: Ivan Sanandres Gutierrez <IvanRPM@users.noreply.github.com>
"""
from enum import Enum
from typing import Literal

from pydantic import ConfigDict, Field, ValidationError

from readyplayerme.asset_validation_schemas.basemodel import BaseModel

MAX_FILE_SIZE = 2  # in MB
MAX_GPU_SIZE = 6  # in MB
# TODO: Figure out how to reference other fields in error messages. Maybe use model_validator instead of field_validator
INSTANCE_ERROR_MSG = "Texture map is unused."
MIMETYPE_ERROR_MSG = "Texture map must be encoded as PNG or JPEG. Found {value} instead."
RESOLUTION_ERROR_MSG = "Image resolution must be a power of 2 and square. Maximum {valid_value}. Found {value} instead."
FILE_SIZE_ERROR_MSG = "Texture map exceeds maximum allowed storage size of {valid_value} MB."
GPU_SIZE_ERROR_MSG = "Texture map exceeds maximum allowed GPU size of {valid_value} MB when fully decompressed."


class ResolutionType(str, Enum):
    """Image resolution data used for textures. Power of 2 and square."""

    _1x1 = "1x1"
    _2x2 = "2x2"
    _4x4 = "4x4"
    _8x8 = "8x8"
    _16x16 = "16x16"
    _32x32 = "32x32"
    _64x64 = "64x64"
    _128x128 = "128x128"
    _256x256 = "256x256"
    _512x512 = "512x512"
    _1024x1024 = "1024x1024"

    def __str__(self):
        """
        Get a string representation of the ResolutionType enum value.

        Returns:
        str: The string representation of the enum value.
        """
        return self.value


class CommonTexture(BaseModel):
    """Validation schema for common properties of texture maps."""

    model_config = ConfigDict(title="Common Texture Map Properties")

    name: str
    uri: str
    instances: int = Field(..., ge=1, json_schema_extra={"errorMessages": {"minimum": INSTANCE_ERROR_MSG}})
    mime_type: Literal["image/png", "image/jpeg"] = Field(
        json_schema_extra={"errorMessages": MIMETYPE_ERROR_MSG.format(value="${0}")}
    )
    compression: str
    resolution: ResolutionType = Field(
        ...,
        json_schema_extra={
            "errorMessages": RESOLUTION_ERROR_MSG.format(valid_value=str(list(ResolutionType)[-1]), value="${0}")
        },
    )
    size: int = Field(
        ...,
        le=MAX_FILE_SIZE * 1024**2,
        json_schema_extra={"errorMessages": {"maximum": FILE_SIZE_ERROR_MSG.format(valid_value=MAX_FILE_SIZE)}},
    )  # Convert to bytes.
    gpu_size: int = Field(
        ...,
        le=MAX_GPU_SIZE * 1024**2,
        json_schema_extra={"errorMessages": {"maximum": GPU_SIZE_ERROR_MSG.format(valid_value=MAX_GPU_SIZE)}},
    )


# Print the generated JSON schema with indentation
if __name__ == "__main__":
    import json
    import logging

    logging.basicConfig(level=logging.DEBUG)
    # Convert model to JSON schema.
    logging.debug(json.dumps(CommonTexture.model_json_schema(), indent=2))

    # Example of validation in Python
    try:
        CommonTexture(
            name="normalmap",
            uri="path/to/normal.png",
            instances=0,
            mime_type="image/webP",
            compression="default",
            resolution="2048x1024",
            size=3097152,
            gpu_size=20291456,
        )
    except ValidationError as error:
        logging.debug("\nValidation Errors:\n %s" % error)
