"""Tests for the Civ6Bridge facade class."""

from pathlib import Path

from civ6_bridge.civ6_bridge import Civ6Bridge


def test_get_current_state_from_fixture():
    """Test that Civ6Bridge can read a fixture log file."""
    log_path = Path(__file__).parent / "fixtures" / "sample_lua_log.txt"
    bridge = Civ6Bridge(log_path=log_path)
    state = bridge.get_current_state()
    assert state is not None
    assert state.turn == 2  # latest frame in the fixture
    assert len(state.players) == 1


def test_get_current_state_empty(tmp_path):
    """Test with a log file that has no frames."""
    empty_log = tmp_path / "Lua.log"
    empty_log.write_text("just some log lines\nno sentinel frames\n")
    bridge = Civ6Bridge(log_path=empty_log)
    state = bridge.get_current_state()
    assert state is None
