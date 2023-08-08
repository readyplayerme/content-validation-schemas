"""Validation model for common properties of meshes."""
from enum import Enum
from typing import Literal

from pydantic import Field, ValidationError
from pydantic.dataclasses import dataclass

from readyplayerme.asset_validation_schemas.basemodel import get_model_config


class IntegerType(str, Enum):
    """Integer types for mesh attributes."""

    u8 = "u8"
    u16 = "u16"


class RenderingMode(str, Enum):
    """Rendering modes for meshes."""

    TRIANGLES = "TRIANGLES"
    LINES = "LINES"
    POINTS = "POINTS"


@dataclass(config=get_model_config(title="Common Mesh Properties"))
class CommonMesh:
    """Validation schema for common properties of meshes."""

    mode: tuple[Literal[RenderingMode.TRIANGLES]] = Field(
        description=f"The rendering mode of the mesh. Only {RenderingMode.TRIANGLES.value} are supported.",
        json_schema_extra={"errorMessage": f"Rendering mode must be {RenderingMode.TRIANGLES.value}."},
    )
    primitives: int = Field(
        ...,
        ge=1,
        le=2,
        description="Number of geometry primitives to be rendered with the given material.",
        json_schema_extra={
            "errorMessage": (
                "Number of primitives in the mesh must be 1, or 2 when an additional transparent material is used."
            )
        },
    )
    indices: tuple[Literal[IntegerType.u16]] = Field(
        description="The index of the accessor that contains the vertex indices.",
        json_schema_extra={"errorMessage": f"Indices must be '{IntegerType.u16.value}' single-item array."},
    )
    instances: Literal[1] = Field(
        description="Number of instances to render.",
        json_schema_extra={"errorMessage": "Only 1 instance per mesh is supported."},
    )
    size: int = Field(
        ...,
        gt=0,
        le=524288,
        description="Byte size. Buffers stored as GLB binary chunk have an implicit limit of (2^32)-1 bytes.",
        json_schema_extra={
            "errorMessage": {
                "maximum": "Maximum allowed mesh size is 512 kB.",
                "exclusiveMinimum": "Mesh has 0 bytes, seems to be empty!",
            }
        },
    )


if __name__ == "__main__":
    import json
    import logging

    from pydantic import TypeAdapter

    logging.basicConfig(level=logging.DEBUG)
    # Convert model to JSON schema.
    logging.debug(json.dumps(TypeAdapter(CommonMesh).json_schema(), indent=2))

    # Example of validation in Python.
    try:
        # Multiple checks at once. Test non-existent field as well.
        model = CommonMesh(mode=("LINES",), primitives=3, indices=("u8",), instances=2, size=int(1e7), extra_prop="no!")
    except ValidationError as error:
        logging.debug("\nValidation Errors:\n %s", error)
