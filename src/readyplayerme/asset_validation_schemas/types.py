"""Custom types and helper functions for creating types."""
from collections.abc import Container, Sized
from enum import Enum
from typing import cast


class StrEnum(str, Enum):
    """Enum with string values.

    This is a workaround for Python 3.10 not yet supporting StrEnum.
    """

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return str.__repr__(self.value)


# Instead of spelling out members and values for each enum, create classes dynamically.
def create_enum_class(name: str, dictionary: dict[str, str], keys: Container[str] | None = None) -> StrEnum:
    """Create an string-enum class from a dictionary.

    If keys are provided, only the keys will be included in the enum class.
    """

    def is_key_set(item: tuple[str, str]) -> bool:
        return item[0] in keys if keys else True

    if keys is None:
        members = dictionary
    else:
        members = dict(filter(is_key_set, dictionary.items()))
    return StrEnum(name, members)  # type: ignore[call-overload]


def get_enum_length(enum: Enum) -> int:
    """Get the length of an enum."""
    return len(cast(Sized, enum))
