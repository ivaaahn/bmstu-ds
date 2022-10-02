from .reflector import Reflector
from .rotor import Rotor


class Enigma:
    def __init__(
        self,
        left_rotor: Rotor,
        mid_rotor: Rotor,
        right_rotor: Rotor,
        reflector: Reflector,
    ) -> None:
        self._left_rotor = left_rotor
        self._mid_rotor = mid_rotor
        self._right_rotor = right_rotor
        self._reflector = reflector

    @property
    def rotors(self) -> list[Rotor]:
        return [
            self._left_rotor,
            self._mid_rotor,
            self._right_rotor,
        ]

    @property
    def reflector(self) -> Reflector:
        return self._reflector

    def _turn_rotors(self) -> None:
        self._right_rotor.turn()

        if self._right_rotor.full_circle_is_done():
            self._mid_rotor.turn()

            if self._mid_rotor.full_circle_is_done():
                self._left_rotor.turn()

    def encrypt(self, letter: int) -> int:
        self._turn_rotors()

        letter_0 = letter
        letter_rs = self._right_rotor.straight(letter_0)
        letter_ms = self._mid_rotor.straight(letter_rs)
        letter_ls = self._left_rotor.straight(letter_ms)

        letter_ref = self._reflector.straight(letter_ls)

        letter_lb = self._left_rotor.back(letter_ref)
        letter_mb = self._mid_rotor.back(letter_lb)
        letter_rb = self._right_rotor.back(letter_mb)
        letter_res = letter_rb

        return letter_res
