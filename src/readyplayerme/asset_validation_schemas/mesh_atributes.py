from typing import Any, ClassVar, List, Literal

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ValidationError, constr

from readyplayerme.asset_validation_schemas.basemodel import SchemaConfig


class MeshAttributesConfig(SchemaConfig):
    """Mesh Attributes schema title and error messages."""

    title = "Mesh Attributes"
    error_msg_templates: ClassVar[dict[str, str]] = {
        # Prepend the error code to the messages.
        "enum": "Mesh ${2/name} error! Allowed attributes are: ${enum_values}. Found ${0}.",
        "contains": "Mesh ${2/name} requires at least 5 vertex attributes: position, normal, 1 UV set, joint influences, and weights. Found ${0/length} attributes: ${0}.",
    }

    @classmethod
    def schema_extra(cls, schema: dict[str, Any], model: type[PydanticBaseModel]) -> None:
        super().schema_extra(schema, model)
        # Add custom ajv-error messages to the schema.
        for prop in schema.get("properties", {}).values():
            if "enum" in prop:
                prop["errorMessage"] = cls.error_msg_templates["enum"].replace(
                    "${enum_values}", ", ".join(prop["enum"])
                )
            elif "contains" in prop:
                prop["errorMessage"] = cls.error_msg_templates["contains"]

class MeshAttributes(SchemaConfig):
    """Pydantic model for Mesh Attributes."""

    unskinned: List[constr(
        enum=["NORMAL:f32", "POSITION:f32", "TEXCOORD_0:f32", "TANGENT:f32"],
    )]
    skinned: List[constr(
        enum=["JOINTS_0:u8", "NORMAL:f32", "POSITION:f32", "TEXCOORD_0:f32", "TANGENT:f32", "WEIGHTS_0:f32"],
    )]


if __name__ == "__main__":
    # Example of validation in Python
    try:
        # Test example validation.
        data = {
            "unskinned": ["NORMAL:f32", "POSITION:f32", "TEXCOORD_0:f32"],
            "skinned": ["JOINTS_0:u8", "NORMAL:f32", "POSITION:f32", "TEXCOORD_0:f32", "WEIGHTS_0:f32"],
        }
        MeshAttributes(**data)
    except ValidationError as error:
        print("\nValidation Errors:\n", error)
