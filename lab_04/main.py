import time
from math import ceil

import click

from custom_rsa.client import Client
from custom_rsa.misc import (
    read_encrypted,
    read_original,
    read_signed,
    write_decrypted,
    write_encrypted,
    write_signed,
)
from custom_rsa.owner import Owner


@click.command()
@click.argument("filename", type=click.Path(exists=True))
@click.option(
    "--encrypt",
    is_flag=True,
    show_default=True,
    default=False,
    help="Encrypt data.",
)
@click.option(
    "--decrypt",
    is_flag=True,
    show_default=True,
    default=False,
    help="Decrypt data.",
)
@click.option(
    "--sign",
    is_flag=True,
    show_default=True,
    default=False,
    help="Sign data",
)
@click.option(
    "--verify",
    is_flag=True,
    show_default=True,
    default=False,
    help="Sign data",
)
def run(
    filename: str,
    encrypt: bool = False,
    decrypt: bool = False,
    sign: bool = False,
    verify: bool = False,
) -> None:
    t1 = time.time_ns()

    owner = Owner()
    client = Client(owner.public_key)
    nbits = ceil(owner.public_key.n.bit_length() / 8)

    name, ext = filename.split(".")

    if sign:
        buffer: bytes = read_original(name, ext)
        signed = owner.sign(buffer)
        write_signed(name, ext, signed, num_bytes=nbits)
    elif verify:
        buffer: bytes = read_original(name, ext)
        signed: list[int] = read_signed(name, ext, size=nbits)
        client.verify(buffer, signed)
    elif encrypt:
        buffer: bytes = read_original(name, ext)
        encrypted = client.encrypt(buffer)
        write_encrypted(name, ext, encrypted, num_bytes=nbits)
    elif decrypt:
        buffer: list[int] = read_encrypted(name, ext, size=nbits)
        write_decrypted(name, ext, owner.decrypt(buffer))

    else:
        click.secho("Must be choose at least one mode", fg="red")

    t2 = time.time_ns()
    t = (t2 - t1) / 1e6
    click.secho(f"Time: {t} ms.", fg="yellow")


if __name__ == "__main__":
    run()
