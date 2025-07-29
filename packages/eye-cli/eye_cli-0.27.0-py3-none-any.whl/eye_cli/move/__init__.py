# eye_cli/move/__init__.py
import typer

# Changed from .rc_export import rc_export_cli
from .export import export_cli 

# Renamed 'move' to 'move_app'
move_cli = typer.Typer(
    name="move", 
    no_args_is_help=True, 
    help="Move data, such as exports, to/from GCS."
)

# Changed name from "rc-export" to "export"
move_cli.add_typer(export_cli, name="export") 