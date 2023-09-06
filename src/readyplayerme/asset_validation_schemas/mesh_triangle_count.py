"""Triangle count validation pydantic model."""
from typing import Annotated, Any

from pydantic import BaseModel as PydanticBaseModel
from pydantic import (
    Field,
    ValidationError,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    create_model,
)
from pydantic.functional_validators import WrapValidator
from pydantic_core import ErrorDetails, InitErrorDetails, PydanticCustomError

from readyplayerme.asset_validation_schemas.basemodel import get_model_config

ERROR_CODE = "TRIANGLE_COUNT"
DOCS_URL = (
    "https://docs.readyplayer.me/asset-creation-guide/validation/validation-checks/"
    "mesh-validations/check-mesh-triangle-count"
)

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
    "head_custom": 6000,
    "headwear": 2500,
    "outfit_bottom": 6000,
    "outfit_top": 6000,
    "outfit_footwear": 2000,
    "halfbody_shirt": 1000,
    "teeth": 1000,
}


def convert_error(error: ErrorDetails, title: str = "Unknown Error", url: str = ""):
    """Convert the error to a PydanticCustomError with a custom error type and message."""
    match error:
        case {"type": "greater_than"}:
            raise PydanticCustomError(
                ERROR_CODE,
                "Mesh must have at least 1 triangle."
                # Include the URL if it's not empty. Indent by tab (4 spaces).
                + "\n\tFor further information visit {url}.".expandtabs(4) * bool(url),
                {"url": url},
            )
        case {"type": "less_than_equal"}:
            raise PydanticCustomError(
                ERROR_CODE,
                "Mesh exceeds triangle count budget. Allowed: {limit}. Found: {wrong_value}."
                + "\n\tFor further information visit {url}.".expandtabs(4) * bool(url),
                {"limit": error["ctx"]["le"], "wrong_value": error["input"], "url": url},
            )
        case _:  # Anything else raise ValidationError.
            # Convert ErrorDetails to InitErrorDetails
            ctx = error.get("ctx", {})
            init_error_details: InitErrorDetails = InitErrorDetails(
                type=error["type"],
                loc=error["loc"],
                input=error["input"],
                ctx=ctx,
            )
            raise ValidationError.from_exception_data(title=title, line_errors=[init_error_details])


def validate_tricount(value: Any, handler: ValidatorFunctionWrapHandler, _info: ValidationInfo) -> int:
    """Wrap the validation function to raise custom error types.

    Return the validated value if no error occurred.
    """
    try:
        return handler(value)
    except ValidationError as error:
        for err in error.errors():
            convert_error(err, title=error.title, url=DOCS_URL)
        return value  # This line is unreachable, but makes type-checkers happy.


def get_triangle_count_type(le: int) -> Annotated:
    """Return a constrained positive integer field type with custom error messages.

    :param le: The (inclusive) maximum of the integer (less-equal).
    """
    return Annotated[
        int,
        Field(
            gt=0,
            le=le,
            json_schema_extra={
                "errorMessage": {
                    "exclusiveMinimum": "Mesh ${1/name} must have at least 1 triangle.",
                    # Use % formatting for error message instead of f-string, since we need to preserve "${0}".
                    "maximum": "Mesh ${1/name} exceeds triangle count budget. Allowed: %d. Found: ${0}." % le,
                }
            },
        ),
        WrapValidator(validate_tricount),
    ]


def get_tricount_field_definitions(limits: dict[str, int]) -> Any:
    """Turn simple integer limits into a dict of constrained positive integer field types with custom error messages."""
    return {
        field_name: (  # Tuple of (type definition, default value).
            get_triangle_count_type(limit),
            None,  # Default value.
        )
        for field_name, limit in limits.items()
    }


# Dynamically create the model with the tri-count limits we defined earlier.
MeshTriangleCountModel: type[PydanticBaseModel] = create_model(
    "MeshTriangleCount",
    __config__=get_model_config(title="Triangle Count", validate_default=False),
    # Populate the fields.
    **get_tricount_field_definitions(limits),
)


if __name__ == "__main__":
    import json
    import logging

    logging.basicConfig(level=logging.DEBUG)
    # Convert model to JSON schema.
    logging.debug(json.dumps(MeshTriangleCountModel.model_json_schema(), indent=2))

    # Example of validation in Python.
    try:
        # Multiple checks at once. Test non-existent field as well.
        MeshTriangleCountModel(outfitBottom=6000, outfitTop=0, outfitFootwear=3000, foo=10)
    except (PydanticCustomError, ValidationError, TypeError) as error:
        logging.error("\nValidation Errors:\n %s", error)
