"""
See https://www.codingame.com/ide/puzzle/rectangle-partition
"""

import sys
import dataclasses
from typing import (
    Generator,
    List,
)


def debug(msg: str, *args, **kwargs):
    print(msg, *args, **kwargs, file=sys.stderr, flush=True)


@dataclasses.dataclass(repr=False, frozen=True)
class Rect:
    x_st: int
    x_ed: int
    y_st: int
    y_ed: int

    @property
    def width(self) -> int:
        return abs(self.x_ed - self.x_st)

    @property
    def height(self) -> int:
        return abs(self.y_ed - self.y_st)

    @property
    def is_square(self) -> bool:
        return self.width == self.height

    def __str__(self):
        return f'[{self.x_st}, {self.x_ed}, {self.y_st}, {self.y_ed}]=Rect({self.width}, {self.height})'

    @classmethod
    def gen_rectangles_for_row(cls, st_y: int, ed_y: int, all_x: List[int]) -> Generator['Rect', None, None]:
        start_x = all_x[0]
        for j, x in enumerate(all_x[1:], start=1):
            r = cls(start_x, x, st_y, ed_y)
            # debug(f'Considering {r}')
            yield r

            for o_x in all_x[j + 1:]:
                r = cls(x, o_x, st_y, ed_y)
                # debug(f'Considering {r}')
                yield r


def process(x_cut: List[int], y_cut: List[int]):
    # debug(f'n_x_cut={len(x_cut)} n_y_cut={len(y_cut)}')
    # debug(f'x_cut={x_cut}')
    # debug(f'y_cut={y_cut}')

    rectangles = []

    #    ___2______5__________
    #   |   |      |          |
    #   |   |      |          |
    #  3|___|______|__________|
    #   |   |      |          |
    #   |___|______|__________|

    start_y = y_cut[0]
    for i, y in enumerate(y_cut[1:], start=1):
        rectangles.extend(Rect.gen_rectangles_for_row(start_y, y, x_cut))

        for o_y in y_cut[i + 1:]:
            rectangles.extend(Rect.gen_rectangles_for_row(y, o_y, x_cut))

    n_square = sum((1 for r in rectangles if r.is_square))

    debug(f'Found {n_square} squares / {len(rectangles)} rectangles')
    return n_square


def main():
    w, h, count_x, count_y = [int(i) for i in input().split()]
    x_cut = [0] + [int(i) for i in input().split()] + [w]
    y_cut = [0] + [int(i) for i in input().split()] + [h]
    print(process(x_cut, y_cut))


if __name__ == '__main__':
    main()
