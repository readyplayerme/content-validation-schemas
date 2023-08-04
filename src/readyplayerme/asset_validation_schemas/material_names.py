from typing import Any, ClassVar, List, Literal

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ValidationError, constr, create_model

from readyplayerme.asset_validation_schemas.basemodel import SchemaConfig


class MaterialNamesConfig(SchemaConfig):
    """Material Names schema title and error messages."""

    title = "Material Names"
    error_msg_templates: ClassVar[dict[str, str]] = {
        # Prepend the error code to the messages.
        "literal": "Material name should be '${const}'. Found ${0} instead.",
        "enum": "Material name should be one of ${allowed_values}. Found ${0} instead.",
    }

    @classmethod
    def schema_extra(cls, schema: dict[str, Any], model: type[PydanticBaseModel]) -> None:
        super().schema_extra(schema, model)
        # Add custom ajv-error messages to the schema.
        for prop in schema.get("properties", {}).values():
            if "literal" in prop:
                prop["errorMessage"] = cls.error_msg_templates["literal"].replace("${const}", prop["literal"])
            elif "enum" in prop:
                prop["errorMessage"] = cls.error_msg_templates["enum"].replace("${allowed_values}", str(prop["enum"]))

class MaterialNames(SchemaConfig):
    beard: Literal["Wolf3D_Beard"]
    facewear: Literal["Wolf3D_Facewear"]
    glasses: Literal["Wolf3D_Glasses"]
    hair: Literal["Wolf3D_Hair"]
    halfBodyShirt: Literal["Wolf3D_Shirt"]
    head: Literal["Wolf3D_Skin"]
    headwear: Literal["Wolf3D_Headwear"]
    modularBottom: Literal["Wolf3D_Outfit_Bottom"]
    modularFootwear: Literal["Wolf3D_Outfit_Footwear"]
    modularTop: Literal["Wolf3D_Outfit_Top"]
    nonCustomizableAvatar: List[Literal[
        "Wolf3D_Body",
        "Wolf3D_Eye",
        "Wolf3D_Outfit_Bottom",
        "Wolf3D_Outfit_Footwear",
        "Wolf3D_Outfit_Top",
        "Wolf3D_Skin",
        "Wolf3D_Teeth",
        "Wolf3D_Hair",
        "Wolf3D_Beard",
        "Wolf3D_Facewear"
        "Wolf3D_Glasses"
        "Wolf3D_Headwear"
    ]]
    outfit: List[Literal[
        "Wolf3D_Body",
        "Wolf3D_Outfit_Bottom",
        "Wolf3D_Outfit_Footwear",
        "Wolf3D_Outfit_Top",
    ]]

MaterialNamesModel = create_model(
    "MaterialNames",
    beard=(Literal["Wolf3D_Beard"], ...),
    facewear=(Literal["Wolf3D_Facewear"], ...),
    glasses=(Literal["Wolf3D_Glasses"], ...),
    hair=(Literal["Wolf3D_Hair"], ...),
    halfBodyShirt=(Literal["Wolf3D_Shirt"], ...),
    head=(Literal["Wolf3D_Skin"], ...),
    headwear=(Literal["Wolf3D_Headwear"], ...),
    modularBottom=(Literal["Wolf3D_Outfit_Bottom"], ...),
    modularFootwear=(Literal["Wolf3D_Outfit_Footwear"], ...),
    modularTop=(Literal["Wolf3D_Outfit_Top"], ...),
    nonCustomizableAvatar=(List[Literal[
        "Wolf3D_Body",
        "Wolf3D_Eye",
        "Wolf3D_Outfit_Bottom",
        "Wolf3D_Outfit_Footwear",
        "Wolf3D_Outfit_Top",
        "Wolf3D_Skin",
        "Wolf3D_Teeth",
        "Wolf3D_Hair",
        "Wolf3D_Beard",
        "Wolf3D_Facewear"
        "Wolf3D_Glasses"
        "Wolf3D_Headwear"
    ]], ...),
    outfit=(List[Literal[
        "Wolf3D_Body",
        "Wolf3D_Outfit_Bottom",
        "Wolf3D_Outfit_Footwear",
        "Wolf3D_Outfit_Top",
    ]], ...),
    __config__=MaterialNamesConfig,
)


if __name__ == "__main__":
    # Convert model to JSON schema.
    print(MaterialNamesModel.schema_json(indent=2))
    # Example of validation in Python.
    try:
        # Test example validation.
        MaterialNamesModel(beard="Wrong_Material_Name")
    except ValidationError as error:
        print("\nValidation Errors:\n", error)
