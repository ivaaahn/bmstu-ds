import os

import click

APP_INSTALLED_MSG = "The application was installed successfully."
APP_UNINSTALLED_MSG = "The application was uninstalled successfully."
APP_NOT_INSTALLED_YET_MSG = "The application is not installed yet."
APP_ALREADY_INSTALLED_MSG = "The application is already installed."


class Installer:
    _PATH_TO_MACHINE_KEY = "/var/lib/dbus/machine-id"
    _PATH_TO_INSTALL_KEY = f"{os.path.expanduser('~')}/.ds-lab01"

    def __init__(self) -> None:
        self._install_key: str | None = None
        self._machine_key: str | None = None

    @staticmethod
    def _read_key(path: str) -> str:
        with open(path) as f:
            key = f.read().strip()
        return key

    @staticmethod
    def _write_key(path: str, key: str) -> None:
        with open(path, "w") as f:
            f.write(key)

    def _read_machine_key(self) -> str:
        if not self._machine_key:
            self._machine_key = self._read_key(self._PATH_TO_MACHINE_KEY)
        return self._machine_key

    def _read_install_key(self) -> str:
        if not self._install_key:
            self._install_key = self._read_key(self._PATH_TO_INSTALL_KEY)
        return self._install_key

    def _save_install_key(self, key: str) -> None:
        self._write_key(self._PATH_TO_INSTALL_KEY, key)

    def _remove_install_key(self) -> None:
        os.system(f"rm {self._PATH_TO_INSTALL_KEY}")

    def install(self) -> None:
        if self.is_installed():
            click.secho(APP_ALREADY_INSTALLED_MSG, fg="green", bold=True)
            return

        machine_key = self._read_machine_key()
        self._save_install_key(machine_key)
        click.secho(APP_INSTALLED_MSG, fg="green", bold=True)

    def uninstall(self) -> None:
        if not self.is_installed():
            click.secho(APP_NOT_INSTALLED_YET_MSG, fg="red", bold=True)
            return

        self._remove_install_key()
        self._install_key = None
        click.secho(APP_UNINSTALLED_MSG, fg="green", bold=True)

    def is_installed(self) -> bool:
        try:
            install_key = self._read_install_key()
        except FileNotFoundError:
            return False

        machine_key = self._read_machine_key()
        return install_key == machine_key
