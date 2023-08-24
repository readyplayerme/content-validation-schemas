"""Provide a global base class and config for all Ready Player Me pydantic models."""
import abc
from typing import Any

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel

from readyplayerme.asset_validation_schemas.schema_io import json_schema_extra


def get_model_config(**kwargs: Any) -> ConfigDict:
    """Return a model config with some default values.

    :param kwargs: Arguments to pass to the model config to add or override default values.
    """
    default_dict = {
        "validate_assignment": True,
        "validate_default": False,
        "strict": False,  # Otherwise, enum values don't pass validation as strings.
        "populate_by_name": True,
        "use_enum_values": True,
        "extra": "forbid",
        "hide_input_in_errors": True,
        "alias_generator": to_camel,
        "str_strip_whitespace": False,
        "json_schema_extra": json_schema_extra,
        "frozen": True,
    }
    updated_dict = default_dict | kwargs
    return ConfigDict(**updated_dict)  # type: ignore[typeddict-item]


class BaseModel(PydanticBaseModel, abc.ABC):
    """Global base class for all models."""

    model_config = get_model_config(title="Base Model", defer_build=True)


if __name__ == "__main__":
    import json
    import logging

    logging.basicConfig(level=logging.DEBUG)

    # Convert model to JSON schema.
    logging.debug(json.dumps(BaseModel.model_json_schema(), indent=2))
