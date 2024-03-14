"""
See https://www.codingame.com/ide/puzzle/card-counting-when-easily-distracted
"""
import sys
from collections import defaultdict


def debug(*args, **kwargs):
    print(*args, file=sys.stderr, flush=True, **kwargs)


deck_values = {
    'K': 10,
    'Q': 10,
    'J': 10,
    'T': 10,
    'A': 1,
    **{str(i): i for i in range(2, 10)}
}


def get_bust_chance(words: list[str], bust: int) -> float:
    """Get left over cards"""
    left_cards = {
        card: 4
        for card in deck_values.keys()
    }

    for word in words:
        to_remove = defaultdict(int)
        for card in word:
            if card in deck_values:
                to_remove[card] += 1
            else:  # not a bunch of cards, skip that word
                to_remove = {}
                break

        for card, count in to_remove.items():
            left_cards[card] -= count

    total_above = 0
    total_bellow = 0
    for card, count in left_cards.items():
        if deck_values[card] < bust:
            total_bellow += count
        else:
            total_above += count

    return total_bellow / float(total_above + total_bellow)


if __name__ == '__main__':
    stream_of_consciousness: list[str] = input().split('.')
    bust_threshold = int(input())

    chance = get_bust_chance(stream_of_consciousness, bust_threshold)
    print(f'{chance * 100.0:.0f}%')
