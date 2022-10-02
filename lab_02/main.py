import click

from enigma import Enigma
from misc import (
    make_enigma_from_settings,
    make_new_rand_enigma,
    read_file,
    write_file,
    write_settings_file,
)


@click.command()
@click.option(
    "-file_path",
    default=None,
    help="Зашифровать файл",
)
@click.option(
    "--use_settings",
    is_flag=True,
    default=False,
    help="Получить сохраненные настройки",
)
def run(file_path: str | None, use_settings: str | None) -> None:
    if use_settings and not file_path:
        click.secho("Используется только вместе в -file_path", fg="red", bold=True)
        return

    enigma: Enigma
    if use_settings:
        enigma = make_enigma_from_settings(file_path)
    else:
        enigma = make_new_rand_enigma()

    write_settings_file(file_path, enigma.rotors, enigma.reflector)

    try:
        file_data: bytes = read_file(path=file_path, mode="rb")
    except FileNotFoundError:
        click.secho("Не удалось найти файл", fg="red", bold=True)
    else:
        cipher_text = b"".join([bytes([enigma.encrypt(letter)]) for letter in file_data])
        write_file(path=f"{file_path}__cipher.txt", data=cipher_text, mode="wb")
        click.secho("Успешно зашифровано!", fg="green", bold=True)


if __name__ == "__main__":
    run()
