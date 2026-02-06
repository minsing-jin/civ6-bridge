"""Tests for civ6_bridge.game_state — from_dict and query helpers."""

import json
from pathlib import Path

import pytest

from civ6_bridge.game_state import from_dict, get_human_player, get_player_by_id
from civ6_bridge.models import GameState


@pytest.fixture
def sample_data():
    fixture = Path(__file__).parent / "fixtures" / "sample_game_state.json"
    return json.loads(fixture.read_text())


class TestFromDict:
    def test_roundtrip(self, sample_data):
        state = from_dict(sample_data)
        assert isinstance(state, GameState)
        assert state.version == 1
        assert state.turn == 42
        assert len(state.players) == 2

    def test_player_fields(self, sample_data):
        state = from_dict(sample_data)
        human = state.players[0]
        assert human.id == 0
        assert human.is_alive is True
        assert human.is_human is True
        assert human.civilization == "CIVILIZATION_AMERICA"
        assert human.leader == "LEADER_TEDDY_ROOSEVELT"

    def test_treasury(self, sample_data):
        state = from_dict(sample_data)
        treasury = state.players[0].treasury
        assert treasury.gold_balance == 150.0
        assert treasury.gold_yield == 12.5
        assert treasury.total_maintenance == 8.0

    def test_science(self, sample_data):
        state = from_dict(sample_data)
        science = state.players[0].science
        assert science.progressing_tech == "TECH_MINING"
        assert science.science_yield == 5.0

    def test_culture(self, sample_data):
        state = from_dict(sample_data)
        culture = state.players[0].culture
        assert culture.progressing_civic == "CIVIC_CODE_OF_LAWS"

    def test_religion(self, sample_data):
        state = from_dict(sample_data)
        religion = state.players[0].religion
        assert religion.faith_balance == 20.0
        assert religion.faith_yield == 1.5

    def test_cities(self, sample_data):
        state = from_dict(sample_data)
        cities = state.players[0].cities
        assert len(cities) == 1
        city = cities[0]
        assert city.name == "Washington"
        assert city.x == 15
        assert city.y == 22
        assert city.population == 4
        assert city.buildings == ("BUILDING_MONUMENT",)
        assert city.districts == ()

    def test_units(self, sample_data):
        state = from_dict(sample_data)
        units = state.players[0].units
        assert len(units) == 1
        unit = units[0]
        assert unit.type == "UNIT_WARRIOR"
        assert unit.combat == 20
        assert unit.moves_remaining == 2

    def test_empty_dict(self):
        state = from_dict({"version": 1})
        assert state.version == 1
        assert state.turn == 0
        assert state.players == ()

    def test_missing_nested_fields(self):
        data = {"version": 1, "turn": 1, "players": [{"id": 0}]}
        state = from_dict(data)
        player = state.players[0]
        assert player.treasury.gold_balance == 0.0
        assert player.cities == ()
        assert player.units == ()


class TestQueryHelpers:
    def test_get_human_player(self, sample_data):
        state = from_dict(sample_data)
        human = get_human_player(state)
        assert human is not None
        assert human.is_human is True
        assert human.civilization == "CIVILIZATION_AMERICA"

    def test_get_human_player_none(self):
        state = GameState(players=())
        assert get_human_player(state) is None

    def test_get_player_by_id(self, sample_data):
        state = from_dict(sample_data)
        rome = get_player_by_id(state, 1)
        assert rome is not None
        assert rome.civilization == "CIVILIZATION_ROME"

    def test_get_player_by_id_missing(self, sample_data):
        state = from_dict(sample_data)
        assert get_player_by_id(state, 99) is None
