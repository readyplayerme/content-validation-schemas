"""Utilities to generate custom schemas and read/write JSON files."""
import inspect
import json
from pathlib import Path
from typing import Any


def write_json(json_obj: Any, path: Path | None = None) -> None:
    """Write JSON file.

    If no path is provided, the file will be written to a .temp folder in the current working directory.
    The file will then have the name of the python file that called this function.

    :param json_obj: JSON object to write.
    :param path: Path to write the JSON file to.
    """
    if not path:
        Path(".temp").mkdir(exist_ok=True)
        caller_filename = inspect.stack()[1].filename
        path = Path(".temp") / Path(caller_filename).with_suffix(".json").name
    with path.open("w", encoding="UTF-8") as target:
        json.dump(json_obj, target, indent=2)
