import subprocess

import inquirer
import typer
from rich import print
from rich.padding import Padding

from eye_cli.util import color, cmd, lines

app = typer.Typer(no_args_is_help=True)


def message(s):
    print(Padding(s, 1))


@app.command()
def list():
    args = [
        "gcloud",
        "compute",
        "instances",
        "list",
        "--project",
        "fde-playground",
        "--format=table(name, zone, machineType, EXTERNAL_IP, status)",
        "--sort-by=name",
    ]
    for vm in get_vms(args):
        print(vm)


@app.command()
def running():
    args = [
        "gcloud",
        "compute",
        "instances",
        "list",
        "--project",
        "fde-playground",
        "--filter=status=RUNNING",
        "--format=table(name, zone, machineType, EXTERNAL_IP, status)",
        "--sort-by=name",
    ]
    for vm in get_vms(args):
        print(vm)


@app.command()
def start(keep_trying: bool = True, show_terminated: bool = False):

    message(f"{color("Which VMs should we start?", "blue")}")

    args = [
        "gcloud",
        "compute",
        "instances",
        "list",
        "--project",
        "fde-playground",
        "--format=table(name, status, zone, machineType)",
        "--sort-by=name",
    ]
    if not show_terminated:
        args.append("--filter=status=TERMINATED")

    vms = inquirer.checkbox("Which VMs?", choices=get_vms(args, header=False))

    # Get just name column
    vms = [vm.split()[0] for vm in vms]

    for vm in vms:
        uri = get_vm_uri(vm)

        try_again = True
        while try_again:
            message(f"{color("START", "green")} {vm}")
            try:
                start_vm(uri)
                try_again = False
            except (ValueError, subprocess.CalledProcessError):
                if not keep_trying:
                    try_again = False


def get_vms(args, header: bool = True):
    res = cmd(args, message="Grabbing vms")
    vms = lines(res)
    if not header:
        vms = vms[1:]
    return vms


@app.command()
def stop(show_all: bool = False):

    message(f"{color("Which VMs should we stop?", "blue")}")

    args = [
        "gcloud",
        "compute",
        "instances",
        "list",
        "--project",
        "fde-playground",
        "--format=table(name, status, zone, machineType)",
        "--sort-by=name",
    ]
    if not show_all:
        args.append("--filter=status=RUNNING")

    vms = inquirer.checkbox("Which VMs?", choices=get_vms(args, header=False))

    # Get just name column
    vms = [vm.split()[0] for vm in vms]

    for vm in vms:
        message(f"{color("STOP", "red")} {vm}")
        try:
            uri = get_vm_uri(vm)
            stop_vm(uri)
        except (ValueError, subprocess.CalledProcessError):
            pass


def start_vm(uri):
    res = cmd(["gcloud", "compute", "instances", "start", uri], message=f"Starting vm ({uri})")
    for line in res.stderr.split("\n"):
        if "external IP" in line:
            print(line)


def stop_vm(uri):
    cmd(["gcloud", "compute", "instances", "stop", uri], message=f"Stopping vm ({uri})")


def get_vm_uri(name):
    res = cmd(
        [
            "gcloud",
            "compute",
            "instances",
            "list",
            f"--filter=name:{name}",
            "--uri",
            "--project",
            "fde-playground",
        ], message=f"Getting URI for vm ({name})"
    )
    uri = lines(res)[0]
    if uri:
        return uri
    else:
        raise ValueError(f"Couldn't get URI for vm {name}")


if __name__ == "__main__":
    app()
