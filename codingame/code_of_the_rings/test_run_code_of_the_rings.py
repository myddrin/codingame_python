import pytest

from codingame.code_of_the_rings.run_code_of_the_rings import process
from codingame.utils import read_package_resource


TEST_RESOURCES = 'codingame.code_of_the_rings'


class TestProcess:

    def test_empty(self):
        assert process('') == ''

    @pytest.mark.parametrize('actions', (
        '+.--.',
        '+.>-.',
    ))
    def test_az(self, actions):
        assert process(actions) == 'AZ'

    @pytest.mark.parametrize('actions, expected', (
        ('+>-[<.>-]', ''.join(['A'] * 26)),  # make a Z -> 26 iter
        ('+>+++++[<.>-]', ''.join(['A'] * 5)),  # make a E  -> 5 iter
    ))
    def test_loops(self, actions, expected):
        assert process(actions) == expected

    @pytest.mark.parametrize('filename', (
        'sample1_static.txt',
        'short_spell_static.txt',
        'long_spell_static.txt',
        'entire_alphabet_memory.txt',
    ))
    def test_samples(self, filename):
        """
        Expecting files that have 3 lines:
        <input>
        <function name>
        <output>
        """
        # remove last line that's empty
        spell, _, output = read_package_resource(TEST_RESOURCES, filename).split('\n')[:-1]
        assert process(output) == spell
