"""Tests for civ6_bridge.models — construction, defaults, immutability."""

import pytest

from civ6_bridge.models import City, CultureState, GameState, Player, ReligionState, ScienceState, Treasury, Unit


class TestTreasury:
    def test_defaults(self):
        t = Treasury()
        assert t.gold_balance == 0.0
        assert t.gold_yield == 0.0
        assert t.total_maintenance == 0.0

    def test_construction(self):
        t = Treasury(gold_balance=100.0, gold_yield=10.5, total_maintenance=3.0)
        assert t.gold_balance == 100.0
        assert t.gold_yield == 10.5
        assert t.total_maintenance == 3.0

    def test_immutable(self):
        t = Treasury()
        with pytest.raises(AttributeError):
            t.gold_balance = 999


class TestCity:
    def test_defaults(self):
        c = City()
        assert c.buildings == ()
        assert c.districts == ()

    def test_construction(self):
        c = City(id=1, name="Washington", x=15, y=22, population=4, buildings=("BUILDING_MONUMENT",))
        assert c.name == "Washington"
        assert c.buildings == ("BUILDING_MONUMENT",)

    def test_immutable(self):
        c = City(name="Test")
        with pytest.raises(AttributeError):
            c.name = "Changed"


class TestUnit:
    def test_defaults(self):
        u = Unit()
        assert u.base_moves == 2
        assert u.combat == 0

    def test_construction(self):
        u = Unit(id=0, type="UNIT_WARRIOR", name="Warrior", combat=20)
        assert u.type == "UNIT_WARRIOR"
        assert u.combat == 20


class TestPlayer:
    def test_defaults(self):
        p = Player()
        assert p.is_alive is True
        assert p.is_human is False
        assert p.cities == ()
        assert p.units == ()
        assert isinstance(p.treasury, Treasury)
        assert isinstance(p.culture, CultureState)
        assert isinstance(p.religion, ReligionState)
        assert isinstance(p.science, ScienceState)

    def test_construction_with_children(self):
        city = City(name="Rome")
        unit = Unit(type="UNIT_WARRIOR")
        p = Player(id=1, cities=(city,), units=(unit,))
        assert len(p.cities) == 1
        assert p.cities[0].name == "Rome"
        assert len(p.units) == 1


class TestGameState:
    def test_defaults(self):
        gs = GameState()
        assert gs.version == 1
        assert gs.turn == 0
        assert gs.players == ()

    def test_construction(self):
        p = Player(id=0, is_human=True)
        gs = GameState(version=1, turn=42, players=(p,))
        assert gs.turn == 42
        assert len(gs.players) == 1
        assert gs.players[0].is_human is True

    def test_immutable(self):
        gs = GameState()
        with pytest.raises(AttributeError):
            gs.turn = 99
