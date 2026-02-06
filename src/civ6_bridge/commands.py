"""High-level command API for controlling Civ6 via FireTuner."""

from __future__ import annotations

from civ6_bridge.exceptions import TunerConnectionError
from civ6_bridge.tuner_client import TunerClient


class GameCommands:
    """Convenience wrapper that translates Python method calls into Lua commands."""

    def __init__(self, client: TunerClient):
        self._client = client

    def move_unit(self, player_id: int, unit_id: int, x: int, y: int) -> str:
        """Move a unit to the target tile."""
        lua = f"Game.AgentMoveUnit({player_id}, {unit_id}, {x}, {y})"
        return self._client.send_command(lua)

    def end_turn(self) -> str:
        """End the current player's turn."""
        return self._client.send_command("Game.AgentEndTurn()")

    def set_gold(self, player_id: int, amount: int) -> str:
        """Set a player's gold balance to an exact amount."""
        lua = f"Game.AgentSetGold({player_id}, {amount})"
        return self._client.send_command(lua)

    def add_gold(self, player_id: int, amount: int) -> str:
        """Add (or subtract) gold from a player's treasury."""
        lua = f"Game.AgentAddGold({player_id}, {amount})"
        return self._client.send_command(lua)

    def research_tech(self, player_id: int, tech_type: str) -> str:
        """Set the current research tech for a player."""
        lua = f'Game.AgentResearchTech({player_id}, "{tech_type}")'
        return self._client.send_command(lua)

    def produce_unit(self, city_id: int, player_id: int, unit_type: str) -> str:
        """Queue a unit for production in a city."""
        lua = f'Game.AgentProduceUnit({city_id}, {player_id}, "{unit_type}")'
        return self._client.send_command(lua)

    def ping(self) -> bool:
        """Check connectivity by sending a ping command."""
        try:
            result = self._client.send_command("Game.AgentPing()")
            return "PONG" in result
        except TunerConnectionError:
            return False
