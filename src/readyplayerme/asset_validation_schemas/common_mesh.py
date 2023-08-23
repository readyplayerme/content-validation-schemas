"""Validation model for common properties of meshes."""
from enum import Enum
from typing import Any, Literal

from pydantic import Field, FieldValidationInfo, ValidationError, ValidatorFunctionWrapHandler, field_validator
from pydantic_core import PydanticCustomError

from readyplayerme.asset_validation_schemas.basemodel import PydanticBaseModel


class IntegerType(str, Enum):
    """Integer types for mesh attributes."""

    u8 = "u8"
    u16 = "u16"


class RenderingMode(str, Enum):
    """Rendering modes for meshes."""

    TRIANGLES = "TRIANGLES"
    LINES = "LINES"
    POINTS = "POINTS"


MAXIMUM_MESH_SIZE = 512  # Kb

render_mode_error = f"Rendering mode must be {RenderingMode.TRIANGLES.value}."
primitives_error = "Number of primitives in the mesh must be 1."
indices_error = f"Indices must be '{IntegerType.u16.value}' single-item array."
instances_error = "Only 1 instance per mesh is supported."
mesh_size_errors = {
    "greater_than": f"Maximum allowed mesh size is {MAXIMUM_MESH_SIZE} kB.",
    "less_than_equal": "Mesh has 0 bytes, seems to be empty!",
}


def get_error_type_msg(field_name: str, error: dict[str, Any]) -> tuple[str, str] | tuple[None, None]:
    """Convert the error to a custom error type and message.

    If the error type is not covered, return a None-tuple.
    """
    match field_name, error:
        case "mode", _:
            return "RENDER_MODE", render_mode_error
        case "primitives", _:
            return "PRIMITIVES", primitives_error
        case "indices", _:
            return "INDICES", indices_error
        case "instances", _:
            return "INSTANCES", instances_error
        case "size", {"le": _}:
            return "MESH_SIZE", mesh_size_errors["greater_than"]
        case "size", {"gt": _}:
            return "MESH_SIZE", mesh_size_errors["less_than_equal"]
        case _:
            return None, None


def custom_error_validator(value: Any, handler: ValidatorFunctionWrapHandler, info: FieldValidationInfo) -> Any:
    """Simplify the error message to avoid a gross error stemming from exhaustive checking of all union options."""
    try:
        return handler(value)
    except ValidationError as error:
        for err in error.errors():
            error_type, error_msg = get_error_type_msg(info.field_name, err["ctx"])
            if error_type and error_msg:
                raise PydanticCustomError(error_type, error_msg) from error
            raise  # We didn't cover this error, so raise default.


# @dataclass(config=get_model_config(title="Common Mesh Properties"))
class CommonMesh(PydanticBaseModel):
    """Validation schema for common properties of meshes."""

    name: object
    mode: tuple[Literal[RenderingMode.TRIANGLES]] = Field(
        ...,
        description=f"The rendering mode of the mesh. Only {RenderingMode.TRIANGLES.value} are supported.",
        json_schema_extra={"errorMessage": render_mode_error},
    )

    primitives: int = Field(
        ...,
        ge=1,
        le=1,
        description="Number of geometry primitives to be rendered with the given material.",
        json_schema_extra={"errorMessage": primitives_error},
    )
    glPrimitives: object  # noqa: N815
    vertices: object
    indices: tuple[Literal[IntegerType.u16]] = Field(
        ...,
        description="The index of the accessor that contains the vertex indices.",
        json_schema_extra={"errorMessage": indices_error},
    )
    attributes: object
    instances: Literal[1] = Field(
        ...,
        description="Number of instances to render.",
        json_schema_extra={"errorMessage": instances_error},
    )

    size: int = Field(
        ...,
        gt=0,
        le=MAXIMUM_MESH_SIZE * 1024,  # Convert to bytes.
        description="Byte size. Buffers stored as GLB binary chunk have an implicit limit of (2^32)-1 bytes.",
        json_schema_extra={
            "errorMessage": {
                "maximum": mesh_size_errors["greater_than"],
                "exclusiveMinimum": mesh_size_errors["less_than_equal"],
            }
        },
    )
    # Wrap all field validators in a custom error validator.
    val_wrap = field_validator("*", mode="wrap")(custom_error_validator)


if __name__ == "__main__":
    import logging

    from pydantic import TypeAdapter

    from readyplayerme.asset_validation_schemas.schema_io import write_json

    logging.basicConfig(level=logging.DEBUG)
    # Convert model to JSON schema.
    top_level_schema = TypeAdapter(CommonMesh).json_schema()
    write_json(top_level_schema)

    # Example of validation in Python.
    try:
        # Multiple checks at once. Test non-existent field as well.
        model = CommonMesh(mode=("LINES",), primitives=3, indices=("u8",), instances=2, size=int(1e7), extra_prop="no!")
    except ValidationError as error:
        logging.debug("\nValidation Errors:\n %s", error)
