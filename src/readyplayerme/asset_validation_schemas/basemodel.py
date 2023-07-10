from typing import Any

from pydantic import BaseConfig, Extra
from pydantic import BaseModel as PydanticBaseModel


class SchemaConfig(BaseConfig):
    extra = Extra.forbid
    validate_assignment = True
    validate_all = True
    anystr_strip_whitespace = True

    @staticmethod
    def schema_extra(schema: dict[str, Any], model: type["PydanticBaseModel"]) -> None:
        # Add metaschema and id.
        schema |= {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            # Get the "outer" class name with a lower case first letter.
            "$id": f"{(name := model.__name__)[0].lower() + name[1:]}.schema.json",
        }
        # Remove "title" & "default" from properties.
        for prop in schema.get("properties", {}).values():
            prop.pop("title", None)
            prop.pop("default", None)


class BaseModel(PydanticBaseModel):
    """Global base class for all models."""

    class Config(SchemaConfig):
        ...
