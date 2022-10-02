import random

from enigma import Enigma, Reflector, Rotor


def read_file(path: str, mode: str = "r") -> str | bytes:
    with open(f"./data/{path}", mode) as f:
        return f.read()


def write_file(path: str, data: str | bytes, mode: str = "w") -> None:
    with open(f"./data/{path}", mode) as f:
        f.write(data)


def make_enigma_from_settings(file_path: str) -> Enigma:
    rotors_data: list[str | bytes] = []

    for idx in range(3):
        filename = make_settings_filename(file_path, f"rotor_{idx}")
        rotors_data.append(read_file(filename, "rb"))

    filename = make_settings_filename(file_path, "reflector")
    reflector_data = read_file(filename, "rb")

    rotors = [Rotor(rotors_data[i], 0) for i in range(3)]
    reflector = Reflector(reflector_data)

    return Enigma(
        rotors[0],
        rotors[1],
        rotors[2],
        reflector,
    )


def make_new_rand_enigma():
    letters_mutable = bytearray(Rotor.POS_TO_LETTER)
    rotors = []
    for _ in range(3):
        random.shuffle(letters_mutable)
        rotors.append(Rotor(letters_mutable.copy(), 0))

    random.shuffle(letters_mutable)
    reflector = Reflector(bytearray(reversed(Rotor.POS_TO_LETTER)))

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

    filename = make_settings_filename(file_path, "reflector")
    write_file(filename, bytes(reflector), "wb")
