"""
Common Texture Validation Schema.

This module defines a Pydantic model for validating common properties of texture maps. It includes error messages
for validation failures and provides a JSON schema for the model.

Author: Daniel-Ionut Rancea <TechyDaniel@users.noreply.github.com>
Co-authored-by: Olaf Haag <Olaf-Wolf3D@users.noreply.github.com>
Co-authored-by: Ivan Sanandres Gutierrez <IvanRPM@users.noreply.github.com>
"""
from enum import Enum
from typing import Literal, TypeAlias

from pydantic import ConfigDict, Field, ValidationError
from pydantic.json_schema import models_json_schema

from readyplayerme.asset_validation_schemas.basemodel import BaseModel

MAX_FILE_SIZE = 2  # in MB
MAX_GPU_SIZE = 6  # in MB
# TODO: Figure out how to reference other fields in error messages. Maybe use model_validator instead of field_validator
INSTANCE_ERROR_MSG = "Texture map is unused."
MIMETYPE_ERROR_MSG = "Texture map must be encoded as PNG or JPEG. Found {value} instead."
RESOLUTION_ERROR_MSG = "Image resolution must be a power of 2 and square. Maximum {valid_value}. Found {value} instead."
FILE_SIZE_ERROR_MSG = "Texture map exceeds maximum allowed storage size of {valid_value} MB."
GPU_SIZE_ERROR_MSG = "Texture map exceeds maximum allowed GPU size of {valid_value} MB when fully decompressed."


ResolutionType: TypeAlias = Literal[
    "16x16",
    "32x32",
    "64x64",
    "128x128",
    "256x256",
    "512x512",
    "1024x1024",
]


class TextureSlot(str, Enum):
    """Available texture inputs for materials."""

    normal_texture = "normalTexture"
    base_color_texture = "baseColorTexture"
    emissive_texture = "emissiveTexture"
    metallic_roughness_texture = "metallicRoughnessTexture"
    occlusion_texture = "occlusionTexture"

    def __str__(self):
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
        description="Image resolution data used for textures. Power of 2 and square.",
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


class FullPBRTextureSet(CommonTexture):
    """Accepting any texture type."""

    slots: list[
        Literal[
            TextureSlot.normal_texture,
            TextureSlot.base_color_texture,
            TextureSlot.emissive_texture,
            TextureSlot.metallic_roughness_texture,
            TextureSlot.occlusion_texture,
        ]
    ] = Field(..., min_items=1, max_items=5)


class NormalOcclusionMapTextureSet(CommonTexture):
    """Accepting only normal and occlusion textures."""

    slots: list[Literal[TextureSlot.normal_texture, TextureSlot.occlusion_texture]] = Field(
        ..., min_items=1, max_items=1
    )


class NormalMap(BaseModel):
    """Normal map validation schema."""

    properties: list[NormalOcclusionMapTextureSet]


class FullPBR(BaseModel):
    """Full PBR validation schema."""

    properties: list[FullPBRTextureSet]


_, top_level_schema = models_json_schema([(NormalMap, "validation"), (FullPBR, "validation")])

# Print the generated JSON schema with indentation
if __name__ == "__main__":
    import json
    import logging

    logging.basicConfig(filename=".temp/commonTexture.log", filemode="w", encoding="utf-8", level=logging.DEBUG)
    # Convert model to JSON schema.
    logging.debug(json.dumps(top_level_schema, indent=2))

    # Example of validation in Python
    try:
        FullPBRTextureSet(
            name="normalmap",
            uri="path/to/normal.png",
            instances=1,
            mime_type="image/png",
            compression="default",
            resolution="1024x1024",
            size=1097152,
            gpu_size=1291456,
            slots=["metallicRoughnessTexture", "occlusionTexture", "specularMap"],
        )
    except ValidationError as error:
        logging.debug("\nValidation Errors:\n %s" % error)
