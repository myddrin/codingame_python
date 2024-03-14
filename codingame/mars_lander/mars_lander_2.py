import dataclasses
import sys
from math import (
    ceil,
    floor,
)
from operator import attrgetter
from typing import (
    ClassVar,
    Dict,
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

    @classmethod
    def land_map(cls, land: List['Position']) -> Dict[int, int]:
        ordered = sorted(land, key=attrgetter('x'))
        prev = ordered[0]
        land_map = {
            prev.x: prev.y
        }
        # TODO(tr) this is somewhat broken
        for point in ordered[1:]:
            dy = float(point.y - prev.y) / (point.x - prev.x)
            # debug(f'delta {prev} -> {point} = {point.x - prev.x}, {dy}')
            cx = prev.x + 1
            cy = float(prev.y)
            while cx < point.x:
                cy += dy
                land_map[cx] = int(ceil(cy))
                cx += 1
            assert point.y == int(ceil(cy)), f'got {cx}, {cy:0.2f} expected {point}'
            land_map[point.x] = point.y

        return land_map


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
        return Position(
            self.speed.x,
            self.speed.y - self.MARS_G + power
        )

    def is_safe_speed(self, speed: Position = None) -> bool:
        if speed is None:
            speed = self.speed
        return abs(speed.x) <= self.MAX_LANDING_SPEED.x and abs(speed.y) <= self.MAX_LANDING_SPEED.y

    def predict_until(self, ground_y: int) -> List['State']:
        current = self
        states = []
        while current.fuel > 0 and current.position.y > ground_y:
            next_power = current.power  # max(current.power - 1, 0)
            next_speed = current.next_speed(power=current.power)
            states.append(State(
                current.position + next_speed,
                next_speed,
                current.fuel - current.power,
                current.rotate,
                next_power,
            ))
            current = states[-1]
        if current.fuel == 0:
            debug(f'CRASH')
        return states


def burn_it_all_vertical(state: State) -> Tuple[int, int]:
    next_angle = 0  # For solution 1 do not change angle

    for next_power in range(0, State.MAX_POWER):
        next_speed = state.next_speed(power=next_power)
        if abs(next_speed.y) < State.MAX_LANDING_SPEED.y:
            return next_angle, next_power

    return next_angle, State.MAX_POWER


def slow_landing(state: State, land: Dict[int, int]) -> Tuple[int, int]:
    next_angle = 0  # TODO(tr) for solution 1 do not change angle
    next_power = max(state.power - 1, 0)

    next_speed = state.next_speed(power=next_power)
    debug(f'Next speed= {next_speed}')
    if abs(next_speed.y) < State.MAX_LANDING_SPEED.y // 2:
        return next_angle, next_power

    landing_elevation = land[state.position.x]
    debug(f'Fund landing level: {landing_elevation}')
    predictions = state.predict_until(landing_elevation)
    debug(f'Predicted {len(predictions)} steps until landing')
    if len(predictions) <= 2:
        return next_angle, State.MAX_POWER

    landing_state = predictions[-1]
    last_predictions = [
        str(p.speed.y)
        for p in predictions[-5:]
    ]
    debug(f'Predictions[-5].speed: {", ".join(last_predictions)}')
    debug(f'Prediction fuel on landing: {landing_state.fuel}L')
    if not landing_state.is_safe_speed() and abs(state.speed.y) > 0:
        next_power = min(next_power + 2, State.MAX_POWER)

    if next_power != state.power:
        debug(f'next_power={next_power}')
    return next_angle, next_power


def main():
    surface = Position.land_from_input()
    for s in surface:
        debug(s)
    land_map = Position.land_map(surface)

    # game loop
    while True:
        current_state = State.from_input()
        debug(current_state)

        # next_angle, next_power = burn_it_all_vertical(current_state, land_map)
        next_angle, next_power = slow_landing(current_state, land_map)

        # 2 integers: rotate power. rotate is the desired rotation angle (should be 0 for level 1), power is the desired thrust power (0 to 4).
        print(f'{next_angle} {next_power}')


if __name__ == '__main__':
    main()
