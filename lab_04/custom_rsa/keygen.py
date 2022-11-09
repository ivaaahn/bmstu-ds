import math
from random import randint, randrange
from typing import NamedTuple

import click

from base64 import b64decode, b64encode


class PrivateKey(NamedTuple):
    n: int
    d: int

    def __bytes__(self) -> bytes:
        return b64encode(f"{self.n};{self.d}".encode())

    @classmethod
    def from_bytes(cls, data: bytes) -> "PrivateKey":
        return PrivateKey(
            *tuple(map(int, b64decode(data).decode().strip().split(";")))
        )


class PublicKey(NamedTuple):
    n: int
    e: int

    def __bytes__(self) -> bytes:
        return b64encode(f"{self.n};{self.e}".encode())

    @classmethod
    def from_bytes(cls, data: bytes) -> "PublicKey":
        return PublicKey(
            *tuple(map(int, b64decode(data).decode().strip().split(";")))
        )


class KeyGenRSA:
    _PUBLIC_KEY_NAME = ".rsa/public.key"
    _PRIVATE_KEY_NAME = ".rsa/private.key"

    def __init__(self, nbits: int = 16) -> None:
        self._p = None
        self._q = None
        self._public = None
        self._private = None
        self._p_q_bits = nbits // 2

        if nbits <= 32:
            prime_numbers = self._collect_primes(limit=256)
            dummy_gen = True
        else:
            prime_numbers = self._collect_primes(limit=1024)
            dummy_gen = False

        self.__prime_numbers = prime_numbers
        self.__is_dummy_gen = dummy_gen

    @property
    def public(self) -> PublicKey:
        return self._public

    @property
    def private(self) -> PrivateKey:
        return self._private

    def generate(self) -> None:
        try:
            self._load()
        except FileNotFoundError:
            self._generate()
            self._save()
        else:
            click.secho("Keys loaded..", fg="green")

    def _load(self) -> None:
        with open(self._PRIVATE_KEY_NAME, "rb") as f:
            self._private = PrivateKey.from_bytes(f.read())

        with open(self._PUBLIC_KEY_NAME, "rb") as f:
            self._public = PublicKey.from_bytes(f.read())

    def _generate(self) -> None:
        # Compute the product of p and q
        click.secho("Generating keys...", fg="green")

        self._generate_p_and_q()

        p, q = self._p, self._q
        n = p * q

        # Choose e such that gcd(e, phi_n) == 1.
        # phi(n) - кол-во чисел, взаимно-простых с n, и меньших n.
        # Для простых - phi(n) = n-1, т.к. все числа взаимно-просты для n.
        # => phi(p*q) = (p-1)*(q-1), если p и q -- взаимно-простые

        phi_n = (p - 1) * (q - 1)
        # По теореме Эйлера a^phi(n) = 1 (mod n), если gcd(a, n) == 1

        # Берем любое число от 2 до phi(n)-1, которое взаимно простое с phi(n).
        click.secho("Generating e", fg="green")
        e = randint(2, phi_n - 1)
        while self._extended_euclidean_gcd(e, phi_n)[0] != 1:
            e = randint(2, phi_n - 1)

        click.secho("Generating d", fg="green")
        d = self._mod_inverse(e, phi_n)
        # gcd(e, phi(n)) == 1 => они взаимно простые.
        # Находим такое число d, что (e * d) % phi(n) = 1. [ed = 1 mod(phi(n))]

        # Согласно теореме, если gcd(a,b) = N, то есть x,y такие
        # что xa+yb=N

        # gcd(e, phi_n) = 1
        # => x*e + y*phi_n = 1
        # g, x, y = _extended_euclidean_gcd(e, phi_n)

        #  ex + phi_n*y = 1
        #  ex - 1 = (-y)*phi_n
        # Если Q-1 делится на phi_n, значит Q имеет остаток 1 по модулю phi(n).
        #  => ex = 1 (mod phi_n)

        # d = x % phi_n

        self._private, self._public = PrivateKey(n, d), PublicKey(n, e)
        click.secho("Generated keys.", fg="green")

    def _save(self) -> None:
        click.secho("Saving keys...", fg="green")

        if self._public and self._private:
            with open(self._PRIVATE_KEY_NAME, "wb") as f:
                f.write(bytes(self._private))

            with open(self._PUBLIC_KEY_NAME, "wb") as f:
                f.write(bytes(self._public))

        click.secho("Saved keys...", fg="green")

    def _generate_p_and_q(self) -> None:
        click.secho("Generating p and q...", fg="green")

        p, q = self._get_prime_number(), self._get_prime_number()

        while q == p:
            q = self._get_prime_number()

        self._p = p
        self._q = q

        click.secho("Generated p and q.", fg="green")

    def _get_prime_number(self) -> int:
        if self.__is_dummy_gen:
            return self._dummy_prime()

        return self._optimized_prime()

    def _dummy_prime(self) -> int:
        candidate = self._get_low_level_prime()
        print(candidate, self._is_miller_rabin_passed(candidate))
        return candidate

    def _optimized_prime(self) -> int:
        candidate = self._get_low_level_prime()
        while not self._is_miller_rabin_passed(candidate):
            candidate = self._get_low_level_prime()

        return candidate

    def _get_low_level_prime(self) -> int:
        while True:
            prime_candidate = self._get_random_number()

            for divisor in self.__prime_numbers:
                if (
                    prime_candidate % divisor == 0
                    and divisor * divisor <= prime_candidate
                ):
                    break
            # If no divisor found, return value
            else:
                return prime_candidate

    def _get_random_number(self) -> int:
        """
        Returns a random number between 2^(n-1) + 1 and 2^n - 1
        """
        nbits = self._p_q_bits
        return randrange(2 ** (nbits - 1) + 1, 2**nbits - 1)

    def _is_miller_rabin_passed(
        self, mrc: int, number_of_rabin_trials: int = 20
    ) -> bool:
        """Run 20 iterations of Rabin Miller Primality test"""

        max_divisions_by_two = 0

        ec = mrc - 1

        while ec % 2 == 0:
            ec >>= 1
            max_divisions_by_two += 1

        assert 2**max_divisions_by_two * ec == mrc - 1

        def trial_composite(tester: int) -> bool:
            if pow(tester, ec, mrc) == 1:
                return False

            for i in range(max_divisions_by_two):
                if pow(tester, 2**i * ec, mrc) == mrc - 1:
                    return False

            return True

        for i in range(number_of_rabin_trials):
            round_tester = randrange(2, mrc)
            if trial_composite(round_tester):
                return False

        return True

    @staticmethod
    def _collect_primes(limit: int = 256, from_: int = 2) -> list[int]:
        primes = [True] * limit
        primes[0] = primes[1] = False

        res: list[int] = []
        for i, isprime in enumerate(primes):
            if isprime:
                if i >= from_:
                    res.append(i)

                for n in range(i * i, limit, i):
                    primes[n] = False

        return res

    def _mod_inverse(self, a: int, m: int) -> int:
        """
        :param a: number
        :param m: module
        :return: mod inverse
        """

        g, x, _ = self._extended_euclidean_gcd(a, m)
        #  ax + my = 1
        #  ax - 1 = (-y)*m
        #  => ax - 1 делится на m
        #  => ax = 1 (mod m)

        if g != 1:
            raise ValueError("Inverse doesn't exist")

        return x % m

    def _extended_euclidean_gcd(self, a: int, b: int) -> tuple[int, int, int]:
        """Return the gcd of a and b, and integers p and q such that

        gcd(a, b) == p * a + b * q.

        Preconditions:
        - a >= 0
        - b >= 0

        extended_euclidean_gcd(13, 10)
        (1, 7, -9)
        """
        x, y = a, b

        px, qx = 1, 0
        py, qy = 0, 1

        while y != 0:
            assert math.gcd(x, y) == math.gcd(a, b)
            assert x == px * a + qx * b
            assert y == py * a + qy * b

            ans, r = divmod(x, y)
            # x - q * y
            # px * a + qx * b - q (py * a + qy * b)
            # r = a (px - A*py) + b (qx - A * qy)

            m, n = px - py * ans, qx - qy * ans

            x, y, px, qx, py, qy = y, r, py, qy, m, n

        return x, px, qx
