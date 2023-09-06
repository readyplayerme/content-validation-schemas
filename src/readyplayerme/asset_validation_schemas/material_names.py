"""Model for allowed names of materials for different asset types."""
from collections.abc import Iterable
from typing import Annotated, cast

from pydantic import BaseModel as PydanticBaseModel
from pydantic import (
    Field,
    ValidationError,
    create_model,
    field_validator,
)
from pydantic_core import ErrorDetails, PydanticCustomError

from readyplayerme.asset_validation_schemas.basemodel import get_model_config
from readyplayerme.asset_validation_schemas.fields import get_enum_field_definitions
from readyplayerme.asset_validation_schemas.types import create_enum_class
from readyplayerme.asset_validation_schemas.validators import CustomValidator, ErrorMsgReturnType

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

AllMaterialNames = create_enum_class("AllMaterialNames", material_names)

OutfitMaterialNames = create_enum_class("OutfitMaterialNames", material_names, {"bottom", "footwear", "top", "body"})

HeroAvatarMaterialNames = create_enum_class(
    "HeroAvatarMaterialNames",
    material_names,
    {"bottom", "footwear", "top", "body", "head", "eye", "teeth", "hair", "beard", "facewear", "glasses", "headwear"},
)


ERROR_CODE = "MATERIAL_NAME"
ERROR_MSG = "Material name should be {valid_value}. Found {value} instead."
ERROR_MSG_MULTI = "Material name should be one of {valid_values}. Found {value} instead."
DOCS_URL = "https://docs.readyplayer.me/asset-creation-guide/validation/validation-checks/"


def get_error_type_msg(field_name: str, error: ErrorDetails) -> ErrorMsgReturnType:
    """Convert the error to a custom error type and message.

    If the error type is not covered, return a None-tuple.
    """
    error_ctx = error.get("ctx", {})
    expected = error_ctx.get("expected")
    value = error.get("input")
    match field_name:
        case key if key in AllMaterialNames.__members__:
            return (
                ERROR_CODE,
                ERROR_MSG.format(valid_value=expected, value=value)
                + f"\n\tFor further information visit {DOCS_URL}.".expandtabs(4) * bool(DOCS_URL),
            )
        case "outfit":
            return (
                ERROR_CODE,
                ERROR_MSG_MULTI.format(valid_values=", ".join(cast(Iterable[str], OutfitMaterialNames)), value=value)
                + f"\n\tFor further information visit {DOCS_URL}.".expandtabs(4) * bool(DOCS_URL),
            )
        case key if key in ("hero_avatar", "heroAvatar"):
            return (
                ERROR_CODE,
                ERROR_MSG_MULTI.format(
                    valid_values=", ".join(cast(Iterable[str], HeroAvatarMaterialNames)), value=value
                )
                + f"\n\tFor further information visit {DOCS_URL}.".expandtabs(4) * bool(DOCS_URL),
            )
    return None, None


# Define fields for outfit assets and hero avatar assets.
outfit_field = Annotated[
    OutfitMaterialNames,  # type: ignore[valid-type]
    Field(
        json_schema_extra={
            "errorMessage": ERROR_MSG_MULTI.format(
                valid_values=", ".join(cast(Iterable[str], OutfitMaterialNames)), value="${0}"
            )
        }
    ),
]

hero_avatar_field = Annotated[
    HeroAvatarMaterialNames,  # type: ignore[valid-type]
    Field(
        json_schema_extra={
            "errorMessage": ERROR_MSG_MULTI.format(
                valid_values=", ".join(cast(Iterable[str], HeroAvatarMaterialNames)), value="${0}"
            )
        }
    ),
]

# Wrapped validator to use for custom error messages.
wrapped_validator = field_validator("*", mode="wrap")(CustomValidator(get_error_type_msg).custom_error_validator)

# We don't really have the need for a model, since we can use the defined fields directly in other schemas.
MaterialNamesModel: type[PydanticBaseModel] = create_model(
    "MaterialNames",
    __config__=get_model_config(title="Material Names"),
    __validators__={"*": wrapped_validator},
    **get_enum_field_definitions(AllMaterialNames, ERROR_MSG),
    outfit=(outfit_field, None),
    non_customizable_avatar=(hero_avatar_field, None),
)


if __name__ == "__main__":
    import logging

    from readyplayerme.asset_validation_schemas.schema_io import write_json

    logging.basicConfig(level=logging.DEBUG)
    # Convert model to JSON schema.
    write_json(MaterialNamesModel.model_json_schema())

    # Example of validation in Python.
    try:
        # Test example validation.
        MaterialNamesModel(beard="Wrong_Material_Name", outfit="Other_Wrong_Material_Name")
    except (PydanticCustomError, ValidationError, TypeError) as error:
        logging.error("\nValidation Errors:\n %s", error)
