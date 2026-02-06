"""Civ6Bridge facade — high-level API for reading and controlling Civ6 game state."""

from __future__ import annotations

import threading
from collections.abc import Callable
from pathlib import Path

from civ6_bridge.commands import GameCommands
from civ6_bridge.constants import TUNER_HOST, TUNER_PORT
from civ6_bridge.log_watcher import LogWatcher
from civ6_bridge.models import GameState
from civ6_bridge.tuner_client import TunerClient
from civ6_bridge.utils import detect_log_path


class Civ6Bridge:
    """Main entry point for the civ6_bridge SDK.

    Usage:
        bridge = Civ6Bridge()              # auto-detect log path
        bridge = Civ6Bridge("/path/to/Lua.log")

        state = bridge.get_current_state()  # one-shot read
        print(state.turn, state.players)

        bridge.on_turn(lambda gs: print(f"Turn {gs.turn}"))
        bridge.stop()

        # Send commands via FireTuner
        bridge.send_command("print('hello')")
        bridge.commands.move_unit(0, 1, 10, 20)
    """

    def __init__(
        self,
        log_path: str | Path | None = None,
        tuner_host: str = TUNER_HOST,
        tuner_port: int = TUNER_PORT,
    ):
        if log_path is None:
            resolved = detect_log_path()
        else:
            resolved = Path(log_path)
        self._watcher = LogWatcher(resolved)
        self._stop_event = threading.Event()
        self._watch_thread: threading.Thread | None = None
        self._tuner = TunerClient(host=tuner_host, port=tuner_port)
        self.commands = GameCommands(self._tuner)

    def get_current_state(self) -> GameState | None:
        """Read the log file and return the latest GameState, or None."""
        return self._watcher.read_latest()

    def on_turn(self, callback: Callable[[GameState], None], poll_interval: float = 1.0) -> None:
        """Start a background thread that calls `callback` for each new GameState.

        Only one watcher thread is active at a time; calling again replaces the previous one.
        """
        self.stop()
        self._stop_event.clear()

        def _run() -> None:
            for state in self._watcher.watch(poll_interval=poll_interval):
                if self._stop_event.is_set():
                    break
                callback(state)

        self._watch_thread = threading.Thread(target=_run, daemon=True)
        self._watch_thread.start()

    def stop(self) -> None:
        """Stop the background watcher thread if running."""
        self._stop_event.set()
        if self._watch_thread is not None:
            self._watch_thread.join(timeout=5.0)
            self._watch_thread = None

    # -- FireTuner command methods --

    def send_command(self, lua_code: str, context: int = 0) -> str:
        """Send a raw Lua command via FireTuner and return the response."""
        return self._tuner.send_command(lua_code, context)

    def move_unit(self, player_id: int, unit_id: int, x: int, y: int) -> str:
        """Move a unit to the target tile."""
        return self.commands.move_unit(player_id, unit_id, x, y)

    def end_turn(self) -> str:
        """End the current player's turn."""
        return self.commands.end_turn()

    def set_gold(self, player_id: int, amount: int) -> str:
        """Set a player's gold balance."""
        return self.commands.set_gold(player_id, amount)

    def add_gold(self, player_id: int, amount: int) -> str:
        """Add gold to a player's treasury."""
        return self.commands.add_gold(player_id, amount)

    def ping(self) -> bool:
        """Check if the FireTuner server is reachable and responding."""
        return self.commands.ping()
