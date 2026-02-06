"""Console script for civ6_bridge."""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from civ6_bridge.constants import TUNER_HOST, TUNER_PORT
from civ6_bridge.exceptions import Civ6BridgeError, TunerConnectionError
from civ6_bridge.log_watcher import LogWatcher
from civ6_bridge.tuner_client import TunerClient

app = typer.Typer(help="Civ6 Bridge — read Civilization VI game state from Lua.log")
console = Console()


@app.command()
def status(
    log_path: str = typer.Option(None, "--log-path", "-l", help="Path to Lua.log (auto-detected if omitted)"),
):
    """Show the latest game state from Lua.log."""
    try:
        path = _resolve_path(log_path)
        watcher = LogWatcher(path)
        state = watcher.read_latest()
    except Civ6BridgeError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from e

    if state is None:
        console.print("[yellow]No game state frames found in the log.[/yellow]")
        raise typer.Exit(0)

    console.print(f"[bold]Turn {state.turn}[/bold]  (schema v{state.version})")
    console.print()

    for player in state.players:
        if not player.is_alive:
            continue
        human_tag = " [green](human)[/green]" if player.is_human else ""
        console.print(f"[bold]Player {player.id}[/bold]{human_tag} — {player.civilization} / {player.leader}")
        console.print(f"  Gold: {player.treasury.gold_balance:.0f} (+{player.treasury.gold_yield:.1f})")
        console.print(f"  Faith: {player.religion.faith_balance:.0f} (+{player.religion.faith_yield:.1f})")
        console.print(f"  Science yield: {player.science.science_yield:.1f}")
        console.print(f"  Researching: {player.science.progressing_tech or '—'}")
        console.print(f"  Civic: {player.culture.progressing_civic or '—'}")

        if player.cities:
            city_table = Table(title="Cities", show_lines=False)
            city_table.add_column("Name")
            city_table.add_column("Pop", justify="right")
            city_table.add_column("Location")
            city_table.add_column("Buildings")
            for city in player.cities:
                city_table.add_row(
                    city.name,
                    str(city.population),
                    f"({city.x},{city.y})",
                    ", ".join(city.buildings) if city.buildings else "—",
                )
            console.print(city_table)

        if player.units:
            unit_table = Table(title="Units", show_lines=False)
            unit_table.add_column("Type")
            unit_table.add_column("Location")
            unit_table.add_column("Moves")
            unit_table.add_column("Combat", justify="right")
            for unit in player.units:
                unit_table.add_row(
                    unit.type,
                    f"({unit.x},{unit.y})",
                    f"{unit.moves_remaining}/{unit.max_moves}",
                    str(unit.combat),
                )
            console.print(unit_table)

        console.print()


@app.command()
def watch(
    log_path: str = typer.Option(None, "--log-path", "-l", help="Path to Lua.log (auto-detected if omitted)"),
    poll: float = typer.Option(1.0, "--poll", "-p", help="Poll interval in seconds"),
):
    """Continuously watch Lua.log and print new game states."""
    try:
        path = _resolve_path(log_path)
        watcher = LogWatcher(path)
    except Civ6BridgeError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from e

    console.print(f"[dim]Watching {path} (poll every {poll}s, Ctrl+C to stop)…[/dim]")
    try:
        for state in watcher.watch(poll_interval=poll):
            console.print(f"[bold]Turn {state.turn}[/bold] — {len(state.players)} players")
    except KeyboardInterrupt:
        console.print("\n[dim]Stopped.[/dim]")


@app.command()
def send(
    lua_code: str = typer.Argument(..., help="Lua code to execute in the game"),
    host: str = typer.Option(TUNER_HOST, "--host", "-H", help="FireTuner host"),
    port: int = typer.Option(TUNER_PORT, "--port", "-P", help="FireTuner port"),
):
    """Send a raw Lua command to Civ6 via FireTuner."""
    client = TunerClient(host=host, port=port)
    try:
        result = client.send_command(lua_code)
        if result:
            console.print(result)
        else:
            console.print("[green]Command sent (no output).[/green]")
    except TunerConnectionError as e:
        console.print(f"[red]Connection error:[/red] {e}")
        raise typer.Exit(1) from e
    except Civ6BridgeError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1) from e


@app.command()
def ping(
    host: str = typer.Option(TUNER_HOST, "--host", "-H", help="FireTuner host"),
    port: int = typer.Option(TUNER_PORT, "--port", "-P", help="FireTuner port"),
):
    """Check if the FireTuner server is reachable."""
    client = TunerClient(host=host, port=port)
    if client.is_connected():
        console.print("[green]Connected to FireTuner.[/green]")
    else:
        console.print(f"[red]Cannot connect to FireTuner at {host}:{port}.[/red]")
        raise typer.Exit(1)


def _resolve_path(log_path: str | None) -> Path:
    if log_path is not None:
        return Path(log_path)
    from civ6_bridge.utils import detect_log_path

    return detect_log_path()


if __name__ == "__main__":
    app()
