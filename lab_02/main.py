import random
import string
import click


ROTOR_1 = "EKMFLGDQVZNTOWYHXUSPAIBRCJ"
ROTOR_2 = "AJDKSIRUXBLHWTMCQGZNPYFVOE"
ROTOR_3 = "BDFHJLCPRTXVZNYEIWGAKMUSQO"
REFLECTOR_B = "YRUHQSLDPXNGOKMIEBFZCWVJAT"


class Mapper:
    POS_TO_LETTER: str = string.ascii_uppercase
    LETTER_TO_POS: dict[str, int] = {
        letter: pos for pos, letter in enumerate(POS_TO_LETTER)
    }

    def __init__(self, letters: str | bytes) -> None:
        self._letters: str = letters
        self._wires: list[int] = [
            self.letter_to_pos(letter) for letter in self._letters
        ]

    @classmethod
    def letter_to_pos(cls, letter: str) -> int:
        return cls.LETTER_TO_POS[letter.upper()]

    @classmethod
    def pos_to_letter(cls, pos: int) -> str:
        return cls.POS_TO_LETTER[pos]

    def straight(self, letter: str) -> str:
        input_number = self.letter_to_pos(letter)
        return self._letters[input_number]

    def back(self, letter: str) -> str:
        letter_pos = self._letters.find(letter)
        return self.pos_to_letter(letter_pos)

    def __str__(self) -> str:
        return self._letters

    def __bytes__(self) -> bytes:
        return bytes(self._letters)

    def __repr__(self) -> str:
        return self.__str__()


class Rotor(Mapper):
    def __init__(self, letters: str | bytes | bytearray, initial_pos: str | bytes) -> None:
        super().__init__(letters)
        self._curr_start = self.letter_to_pos(initial_pos)

    def straight(self, letter: str) -> str:
        pos_in: int = self.letter_to_pos(letter)

        start = self._curr_start

        pos_out: int = self._wires[(pos_in + start) % len(self.POS_TO_LETTER)] - start
        return self.pos_to_letter(pos_out)

    def back(self, letter: str) -> str:
        pos_in: int = self.letter_to_pos(letter)
        start = self._curr_start

        pos_out = self._wires.index((pos_in + start) % len(self.POS_TO_LETTER)) - start

        return self.pos_to_letter(pos_out)

    def turn(self) -> None:
        self._curr_start = (self._curr_start + 1) % len(self.POS_TO_LETTER)


class CustomMixin:
    POS_TO_LETTER: bytes = bytes([i for i in range(256)])
    # LETTER_TO_POS: dict[bytes | str, int] = {
    #     letter: pos for pos, letter in enumerate(POS_TO_LETTER)
    # }

    @classmethod
    def letter_to_pos(cls, letter: str | bytes) -> int:
        if isinstance(letter, str):
            letter = bytes([ord(letter)])
        return cls.POS_TO_LETTER.find(letter)


class Reflector(Mapper):
    pass


class RotorCustom(CustomMixin, Rotor):
    pass


class ReflectorCustom(CustomMixin, Reflector):
    pass


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

    def encrypt(self, letter: str) -> str | bytes:
        self._right_rotor.turn()

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


def read_file(path: str, mode: str = "r") -> str | bytes:
    with open(path, mode) as f:
        return f.read()


def write_file(path: str, data: str | bytes, mode: str = "w") -> None:
    with open(path, mode) as f:
        f.write(data)


def make_real_enigma() -> Enigma:
    rotors = [
        Rotor(ROTOR_1, "A"),
        Rotor(ROTOR_2, "A"),
        Rotor(ROTOR_3, "Z"),
    ]
    reflector = Reflector(REFLECTOR_B)
    return Enigma(
        rotors[0],
        rotors[1],
        rotors[2],
        reflector,
    )


def make_enigma_from_settings(file_path: str) -> Enigma:
    rotors_data: list[str | bytes] = []

    for idx in range(3):
        filename = make_settings_filename(file_path, f"rotor_{idx}")
        rotors_data.append(read_file(filename, "rb"))

    filename = make_settings_filename(file_path, "reflector")
    reflector_data = read_file(filename, "rb")

    rotors = [RotorCustom(rotors_data[i], bytes([0])) for i in range(3)]
    reflector = ReflectorCustom(reflector_data)

    return Enigma(
        rotors[0],
        rotors[1],
        rotors[2],
        reflector,
    )


def make_new_rand_enigma():
    letters_mutable = bytearray(CustomMixin.POS_TO_LETTER)
    rotors = []
    for _ in range(3):
        random.shuffle(letters_mutable)
        rotors.append(RotorCustom(letters_mutable.copy(), bytes((0,))))

    random.shuffle(letters_mutable)
    reflector = ReflectorCustom(bytearray(reversed(CustomMixin.POS_TO_LETTER)))

    return Enigma(
        rotors[0],
        rotors[1],
        rotors[2],
        reflector,
    )


def make_settings_filename(file_path: str, slug: str | int) -> str:
    return f"{file_path}__settings_{slug}.txt"


def write_settings_file(
    file_path: str, rotors: list[Rotor], reflector: Reflector
) -> None:
    for idx, rotor in enumerate(rotors):
        filename = make_settings_filename(file_path, f"rotor_{idx}")
        write_file(filename, bytes(rotor), "wb")

    filename = make_settings_filename(file_path, f"reflector")
    write_file(filename, bytes(reflector), "wb")


@click.command()
@click.option(
    "-file_path",
    default=None,
    help="Из файла.",
)
@click.option(
    "-it",
    is_flag=True,
    show_default=True,
    help="Интерактивный режим.",
)
@click.option(
    "--use_settings",
    is_flag=True,
    default=False,
    help="Из файла.",
)
@click.option(
    "--real_enigma",
    is_flag=True,
    show_default=False,
    help="Моделирование реальной Энигмы (Rotor I, Rotor II, Rotor III, Reflector-B, AAZ).",
)
def main(
    file_path: str | None, it: bool, real_enigma: bool, use_settings: str | None
) -> None:
    if it and file_path:
        click.secho("Выберите только один режим")
        return

    if use_settings and real_enigma:
        click.secho("Выберите только один режим")
        return

    if real_enigma:
        enigma = make_real_enigma()
    elif use_settings:
        if not file_path:
            click.secho("Используется только вместе в -file_path")
            return
        enigma = make_enigma_from_settings(file_path)
    else:
        enigma = make_new_rand_enigma()

    write_settings_file(file_path, enigma.rotors, enigma.reflector)

    if not it:
        try:
            file = read_file(path=file_path, mode="rb")
        except FileNotFoundError:
            click.secho("Не удалось найти файл", fg="red", bold=True)
        else:

            if real_enigma:
                cipher_text = "".join([enigma.encrypt(letter) for letter in file])
            else:
                cipher_text = b"".join([bytes([enigma.encrypt(letter)]) for letter in file])

            write_file(path=f"{file_path}__cipher.txt", data=cipher_text, mode="wb")

        return

    while True:
        click.secho("Введите букву:", fg="yellow", bold=True)
        letter_in = input().strip().lower()
        cipher = enigma.encrypt(letter_in)
        click.secho(f"{letter_in}    -->    {cipher}", fg="green", bold=True)


if __name__ == "__main__":
    main()
