"""
https://www.codingame.com/ide/puzzle/dwarfs-standing-on-the-shoulders-of-giants
"""
import dataclasses
import sys
from typing import (
    ClassVar,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
)


def debug(*args, **kwargs):
    print(*args, file=sys.stderr, flush=True, **kwargs)


@dataclasses.dataclass
class Person:
    people: ClassVar[Dict[int, 'Person']] = {}

    name: int

    has_influence_over: List[int] = dataclasses.field(default_factory=list)
    _best_influence_chain: List['Person'] = None

    def __post_init__(self):
        self.people[self.name] = self

    def _compute_best_influence_chain(self) -> List['Person']:
        if not self.has_influence_over:
            return [self]

        all_chains = []
        for other in self.has_influence_over:
            all_chains.append(self.get(other).best_influence_chain)

        best_chain = sorted(all_chains, key=lambda o: len(o))[-1]
        # we could change that to get all the chains that have the maximum len
        return [self] + best_chain

    @property
    def best_influence_chain(self) -> List['Person']:
        if self._best_influence_chain is None:
            self._best_influence_chain = self._compute_best_influence_chain()
        return self._best_influence_chain

    def add_influence_on(self, other: 'Person'):
        self.has_influence_over.append(other.name)

    @classmethod
    def get(cls, whom: int) -> 'Person':
        obj = cls.people.get(whom)
        if obj is None:
            obj = cls(whom)  # registered in post-init
        return obj

    @classmethod
    def load(cls, actions: List[Tuple[int, int]]) -> Dict[int, 'Person']:
        """return the list of people that have no influence, the people are stored in Person.people"""
        for x, y in actions:
            # x: a relationship of influence between two people (x influences y)
            Person.get(x).add_influence_on(Person.get(y))

        return Person.people


def load_inputs() -> List[Tuple[int, int]]:
    n = int(input())  # the number of relationships of influence
    actions = []
    for _ in range(n):
        x, y = input().split()
        actions.append((int(x), int(y)))
    return actions


def longest_influence_chain(people: Iterable[Person]) -> Optional[Person]:
    if not people:
        return None
    return sorted(people, key=lambda o: len(o.best_influence_chain))[-1]
    # if we wanted them all:
    # p_to_len = {
    #     p.name: len(p.best_influence_chain)
    #     for p in people
    # }
    # best_len = sorted(people, key=lambda o: len(o[1]))[-1]
    # return [
    #     p
    #     for p, influence_len in p_to_len.items()
    #     if influence_len == best_len
    # ]


if __name__ == '__main__':
    # The number of people involved in the longest succession of influences
    debug('N')
    edges = load_inputs()
    if not edges:
        print(0)
        sys.exit()

    Person.load(edges)
    longuest = longest_influence_chain(Person.people.values())  # can have more than one
    debug(f'{longuest.name}: {"->".join((str(o.name) for o in longuest.best_influence_chain))}')
    print(len(longuest.best_influence_chain))
