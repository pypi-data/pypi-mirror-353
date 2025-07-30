import subprocess
from pathlib import Path
from typing import List

import inquirer
import pyperclip
import typer
from rich import print
from rich.padding import Padding

from yaspin import yaspin
from yaspin.spinners import Spinners


def abort(s):
    header = color("Exiting... ", "red")
    message(header + s, padding="around")
    raise typer.Abort()


def message(the_message, padding=None, indent: int = 0):
    if indent:
        the_message = Padding.indent(the_message, indent)

    if padding == "around":
        the_message = Padding(the_message, pad=(1, 2, 1, 2))
    elif padding == "above":
        the_message = Padding(the_message, pad=(1, 2, 0, 2))
    elif padding == "below":
        the_message = Padding(the_message, pad=(0, 2, 1, 2))

    print(the_message)


def color(s, color):
    return f"[bold {color}]{s}[/]"


def cmd(args, message: str = "Running"):
    with yaspin(Spinners.aesthetic, text=f"{message} ...", color="yellow") as spinner:
        try:
            res = subprocess.run(args, check=True, capture_output=True, encoding="utf-8")
            spinner.ok("✅ ")
            return res
        except subprocess.CalledProcessError as e:
            if spinner:
                spinner.fail("💥 ")
            abort(f"Failed to list projects from GCS: {e}\n{e.stderr}")
            return
        except Exception as e:
            if spinner:
                spinner.fail("💥 ")
            abort(f"An unexpected error occurred listing GCS projects: {e}")
            return


def lines(cmd_result: str):
    return cmd_result.stdout.strip().split('\n')




def find_bucket(search_external_drives: bool = False) -> str:
    """Return its path"""
    paths = []

    # search on attached drives on Mac
    if Path("/Volumes").is_dir():
        attached = [d / "bucket" for d in Path("/Volumes").iterdir()]
        paths.extend(attached)

    # search on local machine
    paths.append(LOCAL)
    # Typical Windows paths
    paths.append(Path(r"D:\bucket"))
    paths.append(Path.home() / "Documents" / "bucket")  #C:\Users\gecko\Documents\bucket

    # narrow to those that are present
    paths = [d for d in paths if d.is_dir()]

    paths = [str(p) for p in paths]
    if not paths:
        abort("Can't find your bucket, where is it?")
    if len(paths) == 1:
        path = paths[0]
    else:
        path = inquirer.list_input("Which bucket?", choices=paths)

    return path


LOCAL = Path.home() / "Downloads" / "bucket"

BUCKET = "gs://gecko-chase-photogrammetry-dev"


def gs_path(kind: str, name: str, bucket: str = BUCKET):
    return f"{bucket}/{kind}/{name}"


def commands(argss: List[List[str]]) -> List[str]:
    """Given a list of, a list of command line args,
    stringify the args appropriate for typing into the command line, and return each
    """
    return [" ".join(args) for args in argss]


def copy_to_clipboard(s: str):
    try:
        pyperclip.copy(s)
        message(color("Command copied to clipboard!", "green"), padding="below")
    except pyperclip.PyperclipException as e:
        message(color(f"Error copying to clipboard: {e}", "red"), padding="below")



def gcs_ls_folders(path: str, message: str = "folders"):
    """Returns a list of folders in the given Google Cloud Storage path. 
    Provide an optional message which will be used like
      'Grabbing {message} ...' 
    e.g. 
      'Grabbing projects ...'
    """
    result = cmd(["gsutil", "ls", path], message=f"Grabbing {message}")
    result_lines = lines(result)
    folders = [
        line for line in result_lines
                if line.endswith('/') and line != path and Path(line).name != ""
            ]
    folders = sorted(list(set([Path(f).name for f in folders])))
    if not folders:
        abort(f"No {message} found in {path}. {result_lines}")
    return folders