from operator import itemgetter

import pytest as pytest

from codingame.code_of_the_rings.run_code_of_the_rings import process
from codingame.code_of_the_rings.code_of_the_rings import (
    Action,
    ASCII_MAP,
    Processor,
    run_all,
)
from codingame.utils import read_package_resource


TEST_RESOURCES = 'codingame.code_of_the_rings'


class TestAction:
    @pytest.mark.parametrize('v', list(Action))
    def test_all_reversible(self, v):
        v.reverse()  # should not raise

    @pytest.mark.parametrize('v', list(Action))
    @pytest.mark.parametrize('n', (0, 1, 10))
    def test_repeat(self, v, n):
        assert len(v.repeat(n)) == n

    @pytest.mark.parametrize('v', list(Action))
    @pytest.mark.parametrize('n', (-1, -10))
    def test_negative_repeat(self, v, n):
        rv = v.repeat(n)
        assert len(rv) == abs(n)
        assert rv == v.reverse().repeat(-n)


class TestLocalActions:
    @pytest.mark.parametrize('target', list(ASCII_MAP.keys()))
    def test_same(self, target):
        assert Processor.local_actions(target, target) == ''

    @pytest.mark.parametrize('current, target, expected', (
        ('A', ' ', Action.PrevLetter.value),
        ('Z', ' ', Action.NextLetter.value),
        (' ', 'A', Action.NextLetter.value),
        (' ', 'Z', Action.PrevLetter.value),
    ))
    def test_with_space(self, current, target, expected):
        assert Processor.local_actions(current, target) == expected

    @pytest.mark.parametrize('current, target, expected', (
        ('A', 'N', Action.NextLetter.repeat(13)),
        ('A', 'O', Action.PrevLetter.repeat(13)),
    ))
    def test_shortest(self, current, target, expected):
        rv = Processor.local_actions(current, target)
        assert rv == expected, f'given {len(rv)}'


class TestMemoryLocation:

    @pytest.mark.parametrize('target', (
        'AZ',
        'MINAS',
    ))
    def test_no_repeat(self, target):
        assert Processor.memory_location(target) == Processor.static_location(target)

    # one letter x15
    # one letter x31
    # one letter x70


class TestSamples:
    functions = {
        f.__name__: f
        for f in (Processor.static_location, Processor.memory_location)
    }

    @pytest.mark.parametrize('spell', list(read_package_resource(TEST_RESOURCES, 'samples.txt').split('\n')))
    @pytest.mark.parametrize('func_name', list(functions.keys()))
    def test_samples(self, spell, func_name):
        """
        Expecting files that have 3 lines:
        <input>
        <function name>
        <output>
        """
        # remove last line that's empty
        assert process(self.functions[func_name](spell)) == spell

    @pytest.mark.parametrize('spell', list(read_package_resource(TEST_RESOURCES, 'samples.txt').split('\n')))
    def test_best(self, spell):
        by_fn = {
            name: len(actions)
            for name, actions in run_all(spell).items()
        }
        bests = sorted(
            by_fn.items(),
            key=itemgetter(1),
        )
        expected_best = Processor.memory_location.__name__
        assert by_fn[expected_best] == bests[0][1], f'instead best is {bests[0]}'
