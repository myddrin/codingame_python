"""
See https://www.codingame.com/ide/puzzle/card-counting-when-easily-distracted
"""
import enum
import sys
from typing import (
    Dict,
    Optional,
)


def debug(*args, **kwargs):
    print(*args, file=sys.stderr, flush=True, **kwargs)


class Card(enum.Enum):
    King = 'K'
    Queen = 'Q'
    Jack = 'J'
    Ten = 'T'
    N9 = '9'
    N8 = '8'
    N7 = '7'
    N6 = '6'
    N5 = '5'
    N4 = '4'
    N3 = '3'
    N2 = '2'
    Ace = 'A'

    @classmethod
    def from_string(cls, values: str) -> list['Card']:
        cards = []
        for character in values:
            try:
                card = cls(character)
            except ValueError:
                return []
            else:
                cards.append(card)
        return cards

    @property
    def face_value(self) -> int:
        if self in (self.King, self.Queen, self.Jack, self.Ten):
            return 10
        elif self == self.Ace:
            return 1
        else:
            return int(self.value)


def count_cards(words: list[str]) -> Dict[Card, int]:
    """Get left over cards"""
    count_cards = {
        card: 4
        for card in Card
    }

    for word in words:
        for card in Card.from_string(word):
            count_cards[card] -= 1

    return count_cards


def get_bust_chance(left_cards: Dict[Card, int], bust: int) -> float:
    total_above = 0
    total_bellow = 0
    for card, count in left_cards.items():
        if card.face_value < bust:
            total_bellow += count
        else:
            total_above += count

    return total_bellow / float(total_above + total_bellow)


if __name__ == '__main__':
    stream_of_consciousness: list[str] = input().split('.')
    bust_threshold = int(input())

    cards = count_cards(stream_of_consciousness)
    change = get_bust_chance(cards, bust_threshold)
    print(f'{change * 100.0:.0f}%')
