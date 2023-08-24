"""Utilities to generate custom schemas and read/write JSON files."""
import inspect
import json
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, cast

from pydantic import BaseModel
from pydantic.json_schema import (
    DEFAULT_REF_TEMPLATE,
    DefsRef,
    GenerateJsonSchema,
    JsonSchemaKeyT,
    JsonSchemaMode,
    JsonSchemaValue,
)
from pydantic_core import CoreSchema, core_schema

if TYPE_CHECKING:
    from pydantic._internal._dataclasses import PydanticDataclass  # Didn't find another way of type hinting dataclass.

properties_comment = (
    "gltf-transform's inspect() creates a 'properties' object. Do not confuse with the 'properties' keyword."
)


def write_json(json_obj: Any, path: Path | None = None) -> None:
    """Write JSON file.

    If no path is provided, the file will be written to a .temp folder in the current working directory.
    The file will then have the name of the python file that called this function.

    :param json_obj: JSON object to write.
    :param path: Path to write the JSON file to.
    """
    if not path:
        Path(".temp").mkdir(exist_ok=True)
        try:
            file_name = json_obj["$id"]
        except (TypeError, KeyError):
            # Use caller's file name as a backup.
            file_name = Path(inspect.stack()[1].filename).with_suffix(".schema.json").name
        path = Path(".temp") / file_name
    with path.open("w", encoding="UTF-8") as target:  # type: ignore[union-attr] # We made sure path is set.
        json.dump(json_obj, target, indent=2)


class NoDirectInstantiation(type):
    """Metaclass to prevent direct instantiation of a class."""

    def __call__(cls, *args, **kwargs):
        msg = (
            f"{cls.__name__} cannot be instantiated directly. "
            "Use the with_keys class method instead to create a new class."
        )
        raise TypeError(msg)


class GenerateJsonSchemaWithoutKeys(GenerateJsonSchema):
    """Generator for a JSON schema without given keys."""

    _keys: ClassVar[list[str]] = []

    @classmethod
    def with_keys(cls, keys: list[str]) -> type["GenerateJsonSchemaWithoutKeys"]:
        """Return a new class with given keys."""
        return type(cls.__name__ + "".join(k.title() for k in keys), (cls,), {"_keys": keys})

    def generate(self, schema: CoreSchema, mode: JsonSchemaMode = "validation") -> JsonSchemaValue:
        _schema = super().generate(schema, mode)
        remove_keys(_schema, self._keys)
        return _schema

    def generate_definitions(
        self, inputs: Sequence[tuple[JsonSchemaKeyT, JsonSchemaMode, core_schema.CoreSchema]]
    ) -> tuple[dict[tuple[JsonSchemaKeyT, JsonSchemaMode], JsonSchemaValue], dict[DefsRef, JsonSchemaValue]]:
        json_schemas_map, defs = super().generate_definitions(inputs)
        remove_keys(cast(dict[str, Any], defs), self._keys)
        return json_schemas_map, defs


def remove_keys(dict_: dict[str, Any], keys: list[str]) -> None:
    """Remove given keywords from a dict and its nested dicts."""
    if isinstance(dict_, dict):
        for keyword in keys:
            dict_.pop(keyword, None)
        for prop in dict_.values():
            remove_keys(prop, keys)


def remove_keys_from_schema(schema: dict[str, Any], keys: list[str]) -> None:
    """Remove given keywords from properties of a schema."""
    for value in schema.get("$defs", {}).values():
        remove_keys(value, keys=keys)
    for value in schema.get("properties", {}).values():
        remove_keys(value, keys=keys)


def add_schema_id(schema: dict[str, Any], model: type["BaseModel"]) -> None:
    """Add the JSON schema id based on the model name to a schema."""
    schema["$id"] = f"{(name := model.__name__)[0].lower() + name[1:]}.schema.json"


def add_metaschema(schema: dict[str, Any], schema_generator: type[GenerateJsonSchema] = GenerateJsonSchema) -> None:
    """Add the JSON schema metaschema to a schema."""
    schema["$schema"] = schema_generator.schema_dialect


def json_schema_extra(schema: dict[str, Any], model: type["BaseModel"]) -> None:
    """Provide extra JSON schema properties."""
    # Add metaschema and id.
    add_metaschema(schema)
    add_schema_id(schema, model)
    # Remove "title" & "default" from properties.
    remove_keys_from_schema(schema, ["title", "default"])


def models_definitions_json_schema(
    models: Sequence[type[BaseModel] | type["PydanticDataclass"]],
    *,
    by_alias: bool = True,
    id_: str | None = None,
    title: str | None = None,
    description: str | None = None,
    ref_template: str = DEFAULT_REF_TEMPLATE,
    schema_generator: type[GenerateJsonSchema] = GenerateJsonSchema,
    mode: JsonSchemaMode = "validation",
) -> JsonSchemaValue:
    """Generate a JSON Schema for multiple models.

    Clone of pydantic's models_json_schema function with the following changes:
    Does only return the JSON schema definitions without the mapping.
    The mode is set for all models instead of individually.
    Includes the metaschema ($schema) and ID ($id) in the generated JSON Schema's top-level.

    :param models: A sequence of tuples of the form (model, mode).
    :param by_alias: Whether field aliases should be used as keys in the generated JSON Schema.
    :param id_: The $id of the generated JSON Schema.
    :param title: The title of the generated JSON Schema.
    :param description: The description of the generated JSON Schema.
    :param ref_template: The reference template to use for generating JSON Schema references.
    :param schema_generator: The schema generator to use for generating the JSON Schema.

    :return: A JSON schema containing all definitions along with the optional title and description keys.
    """
    instance = schema_generator(by_alias=by_alias, ref_template=ref_template)
    inputs = [(m, mode, m.__pydantic_core_schema__) for m in models]
    _, definitions = instance.generate_definitions(inputs)

    json_schema: dict[str, Any] = {}
    add_metaschema(json_schema, schema_generator)
    if id_:
        json_schema["$id"] = id_
    if title:
        json_schema["title"] = title
    if description:
        json_schema["description"] = description
    if definitions:
        json_schema["$defs"] = definitions

    return json_schema
