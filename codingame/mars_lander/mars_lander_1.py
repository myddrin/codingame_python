import dataclasses
import sys
from typing import (
    ClassVar,
    List,
    Tuple,
)


def debug(*args, **kwargs):
    print(*args, file=sys.stderr, flush=True, **kwargs)


@dataclasses.dataclass(frozen=True)
class Position:
    MAX_X: ClassVar = 7000 - 1
    MAX_Y: ClassVar = 3000 - 1

    x: int
    y: int

    def __add__(self, other: 'Position'):
        if not isinstance(other, Position):
            raise TypeError(f'Not supported for {other.__class__.__name__}')

        return Position(self.x + other.x, self.y + other.y)

    @classmethod
    def from_input(cls) -> 'Position':
        return cls(*(int(j) for j in input().split()))

    @classmethod
    def land_from_input(cls) -> List['Position']:
        surface_n = int(input())  # the number of points used to draw the surface of Mars.
        return [
            cls.from_input()
            for _ in range(surface_n)
        ]


@dataclasses.dataclass
class State:
    """
    :param position:
    :param speed: the horizontal (x) and vertical (y) speed (in m/s), can be negative.
    :param fuel: the quantity of remaining fuel in liters.
    :param rotate: the rotation angle in degrees (-90 to 90).
    :param power: the thrust power (0 to 4).
    """
    MARS_G: ClassVar = 4
    MAX_POWER: ClassVar = 4
    MAX_ROTATE: ClassVar = 90

    MAX_LANDING_SPEED: ClassVar = Position(20, 40)

    position: Position
    speed: Position
    fuel: int
    rotate: int
    power: int

    @classmethod
    def from_input(cls) -> 'State':
        args = [int(j) for j in input().split()]
        return cls(
            position=Position(*args[0:2]),
            speed=Position(*args[2:4]),
            fuel=args[4],
            rotate=args[5],
            power=args[6],
        )

    def next_speed(self, *, power: int) -> Position:
        # TODO(tr) compute horizontal speed too
        return self.speed + Position(0, power - self.MARS_G)

    def is_safe_speed(self, speed: Position = None) -> bool:
        if speed is None:
            speed = self.speed
        return abs(speed.x) <= self.MAX_LANDING_SPEED.x and abs(speed.y) <= self.MAX_LANDING_SPEED.y


def burn_it_all_vertical(state: State) -> Tuple[int, int]:
    next_angle = 0  # For solution 1 do not change angle

    for next_power in range(0, State.MAX_POWER):
        next_speed = state.next_speed(power=next_power)
        if abs(next_speed.y) < State.MAX_LANDING_SPEED.y:
            return next_angle, next_power

    return next_angle, State.MAX_POWER


def main():
    surface = Position.land_from_input()
    for s in surface:
        debug(s)

    # game loop
    while True:
        current_state = State.from_input()
        debug(current_state)

        next_angle, next_power = burn_it_all_vertical(current_state)

        # 2 integers: rotate power.
        # rotate is the desired rotation angle (should be 0 for level 1),
        # power is the desired thrust power (0 to 4).
        print(f'{next_angle} {next_power}')


if __name__ == '__main__':
    main()
