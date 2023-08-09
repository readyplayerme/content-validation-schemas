"""Provide a global base class and config for all Ready Player Me pydantic models."""
import abc
from typing import Any

from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict
from pydantic.alias_generators import to_camel
from pydantic.json_schema import GenerateJsonSchema


def add_metaschema(schema: dict[str, Any]) -> None:
    """Add the JSON schema metaschema to a schema."""
    schema["$schema"] = GenerateJsonSchema.schema_dialect


def add_schema_id(schema: dict[str, Any], model: type["PydanticBaseModel"]) -> None:
    """Add the JSON schema id based on the model name to a schema."""
    schema["$id"] = f"{(name := model.__name__)[0].lower() + name[1:]}.schema.json"


def remove_keywords_from_properties(schema: dict[str, Any], keywords: list[str]) -> None:
    """Remove given keywords from properties of a schema."""
    for prop in schema.get("properties", {}).values():
        for kw in keywords:
            prop.pop(kw, None)


def json_schema_extra(schema: dict[str, Any], model: type["PydanticBaseModel"]) -> None:
    """Provide extra JSON schema properties."""
    # Add metaschema and id.
    add_metaschema(schema)
    add_schema_id(schema, model)
    # Remove "title" & "default" from properties.
    remove_keywords_from_properties(schema, ["title", "default"])


def get_model_config(**kwargs: Any) -> ConfigDict:
    """Return a model config with some default values.

    :param kwargs: Arguments to pass to the model config to add or override default values.
    """
    default_dict = {
        "validate_assignment": True,
        "validate_default": False,
        "strict": True,
        "populate_by_name": True,
        "extra": "forbid",
        "hide_input_in_errors": True,
        "alias_generator": to_camel,
        "str_strip_whitespace": False,
        "json_schema_extra": json_schema_extra,
        "frozen": True,
    }
    updated_dict = default_dict | kwargs
    return ConfigDict(**updated_dict)  # type: ignore[misc]


class BaseModel(PydanticBaseModel, abc.ABC):
    """Global base class for all models."""

    model_config = get_model_config(title="Base Model", defer_build=True)


if __name__ == "__main__":
    import json
    import logging

    logging.basicConfig(level=logging.DEBUG)

    # Convert model to JSON schema.
    logging.debug(json.dumps(BaseModel.model_json_schema(), indent=2))
