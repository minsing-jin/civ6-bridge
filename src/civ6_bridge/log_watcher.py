"""LogWatcher — tails Lua.log and yields GameState objects."""

from __future__ import annotations

import time
from collections.abc import Generator
from pathlib import Path

from civ6_bridge.exceptions import LogNotFoundError, ParseError, SchemaVersionError
from civ6_bridge.game_state import from_dict
from civ6_bridge.log_parser import extract_frames, parse_frame
from civ6_bridge.models import GameState


class LogWatcher:
    """Watches a Lua.log file for sentinel-delimited game state frames.

    Usage:
        watcher = LogWatcher(Path("Lua.log"))

        # One-shot: get the latest state
        state = watcher.read_latest()

        # Continuous: yield new states as they appear
        for state in watcher.watch(poll_interval=1.0):
            print(state.turn)
    """

    def __init__(self, log_path: Path):
        if not log_path.exists():
            raise LogNotFoundError(f"Log file not found: {log_path}")
        self.log_path = log_path
        self._position: int = 0

    def read_latest(self) -> GameState | None:
        """Read the entire log file and return the last valid GameState, or None."""
        text = self.log_path.read_text(encoding="utf-8", errors="replace")
        frames = extract_frames(text)
        if not frames:
            return None
        # Parse from the end, return first valid frame
        for raw in reversed(frames):
            try:
                data = parse_frame(raw)
                return from_dict(data)
            except (ParseError, SchemaVersionError):
                continue
        return None

    def watch(self, poll_interval: float = 1.0) -> Generator[GameState, None, None]:
        """Yield GameState objects as new frames appear in the log.

        Handles file truncation (e.g., game restart) by resetting position.
        """
        self._position = self.log_path.stat().st_size

        while True:
            try:
                size = self.log_path.stat().st_size
            except FileNotFoundError:
                time.sleep(poll_interval)
                continue

            # Detect truncation
            if size < self._position:
                self._position = 0

            if size > self._position:
                with open(self.log_path, encoding="utf-8", errors="replace") as f:
                    f.seek(self._position)
                    new_text = f.read()
                    self._position = f.tell()

                frames = extract_frames(new_text)
                for raw in frames:
                    try:
                        data = parse_frame(raw)
                        yield from_dict(data)
                    except (ParseError, SchemaVersionError):
                        continue

            time.sleep(poll_interval)
