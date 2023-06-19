import dataclasses
import sys
import math

from enum import IntEnum
from operator import attrgetter
from typing import List, Dict, Optional


DEBUG = False


class StructureType(IntEnum):
    NoStructure = -1
    Goldmine = 0
    Tower = 1  # max hp: 800
    Barracks = 2


class OwnerType(IntEnum):
    NoOwner = -1
    Friendly = 0
    Enemy = 1


class UnitType(IntEnum):
    Queen = -1
    Knight = 0
    Archer = 1
    Giant = 2

    @property
    def cost(self) -> Optional[int]:
        _unit_prices = {
            UnitType.Knight: 80,
            UnitType.Archer: 100,
            UnitType.Giant: 140,
        }
        return _unit_prices.get(self)

    @property
    def max_hp(self) -> Optional[int]:
        _max_hp = {
            UnitType.Knight: 25,
            UnitType.Archer: 45,
            UnitType.Giant: 200,
            UnitType.Queen: 200,
        }
        return _max_hp.get(self)

    @property
    def speed(self) -> Optional[int]:
        _unit_speed = {
            UnitType.Knight: 100,
            UnitType.Archer: 75,
            UnitType.Giant: 50,
            UnitType.Queen: 60,
        }
        return _unit_speed.get(self)

    @property
    def numbers(self) -> Optional[int]:
        _unit_numbers = {
            UnitType.Knight: 4,
            UnitType.Archer: 2,
            UnitType.Giant: 1,
        }
        return _unit_numbers.get(self)

    @property
    def training_time(self) -> Optional[int]:
        _training_time = {
            UnitType.Knight: 5,
            UnitType.Archer: 8,
            UnitType.Giant: 10,
        }
        return _training_time.get(self)


def neg_is_none(value: int) -> Optional[int]:
    return value if value >= 0 else None


def debug(msg: str):
    if DEBUG:
        print(f"D {msg}", file=sys.stderr, flush=True)


def info(msg: str):
    print(f"I {msg}", file=sys.stderr, flush=True)


def warning(msg: str):
    info('====')
    info(msg)
    info('====')


def log_input(input_str: str):
    if DEBUG:
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

    max_distance = 1920 * 1000


@dataclasses.dataclass
class BuildingSite(Coordinate):
    site_id: int
    radius: int

    structure: StructureType = StructureType.NoStructure
    owner: OwnerType = OwnerType.NoOwner
    # amount of gold left to mine
    gold: Optional[int] = None
    # maximum amount minable from the site
    max_mine_size: Optional[int] = None
    # When goldmine: income between 1 and 5
    # When tower: remaining HP
    # When barracks: turns before new creep can be trained
    param_1: Optional[int] = None
    # When tower: attack radius from center
    # When barracks: the creep type
    param_2: Optional[int] = None

    distance_from_my_queen: float = Coordinate.max_distance
    distance_from_their_queen: float = Coordinate.max_distance

    @property
    def income(self) -> Optional[int]:
        if self.structure == StructureType.Goldmine:
            return self.param_1

    @property
    def remaining_hp(self) -> Optional[int]:
        if self.structure == StructureType.Tower:
            return self.param_1

    @property
    def training_delay(self) -> Optional[int]:
        if self.structure == StructureType.Barracks:
            return self.param_1

    @property
    def attack_radius(self) -> Optional[int]:
        if self.structure == StructureType.Tower:
            return self.param_2

    @property
    def barrack_type(self) -> Optional[UnitType]:
        if self.structure == StructureType.Barracks:
            return UnitType(self.param_2)

    @property
    def site_id_str(self) -> str:
        return f'B-{self.site_id}'

    def __str__(self):
        if self.structure == StructureType.Barracks:
            return f'{self.site_id_str} {self.structure.name}-{self.barrack_type.name} delay={self.training_delay}'
        elif self.structure == StructureType.Goldmine:
            return f'{self.site_id_str} {self.structure.name} income={self.income} max_size={self.max_mine_size}'
        return f'{self.site_id_str} {self.structure.name} {self.owner.name} {Coordinate.__str__(self)}'

    def update(self, **kwargs):
        change = []
        for f in dataclasses.fields(self):
            v = kwargs.get(f.name)
            if v is not None and v != getattr(self, f.name):
                setattr(self, f.name, v)
                change.append(f.name)
        # if change:
        #     debug(f'{self.site_id_str} changed {", ".join(change)} {self}')

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
    def build(cls, building: BuildingSite, what: str):
        return f'BUILD {building.site_id} {what}'

    @classmethod
    def build_barracks(cls, building: BuildingSite, unit_type: UnitType):
        return cls.build(building, f'BARRACKS-{unit_type.name.upper()}')

    @classmethod
    def build_tower(cls, building: BuildingSite):
        return cls.build(building, 'TOWER')

    @classmethod
    def build_mine(cls, building: BuildingSite):
        return cls.build(building, 'MINE')

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


class Dummy:

    @classmethod
    def want_barrack(cls, state: "GameState"):
        barrack_type = None

        info(f'Choosing what barrack to build from {({k: len(v.barracks) for k, v in state.unit_info.items()})}')
        n_archer = len(state.unit_info[UnitType.Archer].barracks)
        n_knights = len(state.unit_info[UnitType.Knight].barracks)
        if n_archer < 1 or n_knights > n_archer * 2:
            barrack_type = UnitType.Archer
        elif n_knights < 2:
            barrack_type = UnitType.Knight
        elif len(state.unit_info[UnitType.Giant].barracks) < 1:
            barrack_type = UnitType.Giant

        return barrack_type

    @classmethod
    def want_building(cls, state: "GameState"):
        closest_empty = state.touched_site
        debug(f'Touching {closest_empty}')

        # if (
        #     closest_empty is not None and
        #     closest_empty.owner == OwnerType.Friendly and
        #     closest_empty.structure == BuildingsType.Goldmine and
        #     closest_empty.income < 3
        # ):
        #     debug('Improving mine!')
        #     return Command.build_mine(closest_empty)

        if closest_empty is None or closest_empty.owner != OwnerType.NoOwner:
            # No touching a site that is ours, look for one
            closest_empty = state.closest_building_to_queen(not_owner=OwnerType.Friendly)

        if closest_empty:
            debug(f'Choosing what to build on {closest_empty}')
            mines = state.get_sites(owner=OwnerType.Friendly, structure=StructureType.Goldmine)
            # towers = state.get_sites(owner=OwnerType.Friendly, structure=BuildingsType.Tower)
            expected_income = sum((m.income for m in mines))

            if not state.unit_info[UnitType.Archer].barracks:
                # Defensive: start with archers
                return Command.build_barracks(closest_empty, UnitType.Archer)

            if expected_income == 0:
                debug('We have no income!')
                return Command.build_mine(closest_empty)

            improvable_mines = state.get_sites(owner=OwnerType.Friendly, income_le=4)
            if improvable_mines:
                closest_empty = sorted(improvable_mines, key=attrgetter('distance_from_my_queen'))[0]
                info(f'Improving one of the {len(improvable_mines)} mines: => {closest_empty}')
                return Command.build_mine(closest_empty)

            barrack_type = cls.want_barrack(state)

            if barrack_type is not None:
                debug(f'Building a BARRACK-{barrack_type.name.upper()} on {closest_empty}')
                return Command.build_barracks(closest_empty, barrack_type)

            my_towers = state.get_sites(owner=OwnerType.Friendly, structure=StructureType.Tower)
            if (
                2 * len(my_towers) < len(state.get_sites(owner=OwnerType.Friendly, structure=StructureType.Barracks))
            ):
                return Command.build_tower(closest_empty)

            # TODO(tr) Improve tower ranges

            if len(mines) < len(state.unit_info[UnitType.Knight].barracks) * 2:
                return Command.build_mine(closest_empty)
            else:
                debug('Knight barrack default')
                return Command.build_barracks(closest_empty, UnitType.Knight)
            # We could also recycle old mines

            debug(f'Ignoring {closest_empty}')

    def queen_action(self, state: "GameState") -> str:
        # dummy: we're closed to an empty site: build something
        build_command = self.want_building(state)
        if build_command is not None:
            return build_command

        # Nowhere to go, more logic to avoid enemy (maybe do that first?)
        closest_enemy = state.closest_enemy()
        if closest_enemy and state.my_queen.distance(closest_enemy) < (UnitType.Queen.speed * 3):
            debug(f'Evading from {closest_enemy}')
            return Command.move_to(state.my_queen.get_away(closest_enemy))

        closest_empty = state.closest_building_to_queen(owner=OwnerType.Enemy)
        if closest_empty:
            debug(f'Evading from enemy buildings')
            return Command.move_to(state.my_queen.get_away(closest_empty))

        return Command.wait()

    def train_action(self, state: "GameState") -> str:
        buildings: List[BuildingSite] = []
        gold = state.gold

        # Defensive: build archers first
        if (
            state.get_sites(owner=OwnerType.Enemy, structure=StructureType.Tower)
            and not state.unit_info[UnitType.Giant].allies
        ):
            for b in state.unit_info[UnitType.Giant].barracks:
                if b.training_delay == 0 and gold >= UnitType.Giant.cost:
                    gold -= UnitType.Giant.cost
                    buildings.append(b)
                    break  # one at a time
            else:
                # TODO(tr) When saving maybe change behaviour to be less agressive and improve more
                return Command.train(buildings)  # Saving money

        if (
            state.unit_info[UnitType.Archer].barracks
            and len(state.unit_info[UnitType.Archer].allies) < len(state.get_sites(owner=OwnerType.Enemy, structure=StructureType.Barracks))
        ):
            if gold >= UnitType.Archer.cost:
                # prioritise by proximity to my queen
                for b in sorted(state.unit_info[UnitType.Archer].barracks, key=attrgetter('distance_from_my_queen')):
                    if b.training_delay == 0 and gold >= UnitType.Archer.cost:
                        gold -= UnitType.Archer.cost
                        buildings.append(b)
                        break  # one at a time
                # else:
                #     # TODO(tr) When saving maybe change behaviour to be less agressive and improve more
                #     return Command.train(buildings)  # Saving money

        if state.unit_info[UnitType.Knight].barracks:
            # Prioritise by proximity to enemy queen
            for b in sorted(state.unit_info[UnitType.Knight].barracks, key=attrgetter('distance_from_their_queen')):
                if b.training_delay:
                    continue
                if gold < UnitType.Knight.cost:
                    break  # cannot afford more
                buildings.append(b)

        return Command.train(buildings)


@dataclasses.dataclass
class UnitInfo:
    allies: List[Unit] = dataclasses.field(default_factory=list)
    enemies: List[Unit] = dataclasses.field(default_factory=list)
    barracks: List[BuildingSite] = dataclasses.field(default_factory=list)

    @classmethod
    def empty_dict(cls) -> Dict[UnitType, "UnitInfo"]:
        return {
            k: UnitInfo()
            for k in UnitType
            if k != UnitType.Queen
        }


@dataclasses.dataclass
class GameState:
    gold: int = 0
    touched_site_id: Optional[int] = None

    site_map: Dict[int, BuildingSite] = dataclasses.field(default_factory=dict)

    my_queen: Unit = None
    their_queen: Unit = None
    unit_info: Dict[UnitType, UnitInfo] = dataclasses.field(default_factory=UnitInfo.empty_dict)

    personality: Dummy = dataclasses.field(default_factory=Dummy)

    @property
    def enemies(self):
        for v in self.unit_info.values():
            for u in v.enemies:
                yield u

    @property
    def allies(self):
        for v in self.unit_info.values():
            for u in v.allies:
                yield u

    @property
    def num_sites(self) -> int:
        return len(self.site_map)

    @property
    def touched_site(self) -> Optional[BuildingSite]:
        if self.touched_site_id is not None:
            return self.site_map[self.touched_site_id]

    def get_sites(
        self,
        owner: OwnerType = None,
        not_owner: OwnerType = None,
        structure: StructureType = None,
        not_structure: StructureType = None,
        barrack_type: UnitType = None,
        income_le: int = None,
    ) -> List[BuildingSite]:
        return [
            s
            for s in self.site_map.values()
            if all((
                (owner is None or s.owner == owner),
                (not_owner is None or s.owner != not_owner),
                (structure is None or s.structure == structure),
                (not_structure is None or s.structure != not_structure),
                # It needs to be a built to count!
                (barrack_type is None or s.barrack_type == barrack_type),
                # Improvable mines
                (income_le is None or (s.income is not None and s.income <= income_le and s.income < s.max_mine_size)),
            ))
        ]

    def get_allies(self, unit_type: UnitType) -> List[Unit]:
        return self.unit_info[unit_type].allies

    def get_enemies(self, unit_type: UnitType) -> List[Unit]:
        return self.unit_info[unit_type].enemies

    def print_state(self):
        info(
            f'G={self.gold} my_queen={self.my_queen} with {len(list(self.allies))} units'
            f' and {len(self.get_sites(owner=OwnerType.Friendly))} buildings'
        )
        info(
            f'Enemy queen={self.their_queen} with {len(list(self.enemies))} units '
            f'and {len(self.get_sites(owner=OwnerType.Enemy))} buildings'
        )

    def add_site(self, site: BuildingSite):
        # debug(f'Discovering {site}')
        self.site_map[site.site_id] = site

    def _clear_state(self):
        self.touched_site_id = None
        self.unit_info = UnitInfo.empty_dict()

    def update_from_input(self):
        self._clear_state()

        input_list = [int(j) for j in game_input().split()]
        self.gold = input_list[0]

        self.touched_site_id = neg_is_none(input_list[1])

        for i in range(self.num_sites):
            self._update_map_from_input(game_input())

        num_units = int(game_input())
        for i in range(num_units):
            self._update_units_from_input(game_input())

        self._update_distance_from_queens()

    def _update_map_from_input(self, input_str: str):
        # site_id, gold, maxMineSize, structure_type, owner, param_1, param_2 = [int(j) for j in input_str.split()]
        input_list = [int(j) for j in input_str.split()]

        site = self.site_map[input_list[0]]
        site.update(
            gold=input_list[1],
            max_mine_size=input_list[2],
            structure=StructureType(input_list[3]),
            owner=OwnerType(input_list[4]),
            param_1=neg_is_none(input_list[5]),
            param_2=neg_is_none(input_list[6]),
        )

        if (
            site.structure == StructureType.Barracks and site.owner == OwnerType.Friendly
            and site.barrack_type is not None
        ):
            self.unit_info[site.barrack_type].barracks.append(site)

    def _update_distance_from_queens(self):
        for b in self.site_map.values():
            b.distance_from_my_queen = self.my_queen.distance(b)
            b.distance_from_their_queen = self.their_queen.distance(b)

    def _update_units_from_input(self, input_str: str):
        unit = Unit.from_input(input_str)

        if unit.owner == OwnerType.Friendly:
            if unit.unit_type == UnitType.Queen:
                self.my_queen = unit
            else:
                self.unit_info[unit.unit_type].allies.append(unit)
        elif unit.owner == OwnerType.Enemy:
            if unit.unit_type == UnitType.Queen:
                self.their_queen = unit
            else:
                self.unit_info[unit.unit_type].enemies.append(unit)

    def closest_building_to_queen(self, owner: OwnerType=None, not_owner: OwnerType=None):
        debug(f'Looking for closest owner={owner} not_owner={not_owner} building to the queen')
        # Ignore towers if possible, they hurt.
        sites = self.get_sites(owner=owner, not_owner=not_owner, not_structure=StructureType.Tower)
        if not sites:
            # Try again without ignoring towers
            sites = self.get_sites(owner=owner, not_owner=not_owner)
        if sites:
            return sorted(sites, key=attrgetter('distance_from_my_queen'))[0]

    def closest_enemy(self):
        debug('Looking for the closest enemy')
        # TODO(tr) We could ignore enemies that have little life
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
        return self.personality.queen_action(self)

    def train_action(self) -> str:
        return self.personality.train_action(self)

    def choose_personality(self):
        pass  # TODO(tr) Change personality if needed

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

        info('Checking personality')
        state.choose_personality()

        info('Choosing queen action')
        # First line: A valid queen action
        queen_action = state.queen_action()
        print(queen_action)
        info('Choosing train action')
        # Second line: A set of training instructions
        train_action = state.train_action()
        print(train_action)

        # TODO(tr) if we are stuck in decision make something else...


if __name__ == '__main__':
    play()
