import pytest

from .dwarfs_on_giants import (
    longest_influence_chain,
    Person,
)


@pytest.fixture(autouse=True)
def clean_person():
    Person.people = {}


class TestPerson:
    load_1 = [(1, 2), (1, 3), (3, 4)]
    expected_1 = {
        1: [2, 3],
        2: [],
        3: [4],
        4: [],
    }
    load_2 = load_1 + [(2, 5), (2, 4)]
    expected_2 = {
        1: [2, 3],
        2: [4, 5],
        3: [4],
        4: [],
        5: [],
    }
    load_3 = load_2 + [(10, 1), (10, 3), (10, 11)]
    expected_3 = {
        1: [2, 3],
        2: [4, 5],
        3: [4],
        4: [],
        5: [],
        10: [1, 3, 11],
        11: [],
    }

    @pytest.mark.parametrize('act, exp', (
        (load_1, expected_1),
        (load_2, expected_2),
        (load_3, expected_3),
    ))
    def test_load(self, act, exp):
        people = Person.load(act)
        assert people is Person.people

        assert sorted(people.keys()) == sorted(exp.keys())
        for k, p in people.items():
            assert p.name == k
            assert sorted(p.has_influence_over) == exp[k]

    @pytest.mark.parametrize('act, exp_name, exp', (
        (load_1, 1, [1, 3, 4]),
        # (load_2, 1, [1, 2, 5]),  # both are valid but our algorithm pick only the 2nd one
        (load_2, 1, [1, 3, 4]),
        # (load_3, 10, [10, 1, 2, 5]),
        (load_3, 10, [10, 1, 3, 4]),
    ))
    def test_best_chain_result(self, act, exp_name, exp):
        rv = longest_influence_chain(Person.load(act).values())
        assert isinstance(rv, Person)
        assert rv.name == exp_name
        best_chain = rv.best_influence_chain
        assert [
            p.name
            for p in best_chain
        ] == exp
