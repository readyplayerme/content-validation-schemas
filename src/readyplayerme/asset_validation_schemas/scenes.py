"""Validation models for properties of Scenes."""
from pydantic import Field

from readyplayerme.asset_validation_schemas.basemodel import BaseModel


class SceneProperties(BaseModel):
    """Validation schema for Scenes."""

    name: str
    root_name: str
    bbox_min: tuple[float, float, float] = Field(..., min_items=3, max_items=3)
    bbox_max: tuple[float, float, float] = Field(..., min_items=3, max_items=3)


if __name__ == "__main__":
    import logging

    from readyplayerme.asset_validation_schemas.schema_io import write_json

    logging.basicConfig(encoding="utf-8", level=logging.DEBUG)
    # Convert model to JSON schema.
    write_json(SceneProperties.model_json_schema())
