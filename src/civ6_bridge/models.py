"""Frozen dataclasses representing Civ6 game state."""

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Treasury:
    gold_balance: float = 0.0
    gold_yield: float = 0.0
    total_maintenance: float = 0.0


@dataclass(frozen=True, slots=True)
class CultureState:
    progressing_civic: str = ""


@dataclass(frozen=True, slots=True)
class ReligionState:
    faith_balance: float = 0.0
    faith_yield: float = 0.0


@dataclass(frozen=True, slots=True)
class ScienceState:
    progressing_tech: str = ""
    science_yield: float = 0.0


@dataclass(frozen=True, slots=True)
class City:
    id: int = 0
    name: str = ""
    x: int = 0
    y: int = 0
    population: int = 0
    owner_id: int = 0
    buildings: tuple[str, ...] = ()
    districts: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Unit:
    id: int = 0
    type: str = ""
    name: str = ""
    x: int = 0
    y: int = 0
    owner_id: int = 0
    moves_remaining: int = 0
    max_moves: int = 0
    combat: int = 0
    ranged_combat: int = 0
    range: int = 0
    base_moves: int = 2


@dataclass(frozen=True, slots=True)
class Player:
    id: int = 0
    is_alive: bool = True
    is_human: bool = False
    civilization: str = ""
    leader: str = ""
    treasury: Treasury = field(default_factory=Treasury)
    culture: CultureState = field(default_factory=CultureState)
    religion: ReligionState = field(default_factory=ReligionState)
    science: ScienceState = field(default_factory=ScienceState)
    cities: tuple[City, ...] = ()
    units: tuple[Unit, ...] = ()


@dataclass(frozen=True, slots=True)
class GameState:
    version: int = 1
    turn: int = 0
    players: tuple[Player, ...] = ()
