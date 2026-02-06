"""Utility functions for civ6_bridge."""

from pathlib import Path

from civ6_bridge.constants import DEFAULT_LOG_PATHS
from civ6_bridge.exceptions import LogNotFoundError


def detect_log_path() -> Path:
    """Auto-detect the Civ6 Lua.log file location.

    Checks platform-specific default paths and returns the first one that exists.
    Raises LogNotFoundError if none are found.
    """
    for path in DEFAULT_LOG_PATHS:
        if path.exists():
            return path
    searched = "\n  ".join(str(p) for p in DEFAULT_LOG_PATHS)
    raise LogNotFoundError(f"Could not find Lua.log. Searched:\n  {searched}")
