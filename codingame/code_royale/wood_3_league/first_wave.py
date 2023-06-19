import dataclasses
import sys
import math

from enum import IntEnum, Enum
from typing import List, Dict, Optional, Tuple


class BuildingsType(IntEnum):
    NoStructure = -1
    Barracks = 2


class OwnerType(IntEnum):
    NoOwner = -1
    Friendly = 0
    Enemy = 1


class UnitType(IntEnum):
    Queen = -1
    Knight = 0
    Archer = 1

    @property
    def cost(self):
        _unit_prices = {
            UnitType.Knight: 80,
            UnitType.Archer: 100,
        }
        return _unit_prices.get(self)

    @property
    def speed(self):
        _unit_speed = {
            UnitType.Queen: 60,
            # Knights are fast but we don't know how much
            # Archers are slow but we don't know how much
        }
        return _unit_speed.get(self)

def debug(msg: str):
    print(f"D {msg}", file=sys.stderr, flush=True)


def info(msg: str):
    print(f"I {msg}", file=sys.stderr, flush=True)


def warning(msg: str):
    info('====')
    info(msg)
    info('====')


def log_input(input_str: str):
    print(input_str, file=sys.stderr, flush=True)


@dataclasses.dataclass
class Coordinate:
    x: int
    y: int

    def __str__(self):
        return f'({self.x}, {self.y})'

    def distance(self, other: "Coordinate"):
        return math.sqrt((other.x - self.x)**2 + (other.y - self.y)**2)

    def manhattan(self, other: "Coordinate"):
        # Cheaper, maybe better?
        return abs(self.x - other.x) + abs(self.y - other.y)

    def get_away(self, other: "Coordinate"):
        # dummy get away: we'll go hide in a corner
        d_x = 0
        d_y = 0
        if self.x > other.x:
            d_x += UnitType.Queen.speed
        elif self.x < other.x:
            d_x -= UnitType.Queen.speed

        if self.y > other.y:
            d_y += UnitType.Queen.speed
        elif self.y < other.y:
            d_y -= UnitType.Queen.speed

        return self.legitimate_coordinate(
            max(self.x + d_x, 0),
            max(self.y + d_y, 0),
        )

    @classmethod
    def legitimate_coordinate(cls, x: int, y: int):
        return Coordinate(
            x=min(max(x, 0), 1920),
            y=min(max(y, 0), 1000),
        )


@dataclasses.dataclass
class BuildingSite(Coordinate):
    site_id: int
    radius: int

    structure: BuildingsType = BuildingsType.NoStructure
    owner: OwnerType = OwnerType.NoOwner

    barrack_type: Optional[UnitType] = None

    @property
    def site_id_str(self):
        return f'B-{self.site_id}'

    def __str__(self):
        return f'{self.site_id_str} {self.structure.name} {self.owner.name} {Coordinate.__str__(self)}'

    def update(self, **kwargs):
        change = []
        for f in dataclasses.fields(self):
            v = kwargs.get(f.name)
            if v is not None and v != getattr(self, f.name):
                setattr(self, f.name, v)
                change.append(f.name)
        if change:
            debug(f'{self.site_id_str} changed {", ".join(change)} {self}')

    @classmethod
    def from_input(cls, input_str: str) -> "BuildingSite":
        input_list = [int(j) for j in input_str.split()]
        # site_id, x, y, radius = [int(j) for j in input().split()]
        return cls(
            site_id=input_list[0],
            x=input_list[1],
            y=input_list[2],
            radius=input_list[3],
        )


@dataclasses.dataclass
class Unit(Coordinate):
    unit_type: UnitType
    owner: OwnerType
    health: int

    def __str__(self):
        return f'{self.unit_type.name} {self.owner.name} {self.health} {Coordinate.__str__(self)}'

    @classmethod
    def from_input(cls, input_str: str) -> "Unit":
        # unit_type: -1 = QUEEN, 0 = KNIGHT, 1 = ARCHER
        # x, y, owner, unit_type, health = [int(j) for j in input().split()]
        input_list = [int(j) for j in input_str.split()]
        return cls(
            x=input_list[0],
            y=input_list[1],
            owner=OwnerType(input_list[2]),
            unit_type=UnitType(input_list[3]),
            health=input_list[4],
        )


class Command:

    @classmethod
    def build_barracks(cls, building: BuildingSite, unit_type: UnitType):
        building.barrack_type = unit_type
        return f'BUILD {building.site_id} BARRACKS-{unit_type.name.upper()}'

    @classmethod
    def move_to(cls, where: Coordinate):
        return f'MOVE {where.x} {where.y}'

    @classmethod
    def wait(cls):
        return 'WAIT'

    @classmethod
    def train(cls, buildings: List[BuildingSite]):
        if buildings:
            return f'TRAIN {" ".join([str(b.site_id) for b in buildings])}'
        return 'TRAIN'  # if it contains a space it confuses the parser


@dataclasses.dataclass
class GameState:
    gold: int = 0
    touched_site_id: Optional[int] = None

    site_map: Dict[int, BuildingSite] = dataclasses.field(default_factory=dict)

    my_queen: Optional[Unit] = None
    their_queen: Optional[Unit] = None
    enemies: List[Unit] = dataclasses.field(default_factory=list)
    allies: List[Unit] = dataclasses.field(default_factory=list)

    last_action: Optional[str] = None

    @property
    def num_sites(self) -> int:
        return len(self.site_map)

    @property
    def touched_site(self) -> Optional[BuildingSite]:
        if self.touched_site_id is not None:
            return self.site_map[self.touched_site_id]

    def get_sites(
        self,
        owner: OwnerType=None,
        structure: BuildingsType=None,
        barrack_type: UnitType=None,
    ) -> List[BuildingSite]:
        return [
            s
            for s in self.site_map.values()
            if all((
                (owner is None or s.owner == owner),
                (structure is None or s.structure == structure),
                # It needs to be a built to count!
                (barrack_type is None or (s.structure == BuildingsType.Barracks and s.barrack_type == barrack_type)),
            ))
        ]

    def get_allies(self, unit_type: UnitType) -> List[Unit]:
        return [
            s
            for s in self.allies
            if s.unit_type == unit_type
        ]

    def get_enemies(self, unit_type: UnitType=None) -> List[Unit]:
        return [
            s
            for s in self.enemies
            if (unit_type is None or s.unit_type == unit_type)
        ]

    def print_state(self):
        info(f'G={self.gold} my_queen={self.my_queen} with {len(self.allies)} units and {len(self.get_sites(OwnerType.Friendly))} buildings ')
        info(f'Enemy queen={self.their_queen} with {len(self.enemies)} units and {len(self.get_sites(OwnerType.Enemy))} buildings ')

    def add_site(self, site: BuildingSite):
        # debug(f'Discovering {site}')
        self.site_map[site.site_id] = site

    def _clear_state(self):
        self.touched_site_id = None

        self.my_queen = None
        self.their_queen = None
        self.enemies = []
        self.allies = []
        # self.my_buildings = []  # TODO(tr) compute

    def update_from_input(self):
        self._clear_state()

        input_list = [int(j) for j in game_input().split()]
        self.gold = input_list[0]
        if input_list[1] != -1:
            self.touched_site_id = input_list[1]
        else:
            self.touched_site_id = None

        for i in range(self.num_sites):
            self._update_map_from_input(game_input())

        num_units = int(game_input())
        for i in range(num_units):
            self._update_units_from_input(game_input())

    def _update_map_from_input(self, input_str: str):
        # site_id, ignore_1, ignore_2, structure_type, owner, param_1, param_2 = [int(j) for j in input_str.split()]
        input_list = [int(j) for j in input_str.split()]

        site = self.site_map[input_list[0]]
        site.update(structure=BuildingsType(input_list[3]), owner=OwnerType(input_list[4]))

    def _update_units_from_input(self, input_str: str):
        unit = Unit.from_input(input_str)
        if unit.owner == OwnerType.Friendly:
            if unit.unit_type == UnitType.Queen:
                self.my_queen = unit
            else:
                self.allies.append(unit)
        elif unit.owner == OwnerType.Enemy:
            if unit.unit_type == UnitType.Queen:
                self.their_queen = unit
            else:
                self.enemies.append(unit)

    def closest_building_to_queen(self, owner: OwnerType):
        debug(f'Looking for closest {owner.name} building to the queen')
        closest = None
        distance = None
        for b in self.get_sites(owner=owner):
            d2 = self.my_queen.distance(b)
            debug(f'{b} is {d2} away')
            if closest is None or d2 < distance:
                closest = b
                distance = d2
                continue

        return closest

    def closest_enemy(self):
        debug('Looking for the closest enemy')
        closest = None
        distance = None
        for u in self.get_enemies(unit_type=UnitType.Knight):
            d2 = self.my_queen.distance(u)
            # debug(f'{b} is {d2} away')
            if closest is None or d2 < distance:
                closest = u
                distance = d2
                continue

        return closest

    def queen_action(self) -> str:
        # dummy: we're closed to an empty site: build something
        closest_empty = self.touched_site
        debug(f'Touching {closest_empty}')

        if closest_empty is None or closest_empty.owner != OwnerType.NoOwner:
            # No touching a site that is ours, look for one
            closest_empty = self.closest_building_to_queen(owner=OwnerType.NoOwner)

        if closest_empty:
            barrack_type = None
            # Defensive: ensure 1 archer production
            if len(self.get_sites(owner=OwnerType.Friendly, barrack_type=UnitType.Archer)) < 1:
                barrack_type = UnitType.Archer
            elif len(self.get_sites(owner=OwnerType.Friendly, barrack_type=UnitType.Knight)) < 2:
                barrack_type = UnitType.Knight

            if barrack_type is not None:
                debug(f'Building a BARRACK-{barrack_type.name.upper()} on {closest_empty}')
                self.last_action = None  # we don't want to remember that
                return Command.build_barracks(closest_empty, barrack_type)
            else:
                debug(f'Ignoring {closest_empty}')

        # if self.my_queen.health > 50:
        #     # balsy: go steal a building
        #     closest_empty = self.closest_building_to_queen(owner=OwnerType.Enemy)
        #     if closest_empty:
        #         return Command.build_barracks(closest_empty, UnitType.Knight)

        # Nowhere to go, more logic to avoid enemy (maybe do that first?)
        closest_enemy = self.closest_enemy()
        if closest_enemy and self.my_queen.distance(closest_enemy) < (UnitType.Queen.speed * 3):
            debug(f'Evading from {closest_enemy}')
            return Command.move_to(self.my_queen.get_away(closest_enemy))

        closest_empty = self.closest_building_to_queen(owner=OwnerType.Enemy)
        if closest_empty:
            debug(f'Evading from enemy buildings')
            return Command.move_to(self.my_queen.get_away(closest_empty))

        return Command.wait()

    def train_action(self):
        # TODO(tr) build that directly from the input...
        unit_info = {
            UnitType.Knight: {},
            UnitType.Archer: {},
        }

        for ut in unit_info:
            unit_info[ut]['units'] = [u for u in self.allies if u.unit_type == ut]
            unit_info[ut]['barracks'] = self.get_sites(barrack_type=ut)
            unit_info[ut]['enemy'] = [u for u in self.enemies if u.unit_type == ut]

            debug(f'We have {len(unit_info[ut]["units"])} {ut.name} and {len(unit_info[ut]["barracks"])} barracks')

        buildings: List[BuildingSite] = []
        gold = self.gold

        # Defensive: build archers first
        if (
            len(unit_info[UnitType.Archer]['barracks'])
            and len(unit_info[UnitType.Archer]['units']) < len(self.get_sites(owner=OwnerType.Enemy))
        ):
            if gold >= UnitType.Archer.cost:
                gold -= UnitType.Archer.cost
                # TODO(tr) prioritise by proximity to my queen
                buildings.append(unit_info[UnitType.Archer]['barracks'][0])

        if unit_info[UnitType.Knight]['barracks']:
            # TODO(tr) prioritise by proximity to enemy queen
            for b in unit_info[UnitType.Knight]['barracks']:
                if gold < UnitType.Knight.cost:
                    break  # cannot afford more
                buildings.append(b)

        return Command.train(buildings)
#
#
#


def game_input():
    input_str = input()
    log_input(input_str)
    return input_str


def play():
    num_sites = int(game_input())

    state = GameState()
    for i in range(num_sites):
        site = BuildingSite.from_input(game_input())
        state.add_site(site)

    turns = 0
    # game loop
    while True:
        # touched_site: -1 if none
        # gold, touched_site = [int(i) for i in input().split()]
        turns += 1
        warning(f'TURN {turns}')
        state.update_from_input()
        state.print_state()

        info('Choosing queen action')
        # First line: A valid queen action
        queen_action = state.queen_action()
        print(queen_action)
        info('Choosing train action')
        # Second line: A set of training instructions
        train_action = state.train_action()
        print(train_action)


if __name__ == '__main__':
    play()
