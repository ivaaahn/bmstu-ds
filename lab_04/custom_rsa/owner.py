import click

from .keygen import KeyGenRSA, PrivateKey, PublicKey
from .calculations import hasher, pow_in_executor


class Owner:
    def __init__(self) -> None:
        keygen = KeyGenRSA()
        keygen.generate()
        self._private_key = keygen.private
        self._public_key = keygen.public

    @property
    def public_key(self) -> PublicKey:
        return self._public_key

    @property
    def private_key(self) -> PrivateKey:
        return self._private_key

    def decrypt(self, data: list[int]) -> list[int]:
        click.secho("Decrypting...", fg="green")

        n, d = self._private_key
        res = pow_in_executor(data, d, n)

        click.secho("Decrypted.", fg="green")
        return res

    def sign(self, data: bytes) -> list[int]:
        click.secho("Signing...", fg="green")
        hashed = hasher(data)

        n, s = self._private_key
        res = pow_in_executor(hashed, s, n)

        click.secho("Signed.", fg="green")
        return res
