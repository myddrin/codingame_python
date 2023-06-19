"""
https://www.codingame.com/ide/puzzle/ghost-legs
"""
import dataclasses
import enum
import sys
from typing import List


def debug(*args, **kwargs):
    print(*args, file=sys.stderr, flush=True, **kwargs)


class Action(enum.Enum):
    Stay = '|'
    SwapRight = '|-'
    SwapLeft = '-|'


@dataclasses.dataclass
class GhostLegs:
    input_names: List[str]
    output_names: List[str]
    actions: List[List[Action]]

    @classmethod
    def load_from_input(cls) -> 'GhostLegs':
        _, h = [int(i) for i in input().split()]

        # first line of input is names: "A  B  C" -> ["A", "B", "C"]
        input_names: List[str] = list(input().replace(' ', ''))
        actions: List[List[Action]] = []  # one list of action of size `w` per row `h`
        for _ in range(h - 2):
            # A line like: "|  |  |" or "|--|  |" or "|  |--|" etc
            line = ' ' + input() + ' '  # inject a leading space and a trailing space so we can read 3 char per position
            actions.append([
                Action(line[st:st+3].strip())
                for st in range(0, len(line), 3)
            ])

        # last line of input is output: "1 2 3" -> ["1", "2", "3"]
        output_names: List[str] = list(input().replace(' ', ''))

        return GhostLegs(input_names, output_names, actions)

    def process(self) -> List[str]:
        columns = [n for n in self.input_names]
        for row in self.actions:
            # going from left to right
            for r, act in enumerate(row):
                if act == Action.SwapRight:
                    other = columns[r+1]
                    columns[r+1] = columns[r]
                    columns[r] = other
                elif act in (Action.Stay, Action.SwapLeft):
                    # do nothing on stay
                    # do nothing on swapleft - we've done it with swapright
                    pass

        output = {
            name: i
            for i, name in enumerate(columns)
        }
        return [
            f'{name}{self.output_names[output[name]]}'
            for name in self.input_names
        ]


if __name__ == '__main__':
    gl = GhostLegs.load_from_input()
    # debug(gl)
    for answer in gl.process():
        print(answer)
