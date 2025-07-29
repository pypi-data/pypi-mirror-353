import time
from typing import Literal

import typer

from kds_sms_server.statics.ascii_logo import ASCII_LOGO
from kds_sms_server.console import console
from kds_sms_server.settings import settings

cli_app = typer.Typer()


def print_header(mode: Literal["info", "server", "worker", "cli"]):
    first_line = f"Starting {settings.branding.title}"
    if mode == "info":
        first_line += " ..."
    elif mode == "server":
        first_line += " - Server ..."
    elif mode == "worker":
        first_line += " - Worker ..."
    elif mode == "cli":
        first_line += " - CLI ..."
    console.print(first_line)
    console.print(ASCII_LOGO)
    console.print("_________________________________________________________________________________\n")
    console.print(f"{settings.branding.description}")
    console.print(f"by {settings.branding.author}({settings.branding.author_email})")
    console.print(f"version: {settings.branding.version}")
    console.print(f"License: {settings.branding.license}")
    console.print("_________________________________________________________________________________")


def main_loop(mode: Literal["server", "worker"]):
    console.print(f"{settings.branding.title} - {mode.capitalize()} is ready. Press CTRL+C to quit.")
    try:
        while True:
            time.sleep(0.001)
    except KeyboardInterrupt:
        console.print(f"KeyboardInterrupt received. Stopping {settings.branding.title} - {mode.capitalize()} ...")


@cli_app.command(name="version", help=f"Show the version of {settings.branding.title}.")
def version_command() -> None:
    """
    Show the version of KDSM Manager.

    :return: None
    """

    # print header
    print_header(mode="info")


@cli_app.command(name="listener", help=f"Start the {settings.branding.title} - listener.")
def listener_command():
    """
    Start the server.

    :return: None
    """

    from kds_sms_server.db import db
    from kds_sms_server.listener import SmsListener

    # print header
    print_header(mode="server")

    # init db
    db().create_all()

    # start listener
    SmsListener()

    # entering main loop
    main_loop(mode="server")


@cli_app.command(name="worker", help=f"Start the {settings.branding.title} - worker.")
def worker_command():
    """
    Start the worker.

    :return: None
    """

    from kds_sms_server.db import db
    from kds_sms_server.worker import SmsWorker

    # print header
    print_header(mode="server")

    # init db
    db().create_all()

    # start worker
    SmsWorker()

    # entering main loop
    main_loop(mode="server")


@cli_app.command(name="init-db", help="Initialize database.")
def init_db_command():
    """
    Initialize database.
    :return: None
    """

    from kds_sms_server.db import db

    # print header
    print_header(mode="server")

    # init db
    console.print("Initializing database ...")
    db().create_all()
    console.print("Initializing database ... done")
