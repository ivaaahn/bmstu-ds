class Mapper:
    POS_TO_LETTER: bytes = bytes([i for i in range(256)])
    LETTER_TO_POS: dict[bytes, int] = {
        letter: pos for pos, letter in enumerate(POS_TO_LETTER)
    }

    def __init__(self, letters: bytes) -> None:
        self._letters: bytes = letters
        self._wires: list[int] = [
            self.letter_to_pos(letter) for letter in self._letters
        ]

    @classmethod
    def letter_to_pos(cls, letter: int) -> int:
        if isinstance(letter, str):
            letter = bytes([ord(letter)])
        return cls.POS_TO_LETTER.find(letter)

    @classmethod
    def pos_to_letter(cls, pos: int) -> int:
        return cls.POS_TO_LETTER[pos]

    def straight(self, letter: int) -> int:
        input_number = self.letter_to_pos(letter)
        return self._letters[input_number]

    def back(self, letter: bytes) -> int:
        letter_pos = self._letters.find(letter)
        return self.pos_to_letter(letter_pos)

    def __bytes__(self) -> bytes:
        return bytes(self._letters)

    def __repr__(self) -> str:
        return self.__str__()
