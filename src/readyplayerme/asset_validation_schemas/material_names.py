"""Model for allowed names of materials for different asset types."""
from collections.abc import Container, Iterable
from enum import Enum
from typing import Annotated, Any, Literal, cast

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


# Instead of spelling out members and values for each enum, create classes dynamically.
def create_enum_class(name: str, dictionary: dict[str, str], keys: Container[str] | None = None) -> Enum:
    """Create an string-enum class from a dictionary.

    If keys are provided, only the keys will be included in the enum class.
    """

    def is_key_set(item: tuple[str, str]) -> bool:
        return item[0] in keys if keys else True

    if keys is None:
        members = dictionary
    else:
        members = dict(filter(is_key_set, dictionary.items()))
    return Enum(name, members, type=str)


AllMaterialNames = create_enum_class("AllMaterialNames", material_names)

OutfitMaterialNames = create_enum_class("OutfitMaterialNames", material_names, {"bottom", "footwear", "top", "body"})

HeroAvatarMaterialNames = create_enum_class(
    "HeroAvatarMaterialNames",
    material_names,
    {"bottom", "footwear", "top", "body", "head", "eye", "teeth", "hair", "beard", "facewear", "glasses", "headwear"},
)


ERROR_CODE = "MATERIAL_NAME"
ERROR_MSG = "Material name should be {valid_name}. Found {value} instead."
ERROR_MSG_MULTI = "Material name should be one of {valid_names}. Found {value} instead."
DOCS_URL = "https://docs.readyplayer.me/asset-creation-guide/validation/validation-checks/"


def get_error_type_msg(field_name: str, value: Any) -> tuple[str, str] | tuple[None, None]:
    """Convert the error to a custom error type and message.

    If the error type is not covered, return a None-tuple.
    """
    match field_name:
        case key if key in AllMaterialNames.__members__:  # type: ignore[attr-defined]
            return (
                ERROR_CODE,
                ERROR_MSG.format(valid_name=getattr(AllMaterialNames, key).value, value=value)
                + f"\n\tFor further information visit {DOCS_URL}.".expandtabs(4) * bool(DOCS_URL),
            )
        case "outfit":
            return (
                ERROR_CODE,
                ERROR_MSG_MULTI.format(valid_names=", ".join(cast(Iterable[str], OutfitMaterialNames)), value=value)
                + f"\n\tFor further information visit {DOCS_URL}.".expandtabs(4) * bool(DOCS_URL),
            )
        case key if key in ("non_customizable_avatar", "nonCustomizableAvatar"):
            return (
                ERROR_CODE,
                ERROR_MSG_MULTI.format(valid_names=", ".join(cast(Iterable[str], HeroAvatarMaterialNames)), value=value)
                + f"\n\tFor further information visit {DOCS_URL}.".expandtabs(4) * bool(DOCS_URL),
            )
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


def get_const_str_field_type(const: str) -> Any:
    """Return a constant-string field type with custom error messages."""
    return Annotated[
        # While this is not really a Literal, since we illegally use a variable, it works as "const" in json schema.
        Literal[const],
        Field(json_schema_extra={"errorMessage": ERROR_MSG.format(valid_name=const, value="${0}")}),
    ]


def get_field_definitions(field_input: Enum) -> Any:
    """Turn a StrEnum into field types of string-constants."""
    return {
        member.name: (  # Tuple of (type definition, default value).
            get_const_str_field_type(member.value),
            None,  # Default value.
        )
        for member in field_input  # type: ignore[attr-defined]
    }


# Define fields for outfit assets and hero avatar assets.
outfit_field = Annotated[
    OutfitMaterialNames,  # type: ignore[valid-type]
    Field(
        json_schema_extra={
            "errorMessage": ERROR_MSG_MULTI.format(
                valid_names=", ".join(cast(Iterable[str], OutfitMaterialNames)), value="${0}"
            )
        }
    ),
]

hero_avatar_field = Annotated[
    HeroAvatarMaterialNames,  # type: ignore[valid-type]
    Field(
        json_schema_extra={
            "errorMessage": ERROR_MSG_MULTI.format(
                valid_names=", ".join(cast(Iterable[str], HeroAvatarMaterialNames)), value="${0}"
            )
        }
    ),
]

# Wrap all field validators in a custom error validator.
wrapped_validator = field_validator("*", mode="wrap")(custom_error_validator)

MaterialNamesModel: type[PydanticBaseModel] = create_model(
    "MaterialNames",
    __config__=get_model_config(title="Material Names"),
    __validators__={"*": wrapped_validator},  # type: ignore[dict-item]
    **get_field_definitions(AllMaterialNames),
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
