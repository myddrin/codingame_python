"""
https://www.codingame.com/ide/puzzle/code-of-the-rings
"""
import dataclasses
import enum
import sys
from collections import defaultdict
from typing import (
    ClassVar,
    Dict,
    List,
)


ASCII_MAP = {
    chr(v): v
    for v in range(ord('A'), ord('Z') + 1)
}
ASCII_MAP[' '] = ord('A') - 1  # +1 from space to A
HALF_MAP = len(ASCII_MAP) // 2
N_STATES = 30


def debug(*args, **kwargs):
    print(*args, file=sys.stderr, flush=True, **kwargs)


class Action(enum.Enum):
    GoLeft = '<'
    GoRight = '>'
    NextLetter = '+'
    PrevLetter = '-'
    Commit = '.'
    StartLoop = '['
    EndLoop = ']'

    def repeat(self, n: int) -> str:
        act = self
        if n < 0:
            act = act.reverse()
        return ''.join([act.value] * abs(n))

    def reverse(self) -> 'Action':
        if self == self.GoLeft:
            return self.GoRight
        elif self == self.GoRight:
            return self.GoLeft
        elif self == self.NextLetter:
            return self.PrevLetter
        elif self == self.PrevLetter:
            return self.NextLetter
        elif self == self.Commit:
            return self
        elif self == self.StartLoop:
            return self.EndLoop
        elif self == self.EndLoop:
            return self.StartLoop
        raise ValueError(f'Unsupported action: {self}')


@dataclasses.dataclass
class Processor:
    half_states: ClassVar[int] = N_STATES // 2

    states: List[str] = dataclasses.field(default_factory=lambda: [' '] * N_STATES)
    _current_idx = 0
    actions: List[str] = dataclasses.field(default_factory=list)

    @property
    def current_idx(self) -> int:
        return self._current_idx

    @current_idx.setter
    def current_idx(self, v: int):
        self._current_idx = v % N_STATES

    @property
    def current_letter(self) -> str:
        return self.states[self.current_idx]

    @current_letter.setter
    def current_letter(self, v: str):
        self.states[self.current_idx] = v

    @classmethod
    def local_actions(cls, current: str, target: str) -> str:
        steps = ASCII_MAP[target] - ASCII_MAP[current]
        action = Action.NextLetter
        # debug(f'current={current} target={target} steps={steps}')

        if steps > HALF_MAP:
            steps -= len(ASCII_MAP)  # reverse() handled by repeat
        elif steps < -HALF_MAP:
            steps += len(ASCII_MAP)  # reverse() handled by repeat

        return action.repeat(steps)

    @classmethod
    def static_location(cls, magic_phrase: str) -> str:
        obj = cls()
        debug('static_location')
        actions = []
        for letter in magic_phrase:
            actions.append(cls.local_actions(obj.current_letter, letter) + Action.Commit.value)
            obj.current_letter = letter

        return ''.join(actions)

    @classmethod
    def memory_location(cls, magic_phrase: str) -> str:
        obj = cls()

        unique_letters = defaultdict(int)
        for letter in magic_phrase:
            unique_letters[letter] += 1
        # more than 30 repeated letters? sorted(unique_letters.items(), key=lambda o: o[1], reversed=True)[:N_STATES]
        repeated_letters = {
            letter
            for letter, n_l in unique_letters.items()
            if n_l > 1 and letter != ' '
        }

        debug(f'memory_location repeated={"".join(sorted(repeated_letters))}')
        for i, letter in enumerate(magic_phrase):
            if letter == obj.current_letter:
                obj.actions.append(Action.Commit.value)
                continue  # next

            if (obj.current_letter in repeated_letters and i > 0) or letter in repeated_letters:
                next_idx = (obj.current_idx + 1) % N_STATES
                local_action = Action.GoRight.value + Processor.local_actions(
                    obj.states[next_idx],
                    letter,
                ) + Action.Commit.value
            else:
                local_action = Processor.local_actions(
                    obj.current_letter,
                    letter,
                ) + Action.Commit.value

            if letter in obj.states:
                target_idx = obj.states.index(letter)  # dumb search: first in list rather than closest
                moves = obj.current_idx - target_idx
                action = Action.GoLeft
                if moves > cls.half_states:
                    moves -= N_STATES  # reverse() handled by repeat
                elif moves < -HALF_MAP:
                    moves += N_STATES  # reverse() handled by repeat

                move_action = action.repeat(moves) + Action.Commit.value

                if len(move_action) < len(local_action):
                    obj.actions.append(move_action)
                    obj.current_idx = target_idx
                    continue
            if local_action.startswith(Action.GoRight.value):
                obj.current_idx += 1
            elif local_action.startswith(Action.GoLeft.value):
                obj.current_idx -= 1

            # debug(f'Make {letter}@{current_idx}')
            obj.actions.append(local_action)
            obj.current_letter = letter

        return ''.join(obj.actions)


def run_all(magic_phrase: str) -> Dict[str, str]:
    return {
        fn.__name__: fn(magic_phrase)
        for fn in (
            Processor.static_location,
            Processor.memory_location,
        )
    }


if __name__ == '__main__':
    magic_phrase_input = input()
    options = run_all(magic_phrase_input)
    for name, actions in options.items():
        debug(f'{name}={len(actions)}')

    best = sorted(options.values(), key=len)[0]
    print(best)
