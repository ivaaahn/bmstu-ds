import click

from .keygen import PublicKey
from .calculations import hasher, pow_in_executor


class Client:
    def __init__(self, public_key: PublicKey) -> None:
        self._public_key = public_key

    def encrypt(self, data: bytes) -> list[int]:
        click.secho("Encrypting...", fg="green")

        n, e = self._public_key
        res = pow_in_executor(data, e, n)

        click.secho("Encrypted.", fg="green")
        return res

    def verify(self, data: bytes, signed: list[int]) -> bool:
        click.secho("Verifying...", fg="green")

        n, u = self._public_key
        hash_original = bytes(pow_in_executor(signed, u, n))

        if hasher(data) == hash_original:
            click.secho("Verified.", fg="green")
            return True

        click.secho("Not verified.", fg="red")
        return False
