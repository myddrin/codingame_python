from typing import Tuple

import pytest

from .easily_distracted import (
    Card,
    count_cards,
    get_bust_chance,
)


class TestCard:

    @pytest.mark.parametrize('values, cards', (
        ('JT7A44', [Card.Jack, Card.Ten, Card.N7, Card.Ace, Card.N4, Card.N4]),
    ))
    def test_from_string_valid(self, values, cards):
        assert Card.from_string(values) == cards

    @pytest.mark.parametrize('values', (
        'JAKE',
        'AT&T',
        'T1',
    ))
    def test_from_string_invalid(self, values):
        assert Card.from_string(values) == []

    @pytest.mark.parametrize('card', list(Card))
    def test_all_cards_have_face_value(self, card):
        assert card.face_value is not None

    @pytest.mark.parametrize('card, exp_value', (
        (Card.King, 10),
        (Card.Queen, 10),
        (Card.Jack, 10),
        (Card.Ten, 10),
        (Card.Ace, 1),
    ))
    def test_special_card_values(self, card, exp_value):
        assert card.face_value == exp_value


class TestCountCards:

    def test_example(self):
        assert count_cards(['JT7A44', 'JAKE', 'AT&T', 'T1', 'KQ']) == {
            Card.King: 3,
            Card.Queen: 3,
            Card.Jack: 3,
            Card.Ten: 3,
            Card.N9: 4,
            Card.N8: 4,
            Card.N7: 3,
            Card.N6: 4,
            Card.N5: 4,
            Card.N4: 2,
            Card.N3: 4,
            Card.N2: 4,
            Card.Ace: 3,
        }


class TestBustChance:

    @pytest.mark.parametrize('cards, bust, exp_bust', (
        (
            [
                ('2', 3), ('3', 3), ('4', 3), ('5', 4), ('6', 4), ('7', 4), ('8', 4), ('9', 4), ('T', 4), ('J', 4),
                ('Q', 4), ('K', 4), ('A', 4)
            ],
            4,
            0.67
        ),
        (
            [
                ('A', 4), ('T', 2), ('3', 4), ('7', 3), ('J', 4), ('9', 2), ('5', 3), ('2', 3), ('4', 4), ('8', 4),
                ('Q', 4), ('6', 4), ('K', 3)
            ],
            7,
            0.25,
        ),
        (
            [
                ('9', 3), ('J', 1), ('4', 2), ('T', 4), ('7', 2), ('A', 4), ('5', 3), ('Q', 1), ('3', 3), ('6', 4),
                ('K', 1), ('2', 1),
            ],
            10,
            0.61,
        ),
    ))
    def test_example(self, cards, bust, exp_bust):
        left_cards = {
            Card(card[0]): 4 - card[1]
            for card in cards  # type: Tuple[str, int]
        }
        found = get_bust_chance(left_cards, bust)
        assert f'{found:.2f}' == f'{exp_bust:.2f}'
