from operator import itemgetter
from typing import Dict

from codingame.code_of_the_rings.code_of_the_rings import (
    ASCII_MAP,
    N_STATES,
    Action,
    Processor,
)


def process(actions: str) -> str:
    current_idx = 0
    ascii_index_map = {
        i: k
        for i, k in enumerate(ASCII_MAP.keys())
    }
    current_state = [len(ascii_index_map) - 1] * N_STATES
    assert ascii_index_map[current_state[0]] == ' '

    output = []
    act_idx = 0
    loop_back_refs: Dict[int, int] = {}  # closing idx -> opening idx
    loop_fwrd_refs: Dict[int, int] = {}  # opening idx -> closing idx

    while act_idx < len(actions):
        act = Action(actions[act_idx])

        if act == Action.Commit:
            output.append(current_state[current_idx])
        elif act == Action.GoLeft:
            current_idx = (current_idx - 1) % N_STATES
        elif act == Action.GoRight:
            current_idx = (current_idx + 1) % N_STATES
        elif act == Action.NextLetter:
            current_state[current_idx] = (current_state[current_idx] + 1) % len(ascii_index_map)
        elif act == Action.PrevLetter:
            current_state[current_idx] = (current_state[current_idx] - 1) % len(ascii_index_map)
        elif act == Action.StartLoop:
            if act_idx not in loop_fwrd_refs:
                try:
                    closing = actions.index(Action.EndLoop.value, act_idx)
                except ValueError:
                    raise RuntimeError(f'Unclosed loop at {act_idx}')
                else:
                    loop_fwrd_refs[act_idx] = closing
                    loop_back_refs[closing] = act_idx + 1  # skip the loop opening - it won't be space

            if ascii_index_map[current_state[current_idx]] == ' ':
                act_idx = loop_fwrd_refs[act_idx]
                continue  # jump forward
            # otherwise run the loop!
        elif act == Action.EndLoop:
            if ascii_index_map[current_state[current_idx]] != ' ':
                act_idx = loop_back_refs[act_idx]
                continue  # jump back - die if there was no ref
            # else continue - loop is finished
        else:
            raise ValueError(f'Unsupported {act}')

        act_idx += 1

    return ''.join((
        ascii_index_map[o]
        for o in output
    ))


def main():
    import argparse
    functions = {
        fn.__name__: fn
        for fn in (
            Processor.static_location,
            Processor.memory_location,
        )
    }

    parser = argparse.ArgumentParser()
    parser.add_argument('spell')
    parser.add_argument('--function', choices=sorted(functions.keys()), default=None)
    args = parser.parse_args()
    spell = args.spell.upper()
    sizes = {}

    for fn_name, fn in functions.items():
        if args.function is None or fn_name == args.function:
            print(f'Using {fn_name} to encode "{spell}"')
            given_actions = fn(spell)
            sizes[fn_name] = len(given_actions)
            print(f'Decoding {len(given_actions)} actions...')
            if process(given_actions) != spell:
                raise RuntimeError('Mismatch')
            print(f'{fn_name} OK!')
            print()

    if len(sizes) > 0:
        print('Performance:')
        for fn_name, size in sorted(sizes.items(), key=itemgetter(1)):
            print(f'{fn_name} = {size}')


if __name__ == '__main__':
    main()
