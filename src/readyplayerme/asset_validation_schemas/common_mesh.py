from enum import Enum
from typing import Any

from pydantic import Field, ValidationError, validator

from readyplayerme.asset_validation_schemas.basemodel import BaseModel


class IntegerType(str, Enum):
    u8 = "u8"
    u16 = "u16"


class RenderingMode(str, Enum):
    TRIANGLES = "TRIANGLES"
    LINES = "LINES"
    POINTS = "POINTS"


class CommonMesh(BaseModel):
    """Validation schema for common properties of meshes."""

    class Config(BaseModel.Config):
        title = "Common Mesh Properties"
        error_msg_templates = {"value_error.number.not_le": "The value must be less than or equal to {limit_value}"}

        @classmethod
        def schema_extra(cls, schema: dict[str, Any], model: type["BaseModel"]) -> None:
            super().schema_extra(schema, model)
            schema["required"] = ["mode", "primitives", "indices", "instances", "size"]

    mode: set[str] = Field(
        {RenderingMode.TRIANGLES},
        description=f"The rendering mode of the mesh. Only {RenderingMode.TRIANGLES.value} are supported.",
        errorMessage=f"Rendering mode must be {RenderingMode.TRIANGLES.value}.",
        const=True,
    )
    primitives: int = Field(
        ...,
        ge=1,
        le=2,
        description="Number of geometry primitives to be rendered with the given material.",
        errorMessage="Number of primitives in the mesh must be 1, or 2 when an additional transparent material is used.",
    )
    indices: set[str] = Field(
        {IntegerType.u16},
        description="The index of the accessor that contains the vertex indices.",
        errorMessage=f"Indices must be '{IntegerType.u16.value}' single-item array.",
        const=True,
    )
    instances: int = Field(
        1,
        const=True,
        description="Number of instances to render.",
        errorMessage="Only 1 instance per mesh is supported.",
    )
    size: int = Field(
        ...,
        gt=0,
        le=524288,
        description="Byte size. Buffers stored as GLB binary chunk have an implicit limit of (2^32)-1 bytes.",
        errorMessage={
            "maximum": "Maximum allowed mesh size is 512 kB.",
            "exclusiveMinimum": "Mesh has 0 bytes, seems to be empty!",
        },
    )

    @validator("size", pre=True)
    def check_size(cls, value):
        if value == 0:
            msg = "Mesh size must be greater than 0 Bytes."
            raise ValueError(msg)
        return value


if __name__ == "__main__":
    # Convert model to JSON schema.
    print(CommonMesh.schema_json(indent=2))

    # Example of validation in Python.
    try:
        # Multiple checks at once. Test non-existent field as well.
        model = CommonMesh(mode=["LINES"], primitives=3, indices=["u8"], instances=2, size=1e7)
    except ValidationError as error:
        print("\nValidation Errors:\n", error)
