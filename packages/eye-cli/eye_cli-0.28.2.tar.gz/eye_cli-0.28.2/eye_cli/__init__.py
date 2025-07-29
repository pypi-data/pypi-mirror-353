import warnings

import typer

# Here to ignore the warning from yaspin
# about running in Jupyter
# TODO make this a more specific ignore
warnings.filterwarnings("ignore", category=UserWarning)

from . import vms, dl, rc, hmm
from .move import move_cli
from .data import data

cli = typer.Typer(no_args_is_help=True)
cli.add_typer(data.app, name="data")
cli.add_typer(rc.app, name="rc")
cli.add_typer(vms.app, name="vms")
cli.add_typer(hmm.app, name="hmm")
cli.add_typer(dl.cli, name="dl")
cli.add_typer(move_cli, name="move")


__version__ = "0.28.2"


def version_callback(value: bool):
    if value:
        typer.echo(f"Eye CLI: {__version__}")
        raise typer.Exit()


@cli.callback()
def main(
    version: bool = typer.Option(
        None, "--version", callback=version_callback, is_eager=True
    ),
):
    # Do other global stuff, handle other global options here
    return
