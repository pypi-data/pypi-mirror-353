# eye_cli/move/export.py
import subprocess
from pathlib import Path
from typing import Tuple

import inquirer
import typer
import pyperclip

from eye_cli.util import copy_to_clipboard, message, color, abort, LOCAL, BUCKET, find_bucket
from eye_cli.util import gcs_ls_folders

RC_EXPORT = "rc-export"

export_cli = typer.Typer(
    name="export", 
    no_args_is_help=True, 
    help="Prepares gsutil rsync commands for uploading or downloading export data to/from GCS."
)

def _select_or_create_dir(base_path: Path, prompt_message: str, new_dir_prompt_message: str, allow_creation: bool = True) -> Tuple[Path, bool]:
    """Helper function to list subdirectories or allow creation. Returns (selected_path, was_newly_created)."""
    was_newly_created = False
    if not base_path.exists(): 
        base_path.mkdir(parents=True, exist_ok=True)

    existing_dirs = sorted([d.name for d in base_path.iterdir() if d.is_dir()])
    
    choices = existing_dirs
    NEW_DIR_OPTION = "[Create New Folder]"

    if allow_creation:
        choices.append(NEW_DIR_OPTION)

    if not choices: 
        if allow_creation: 
             message(f"No existing folders found in {base_path}. You will be prompted to create one.", padding="above")
             selected_name = NEW_DIR_OPTION
        else: 
            abort(f"No folders found in {base_path} and creation is not enabled.")
    elif not existing_dirs and not allow_creation:
         abort(f"No folders found in {base_path} and creation is not allowed for this step.")
    else:
        selected_name = inquirer.list_input(prompt_message, choices=choices)

    if not selected_name:
        abort("Selection cancelled.")

    if allow_creation and selected_name == NEW_DIR_OPTION:
        new_name = inquirer.text(message=new_dir_prompt_message)
        if not new_name:
            abort("Folder name cannot be empty.")
        selected_path = base_path / new_name
        if not selected_path.exists():
            selected_path.mkdir(parents=True, exist_ok=True)
            message(f"Created new folder: {selected_path}", padding="below")
            was_newly_created = True
        else:
            message(f"Using existing folder: {selected_path}", padding="below")
        return selected_path, was_newly_created
    else:
        selected_path = base_path / selected_name
        message(f"Selected existing folder: {selected_path}", padding="below")
        return selected_path, False

@export_cli.command(name="up")
def export_up(dryrun: bool = typer.Option(True, help="Dryrun or actually move files. Works by setting gsutil's dry-run (-n) mode. ")):
    """Interactively selects a local export directory and prepares gsutil rsync command for upload."""
    message(color("Prepare Export Upload Command", "yellow"), padding="around")
    
    if dryrun:
        message(color("Preview Mode: -n (dry-run) will be added to the command.", "magenta"), padding="below")
    else:
        message(color("Live Mode: -n (dry-run) will NOT be added. Actual data transfer will occur.", "red"), padding="below")

    base_dir_str = find_bucket(search_external_drives=True)
    base_dir = Path(base_dir_str)
    message(f"Using base directory: {base_dir}", padding="below")

    projects_root_path = base_dir / "projects"
    if not projects_root_path.is_dir():
        projects_root_path.mkdir(parents=True, exist_ok=True)
        message(f"Created 'projects' directory in {base_dir}", padding="below")
    
    project_path_local, _ = _select_or_create_dir(
        base_path=projects_root_path,
        prompt_message="Select Project or create new:",
        new_dir_prompt_message="Enter name for the new Project folder:"
    )
    selected_project_name = project_path_local.name

    rc_export_folder_name_fixed = "rc-export"
    rc_export_base_path_local = project_path_local / rc_export_folder_name_fixed
    
    if not rc_export_base_path_local.exists():
        message(f"'{rc_export_folder_name_fixed}' directory not found in {project_path_local}. Creating it...", padding="above")
        rc_export_base_path_local.mkdir(parents=True, exist_ok=True)
        message(f"Created '{rc_export_folder_name_fixed}' directory at: {rc_export_base_path_local}", padding="below")
    elif not rc_export_base_path_local.is_dir():
        abort(f"A file exists at {rc_export_base_path_local} but a directory named '{rc_export_folder_name_fixed}' is required.")
    else:
        message(f"Using existing '{rc_export_folder_name_fixed}' directory: {rc_export_base_path_local}", padding="below")

    subtype_path_local, _ = _select_or_create_dir(
        base_path=rc_export_base_path_local,
        prompt_message="Select Export Subtype (e.g., alignment, mesh) or create new:",
        new_dir_prompt_message="Enter name for the new Export Subtype folder (e.g., alignment, mesh):"
    )
    selected_export_subtype_name = subtype_path_local.name

    specific_export_path_local, was_specific_export_newly_created = _select_or_create_dir(
        base_path=subtype_path_local,
        prompt_message="Select Specific Export folder (e.g., run_01, final_output) or create new:",
        new_dir_prompt_message="Enter name for the new Specific Export folder (e.g., run_01, final_output):"
    )
    selected_specific_export_name = specific_export_path_local.name
    
    local_path = specific_export_path_local 

    if was_specific_export_newly_created and not list(local_path.iterdir()): 
        message(color("Important:", "yellow") + f" The new export folder {local_path} is empty. Please add files to upload into it if this is a new export.", padding="below")

    project_name_gcs = selected_project_name
    export_category_on_gcs = "rc-export" 
    export_subtype_on_gcs = selected_export_subtype_name
    specific_export_name_on_gcs = selected_specific_export_name
    
    gcs_destination_full = f"{BUCKET}/projects/{project_name_gcs}/{export_category_on_gcs}/{export_subtype_on_gcs}/{specific_export_name_on_gcs}/"

    message(f"Local source:     {local_path}", padding="above")
    message(f"GCS destination:  {gcs_destination_full}")

    if not list(local_path.iterdir()):
        message(color("Warning:", "yellow") + f" The local source directory {local_path} is empty.", padding="around")

    gsutil_args = ["gsutil", "-m", "rsync"]
    if dryrun:
        gsutil_args.append("-n")
    gsutil_args.append("-r") # Add -r for recursive rsync
    
    quoted_local_path = f'"{str(local_path)}"'
    quoted_gcs_destination = f'"{gcs_destination_full}"'
    
    gsutil_args.extend([quoted_local_path, quoted_gcs_destination])
    command_string = " ".join(gsutil_args)

    message(color("Command to run:", "cyan"), padding="above")
    print(command_string)

    try:
        pyperclip.copy(command_string)
        message(color("Command copied to clipboard!", "green"), padding="below")
    except pyperclip.PyperclipException as e:
        message(color(f"Error copying to clipboard: {e}", "red"), padding="below")


@export_cli.command(name="down")
def export_down(dryrun: bool = typer.Option(True, help="Dryrun or actually move files. Works by setting gsutil's dry-run (-n) mode. ")):
    """Interactively selects a GCS export and prepares gsutil rsync command for download."""
    message(color("Prepare Export Download Command", "yellow"), padding="around")
    if dryrun:
        message(color("Dryrun Mode: -n will be added to the command.", "magenta"), padding="below")
    else:
        message(color("Live Mode: -n will NOT be added. Actual data transfer will occur.", "red"), padding="below")

    projects_base_path_gcs = f"{BUCKET}/projects/"
    project_names = gcs_ls_folders(projects_base_path_gcs, "projects")
    project_name = inquirer.list_input("Select GCS Project:", choices=project_names)

    export_type_base_path = f"{BUCKET}/projects/{project_name}/{RC_EXPORT}/"
    export_types = gcs_ls_folders(export_type_base_path, "export types")
    export_type = inquirer.list_input("Select Export Type:", choices=export_types)

    specific_export_base_path = f"{BUCKET}/projects/{project_name}/{RC_EXPORT}/{export_type}/"
    specific_exports = gcs_ls_folders(specific_export_base_path, "specific exports")
    specific_export = inquirer.list_input("Select Specific Export to download:", choices=specific_exports)

    gcs_source_full = f"{specific_export_base_path}{specific_export}"

    default_local_dir_name = Path(LOCAL) / "projects" / project_name / RC_EXPORT / export_type
    local_destination_path = default_local_dir_name / specific_export

    if not local_destination_path.exists():
        local_destination_path.mkdir(parents=True, exist_ok=True)

    message(f"GCS source:             {gcs_source_full}")
    message(f"Local destination:      {local_destination_path}")

    gsutil_download_args = ["gsutil", "-m", "rsync"]
    if dryrun:
        gsutil_download_args.append("-n")
    gsutil_download_args.append("-r") # Add -r for recursive rsync
        
    quoted_gcs_source = f'"{gcs_source_full}"'
    quoted_local_destination = f'"{str(local_destination_path)}"'

    gsutil_download_args.extend([quoted_gcs_source, quoted_local_destination])
    command_string_download = " ".join(gsutil_download_args)

    message(color("Command to run:", "cyan"), padding="above")
    print(command_string_download)

    copy_to_clipboard(command_string_download)
