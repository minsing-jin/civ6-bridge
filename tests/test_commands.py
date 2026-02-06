"""Tests for the GameCommands high-level API."""

from unittest.mock import MagicMock

from civ6_bridge.commands import GameCommands
from civ6_bridge.exceptions import TunerConnectionError


class TestGameCommands:
    def setup_method(self):
        self.mock_client = MagicMock()
        self.commands = GameCommands(self.mock_client)

    def test_move_unit(self):
        self.commands.move_unit(0, 1, 10, 20)
        self.mock_client.send_command.assert_called_once_with("Game.AgentMoveUnit(0, 1, 10, 20)")

    def test_end_turn(self):
        self.commands.end_turn()
        self.mock_client.send_command.assert_called_once_with("Game.AgentEndTurn()")

    def test_set_gold(self):
        self.commands.set_gold(0, 500)
        self.mock_client.send_command.assert_called_once_with("Game.AgentSetGold(0, 500)")

    def test_add_gold(self):
        self.commands.add_gold(1, -100)
        self.mock_client.send_command.assert_called_once_with("Game.AgentAddGold(1, -100)")

    def test_research_tech(self):
        self.commands.research_tech(0, "TECH_POTTERY")
        self.mock_client.send_command.assert_called_once_with('Game.AgentResearchTech(0, "TECH_POTTERY")')

    def test_produce_unit(self):
        self.commands.produce_unit(1, 0, "UNIT_WARRIOR")
        self.mock_client.send_command.assert_called_once_with('Game.AgentProduceUnit(1, 0, "UNIT_WARRIOR")')

    def test_ping_success(self):
        self.mock_client.send_command.return_value = "PONG"
        assert self.commands.ping() is True
        self.mock_client.send_command.assert_called_once_with("Game.AgentPing()")

    def test_ping_connection_error(self):
        self.mock_client.send_command.side_effect = TunerConnectionError("fail")
        assert self.commands.ping() is False

    def test_ping_no_pong(self):
        self.mock_client.send_command.return_value = "something else"
        assert self.commands.ping() is False
