import importlib.resources
import json
from typing import Any


def get_schema(tool_name: str = "monochromatic") -> Any:
    """Get the stored complete schema for monochromatic's settings."""
    assert tool_name == "monochromatic", "Only monochromatic is supported."

    pkg = "monochromatic.resources"
    fname = "monochromatic.schema.json"

    schema = importlib.resources.files(pkg).joinpath(fname)
    with schema.open(encoding="utf-8") as f:
        return json.load(f)
