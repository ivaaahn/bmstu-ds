from .mapper import Mapper


class Rotor(Mapper):
    def __init__(self, letters: bytes, initial_pos: int) -> None:
        super().__init__(letters)
        self._curr_start = self.letter_to_pos(initial_pos)

    @property
    def curr_start(self) -> int:
        return self._curr_start

    def straight(self, letter: int) -> int:
        pos_in: int = self.letter_to_pos(letter)

        start = self._curr_start

        pos_out: int = self._wires[(pos_in + start) % len(self.POS_TO_LETTER)] - start
        return self.pos_to_letter(pos_out)

    def back(self, letter: int) -> int:
        pos_in: int = self.letter_to_pos(letter)
        start = self._curr_start

        pos_out = self._wires.index((pos_in + start) % len(self.POS_TO_LETTER)) - start

        return self.pos_to_letter(pos_out)

    def turn(self) -> None:
        self._curr_start = (self._curr_start + 1) % len(self.POS_TO_LETTER)

    def full_circle_is_done(self) -> bool:
        return self.curr_start == 0
