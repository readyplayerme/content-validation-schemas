"""Model for allowed names of materials for different asset types."""
from enum import Enum
from typing import Annotated, Any, Literal

from pydantic import BaseModel as PydanticBaseModel
from pydantic import (
    Field,
    FieldValidationInfo,
    ValidationError,
    ValidatorFunctionWrapHandler,
    create_model,
    field_validator,
)
from pydantic_core import PydanticCustomError

from readyplayerme.asset_validation_schemas.basemodel import get_model_config

material_names = {
    "beard": "Wolf3D_Beard",
    "body": "Wolf3D_Body",
    "facewear": "Wolf3D_Facewear",
    "glasses": "Wolf3D_Glasses",
    "hair": "Wolf3D_Hair",
    "halfBodyShirt": "Wolf3D_Shirt",
    "head": "Wolf3D_Skin",
    "eye": "Wolf3D_Eye",
    "teeth": "Wolf3D_Teeth",
    "headwear": "Wolf3D_Headwear",
    "bottom": "Wolf3D_Outfit_Bottom",
    "footwear": "Wolf3D_Outfit_Footwear",
    "top": "Wolf3D_Outfit_Top",
}


class OutfitMaterialNames(str, Enum):
    """Allowed names of materials for outfit assets."""

    bottom = material_names["bottom"]
    footwear = material_names["footwear"]
    top = material_names["top"]
    body = material_names["body"]


class HeroAvatarMaterialNames(str, Enum):
    """Allowed names of materials for hero avatar assets."""

    bottom = material_names["bottom"]
    footwear = material_names["footwear"]
    top = material_names["top"]
    body = material_names["body"]
    head = material_names["head"]
    eye = material_names["eye"]
    teeth = material_names["teeth"]
    hair = material_names["hair"]
    beard = material_names["beard"]
    facewear = material_names["facewear"]
    glasses = material_names["glasses"]
    headwear = material_names["headwear"]


ERROR_CODE = "MATERIAL_NAME"
DOCS_URL = "https://docs.readyplayer.me/asset-creation-guide/validation/validation-checks/"


def get_error_type_msg(field_name: str, value: Any) -> tuple[str, str] | tuple[None, None]:
    """Convert the error to a custom error type and message.

    If the error type is not covered, return a None-tuple.
    """
    match field_name:
        case key if key in material_names:
            return (
                ERROR_CODE,
                f"Material name should be '{material_names[key]}'. Found '{value}' instead."
                + f"\n\tFor further information visit {DOCS_URL}.".expandtabs(4) * bool(DOCS_URL),
            )
        case "outfit":
            return (
                ERROR_CODE,
                f"Material name should be one of {', '.join(OutfitMaterialNames)}. Found '{value}' instead."
                + f"\n\tFor further information visit {DOCS_URL}.".expandtabs(4) * bool(DOCS_URL),
            )
        case key if key in ("non_customizable_avatar", "nonCustomizableAvatar"):
            return (
                ERROR_CODE,
                f"Material name should be one of {', '.join(HeroAvatarMaterialNames)}. Found '{value}' instead."
                + f"\n\tFor further information visit {DOCS_URL}.".expandtabs(4) * bool(DOCS_URL),
            )
        case _:
            return None, None


def custom_error_validator(value: Any, handler: ValidatorFunctionWrapHandler, info: FieldValidationInfo) -> Any:
    """Wrap the field validation function to raise custom error types.

    Return the validated value if no error occurred.
    """
    try:
        return handler(value)
    except ValidationError as error:
        for err in error.errors():
            error_type, error_msg = get_error_type_msg(info.field_name, err["input"])
            if error_type and error_msg:
                raise PydanticCustomError(error_type, error_msg) from error
            raise  # We didn't cover this error, so raise default.


def get_material_name_type(material_name: str) -> Annotated:
    """Return a constrained positive integer field type with custom error messages."""
    return Annotated[
        Literal[material_name],
        Field(json_schema_extra={"errorMessage": "Material name should be '%s'. Found ${0} instead." % material_name}),
    ]


def get_material_name_field_definitions(material_names: dict[str, str]) -> Any:
    """Turn simple integer limits into a dict of constrained positive integer field types with custom error messages."""
    return {
        field_name: (  # Tuple of (type definition, default value).
            get_material_name_type(material_name),
            None,  # Default value.
        )
        for field_name, material_name in material_names.items()
    }


# Define fields for outfit assets and hero avatar assets.
outfit_field = Annotated[
    OutfitMaterialNames,
    Field(
        json_schema_extra={
            "errorMessage": "Material name should be one of %s. Found ${0} instead." % ", ".join(OutfitMaterialNames)
        }
    ),
]

hero_avatar_field = Annotated[
    HeroAvatarMaterialNames,
    Field(
        json_schema_extra={
            "errorMessage": "Material name should be one of %s. Found ${0} instead."
            % ", ".join(HeroAvatarMaterialNames)
        }
    ),
]

# Wrap all field validators in a custom error validator.
wrapped_validator = field_validator("*", mode="wrap")(custom_error_validator)

MaterialNamesModel: type[PydanticBaseModel] = create_model(
    "MaterialNames",
    __config__=get_model_config(title="Material Names"),
    __validators__={"*": wrapped_validator},
    **get_material_name_field_definitions(material_names),
    outfit=(outfit_field, None),
    non_customizable_avatar=(hero_avatar_field, None),
)


if __name__ == "__main__":
    import json
    import logging

    logging.basicConfig(level=logging.DEBUG)
    # Convert model to JSON schema.
    logging.debug(json.dumps(MaterialNamesModel.model_json_schema(), indent=2))
    # Example of validation in Python.
    try:
        # Test example validation.
        MaterialNamesModel(beard="Wrong_Material_Name", outfit="Other_Wrong_Material_Name")
    except (PydanticCustomError, ValidationError, TypeError) as error:
        logging.error("\nValidation Errors:\n %s", error)
