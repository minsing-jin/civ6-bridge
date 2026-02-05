"""Console script for civ6_bridge."""

import typer
from rich.console import Console

from civ6_bridge import utils

app = typer.Typer()
console = Console()


@app.command()
def main():
    """Console script for civ6_bridge."""
    console.print("Replace this message by putting your code into civ6_bridge.cli.main")
    console.print("See Typer documentation at https://typer.tiangolo.com/")
    utils.do_something_useful()


if __name__ == "__main__":
    app()
