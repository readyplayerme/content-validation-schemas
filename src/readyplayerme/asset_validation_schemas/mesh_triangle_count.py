from typing import Any, ClassVar

from pydantic import BaseModel as PydanticBaseModel
from pydantic import (
    ValidationError,
    conint,
    create_model,
)

from readyplayerme.asset_validation_schemas.basemodel import SchemaConfig

ERROR_CODE = "TRIANGLE_COUNT"

# Triangle budgets could be set via config.
limits = {
    "beard": 1000,
    "body": 14000,
    "body_custom": 14000,
    "eyebrow": 60,
    "eye": 60,
    "facewear": 900,
    "glasses": 1000,
    "hair": 3000,
    "head": 4574,
    "headCustom": 6000,
    "headwear": 2500,
    "outfitBottom": 6000,
    "outfitTop": 6000,
    "outfitFootwear": 2000,
    "halfbodyShirt": 1000,
    "teeth": 1000,
}


def get_tricount_field_definitions(limits: dict[str, int]) -> Any:
    """Turn simple integer limits into a dict of constrained positive integer field types."""
    return {field_name: (conint(gt=0, le=limit), None) for field_name, limit in limits.items()}


class TriCountConfig(SchemaConfig):
    """Triangle count schema title and error messages."""

    title = "Triangle Count"
    error_msg_templates: ClassVar[dict[str, str]] = {
        # Prepend the error code to the messages.
        e: f"{ERROR_CODE} " + msg
        for e, msg in {
            "value_error.number.not_gt": "Mesh must have at least 1 triangle.",
            "value_error.number.not_le": "Mesh exceeds triangle count budget. Allowed: {limit_value}.",
            "value_error.extra": "Invalid extra mesh.",
        }.items()
    }

    @classmethod  # As a staticmethod, TypeError is raised with super().schema_extra args. Works with classmethod.
    def schema_extra(cls, schema: dict[str, Any], model: type["PydanticBaseModel"]) -> None:
        super().schema_extra(schema, model)
        # Add custom ajv-error messages to the schema.
        for prop in schema.get("properties", {}).values():
            prop["errorMessage"] = {
                "exclusiveMinimum": "Mesh ${1/name} must have at least 1 triangle.",
                "maximum": "Mesh ${1/name} exceeds triangle count budget. Allowed: %d. Found: ${0}." % prop["maximum"],
            }


# Dynamically create the model with the tri-count limits we defined earlier.
MeshTriangleCountModel: type[PydanticBaseModel] = create_model(
    "MeshTriangleCount",
    __config__=TriCountConfig,
    # Populate the fields.
    **get_tricount_field_definitions(limits),
)


if __name__ == "__main__":
    # Convert model to JSON schema.
    print(MeshTriangleCountModel.schema_json(indent=2))

    # Example of validation in Python.
    try:
        # Multiple checks at once. Test non-existent field as well.
        MeshTriangleCountModel(outfitBottom=6000, outfitTop=0, outfitFootwear=3000, foo=10)
    except ValidationError as error:
        print("\nValidation Errors:\n", error)
