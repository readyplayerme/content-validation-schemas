"""Custom types and helper functions for creating types."""
from collections.abc import Container
from enum import Enum


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
