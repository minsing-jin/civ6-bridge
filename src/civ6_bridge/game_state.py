"""Build GameState model trees from parsed dicts and provide query helpers."""

from civ6_bridge.models import (
    City,
    CultureState,
    GameState,
    Player,
    ReligionState,
    ScienceState,
    Treasury,
    Unit,
)


def _build_treasury(data: dict) -> Treasury:
    return Treasury(
        gold_balance=float(data.get("gold_balance", 0)),
        gold_yield=float(data.get("gold_yield", 0)),
        total_maintenance=float(data.get("total_maintenance", 0)),
    )


def _build_culture(data: dict) -> CultureState:
    return CultureState(progressing_civic=data.get("progressing_civic", ""))


def _build_religion(data: dict) -> ReligionState:
    return ReligionState(
        faith_balance=float(data.get("faith_balance", 0)),
        faith_yield=float(data.get("faith_yield", 0)),
    )


def _build_science(data: dict) -> ScienceState:
    return ScienceState(
        progressing_tech=data.get("progressing_tech", ""),
        science_yield=float(data.get("science_yield", 0)),
    )


def _build_city(data: dict) -> City:
    return City(
        id=int(data.get("id", 0)),
        name=data.get("name", ""),
        x=int(data.get("x", 0)),
        y=int(data.get("y", 0)),
        population=int(data.get("population", 0)),
        owner_id=int(data.get("owner_id", 0)),
        buildings=tuple(data.get("buildings", [])),
        districts=tuple(data.get("districts", [])),
    )


def _build_unit(data: dict) -> Unit:
    return Unit(
        id=int(data.get("id", 0)),
        type=data.get("type", ""),
        name=data.get("name", ""),
        x=int(data.get("x", 0)),
        y=int(data.get("y", 0)),
        owner_id=int(data.get("owner_id", 0)),
        moves_remaining=int(data.get("moves_remaining", 0)),
        max_moves=int(data.get("max_moves", 0)),
        combat=int(data.get("combat", 0)),
        ranged_combat=int(data.get("ranged_combat", 0)),
        range=int(data.get("range", 0)),
        base_moves=int(data.get("base_moves", 2)),
    )


def _build_player(data: dict) -> Player:
    return Player(
        id=int(data.get("id", 0)),
        is_alive=bool(data.get("is_alive", True)),
        is_human=bool(data.get("is_human", False)),
        civilization=data.get("civilization", ""),
        leader=data.get("leader", ""),
        treasury=_build_treasury(data.get("treasury", {})),
        culture=_build_culture(data.get("culture", {})),
        religion=_build_religion(data.get("religion", {})),
        science=_build_science(data.get("science", {})),
        cities=tuple(_build_city(c) for c in data.get("cities", [])),
        units=tuple(_build_unit(u) for u in data.get("units", [])),
    )


def from_dict(data: dict) -> GameState:
    """Convert a parsed JSON dict into a GameState model tree."""
    return GameState(
        version=int(data.get("version", 1)),
        turn=int(data.get("turn", 0)),
        players=tuple(_build_player(p) for p in data.get("players", [])),
    )


def get_human_player(state: GameState) -> Player | None:
    """Return the first human player, or None."""
    for player in state.players:
        if player.is_human:
            return player
    return None


def get_player_by_id(state: GameState, player_id: int) -> Player | None:
    """Return the player with the given ID, or None."""
    for player in state.players:
        if player.id == player_id:
            return player
    return None
