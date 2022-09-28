import click

from application import Application
from installer import Installer

BOTH_INSTALL_UNINSTALL_MSG = "Cannot install and uninstall together."
APP_NOT_INSTALLED_MSG = (
    "It must be installed before running the application (see --help)."
)


@click.command()
@click.option(
    "--install",
    is_flag=True,
    show_default=True,
    default=False,
    help="Install the application.",
)
@click.option(
    "--uninstall",
    is_flag=True,
    show_default=True,
    default=False,
    help="Uninstall the application.",
)
def main(install: bool, uninstall: bool) -> None:
    if install and uninstall:
        click.secho(BOTH_INSTALL_UNINSTALL_MSG, fg="red", bold=True)
        return

    installer = Installer()
    if uninstall:
        return installer.uninstall()

    if install:
        return installer.install()

    if not installer.is_installed():
        click.secho(APP_NOT_INSTALLED_MSG, fg="red", bold=True)
        return

    app = Application()
    app.run()


if __name__ == "__main__":
    main()
