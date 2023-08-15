"""
Glasses Validation Schema.

This module defines a Pydantic model for validating an asset of type Glasses. It includes error messages
for validation failures and provides a JSON schema for the model.

Author: Daniel-Ionut Rancea <TechyDaniel@users.noreply.github.com>
Co-authored-by: Olaf Haag <Olaf-Wolf3D@users.noreply.github.com>
Co-authored-by: Ivan Sanandres Gutierrez <IvanRPM@users.noreply.github.com>
"""


from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, TypeAdapter, ValidationError

from readyplayerme.asset_validation_schemas import common_mesh, common_textures
from readyplayerme.asset_validation_schemas.basemodel import BaseModel

# Defining constants
# TODO: Figure out how to reference other fields in error messages. Maybe use model_validator instead of field_validator


class Mesh(PydanticBaseModel):
    """
    Mesh validation schema.

    This is a hack to create a 'properties' object.
    inspect() creates a 'properties' object. Do not confuse with the 'properties' keyword.
    """

    properties: common_mesh.CommonMesh


class AssetGlasses(BaseModel):
    """Validation schema for asset of type Glasses."""

    model_config = ConfigDict(title="Glasses Asset")

    scenes: str
    meshes: Mesh
    materials: str
    animations: str | None = None
    textures: common_textures.FullPBR


# Print the generated JSON schema with indentation
if __name__ == "__main__":
    import json
    import logging

    logging.basicConfig(filename=".temp/commonTexture.log", filemode="w", encoding="utf-8", level=logging.DEBUG)
    # Convert model to JSON schema.
    logging.debug(json.dumps(TypeAdapter(AssetGlasses).json_schema(), indent=2))

    # Example of validation in Python
    try:
        AssetGlasses(
            scenes="glass_scene",
            meshes=Mesh(
                properties=common_mesh.CommonMesh(
                    mode=("LINES",), primitives=3, indices=("u8",), instances=2, size=int(1e7), extra_prop="no!"
                ),
            ),
            materials="glass_material",
            animations=None,
            textures=common_textures.FullPBR(
                properties=common_textures.CommonTexture(
                    name="normalmap",
                    uri="path/to/normal.asf",
                    instances=1,
                    mime_type="image/png",
                    compression="default",
                    resolution="1024x1024",
                    size=1097152,
                    gpu_size=1291456,
                    slots=["normalTexture", "baseColorTexture"],
                ),
            ),
        )

    except ValidationError as error:
        logging.debug("\nValidation Errors:\n %s" % error)
