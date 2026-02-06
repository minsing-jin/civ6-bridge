"""Sentinel strings, default log paths, and schema version constants."""

import platform
from pathlib import Path

SENTINEL_BEGIN = "[CIV6BRIDGE_BEGIN_v1]"
SENTINEL_END = "[CIV6BRIDGE_END_v1]"
SCHEMA_VERSION = 1

# FireTuner TCP connection
TUNER_HOST = "127.0.0.1"
TUNER_PORT = 4318
TUNER_MSG_TYPE = 3

# Response sentinels for agent commands
RESULT_BEGIN = "CIV6BRIDGE_RESULT:"
RESULT_END = ":CIV6BRIDGE_END"


def _default_log_paths() -> list[Path]:
    """Return platform-specific candidate paths for Civ6's Lua.log."""
    system = platform.system()
    if system == "Windows":
        local = Path.home() / "AppData" / "Local"
        docs = Path.home() / "Documents" / "My Games" / "Sid Meier's Civilization VI" / "Logs" / "Lua.log"
        return [
            local / "Firaxis Games" / "Sid Meier's Civilization VI" / "Logs" / "Lua.log",
            docs,
        ]
    elif system == "Darwin":
        return [
            Path.home() / "Library" / "Application Support" / "Sid Meier's Civilization VI" / "Logs" / "Lua.log",
        ]
    else:
        # Linux (proton/wine)
        return [
            Path.home() / ".local" / "share" / "aspyr-media" / "Sid Meier's Civilization VI" / "Logs" / "Lua.log",
        ]


DEFAULT_LOG_PATHS = _default_log_paths()
