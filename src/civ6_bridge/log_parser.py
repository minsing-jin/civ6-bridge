"""Extract and parse sentinel-delimited JSON frames from Lua.log text."""

import json

from civ6_bridge.constants import SCHEMA_VERSION, SENTINEL_BEGIN, SENTINEL_END
from civ6_bridge.exceptions import ParseError, SchemaVersionError


def extract_frames(text: str) -> list[str]:
    """Find all complete BEGIN…END blocks in raw log text.

    Returns a list of JSON strings (one per frame).
    Incomplete (truncated) frames are silently skipped.
    """
    frames: list[str] = []
    start = 0
    while True:
        begin_idx = text.find(SENTINEL_BEGIN, start)
        if begin_idx == -1:
            break
        payload_start = begin_idx + len(SENTINEL_BEGIN)
        end_idx = text.find(SENTINEL_END, payload_start)
        if end_idx == -1:
            break  # truncated frame
        raw = text[payload_start:end_idx].strip()
        if raw:
            frames.append(raw)
        start = end_idx + len(SENTINEL_END)
    return frames


def parse_frame(raw: str) -> dict:
    """Parse a single JSON frame string and validate the schema version.

    Returns the parsed dict.
    Raises ParseError for invalid JSON, SchemaVersionError for version mismatch.
    """
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ParseError(f"Invalid JSON in frame: {e}") from e

    if not isinstance(data, dict):
        raise ParseError(f"Expected JSON object, got {type(data).__name__}")

    version = data.get("version")
    if version != SCHEMA_VERSION:
        raise SchemaVersionError(expected=SCHEMA_VERSION, got=version)

    return data
