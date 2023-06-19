"""
https://www.codingame.com/ide/puzzle/logic-gates
"""

from typing import (
    Dict,
    List,
)


def signal_from_str(v: str) -> bool:
    return v == '-'


def signal_to_str(s: bool) -> str:
    if s:
        return '-'
    return '_'


def apply_and(a: List[bool], b: List[bool]) -> List[bool]:
    assert len(a) == len(b), 'sanity'
    return [
        a[i] & b[i]
        for i in range(len(a))
    ]


def apply_or(a: List[bool], b: List[bool]) -> List[bool]:
    assert len(a) == len(b), 'sanity'
    return [
        a[i] | b[i]
        for i in range(len(a))
    ]


def apply_xor(a: List[bool], b: List[bool]) -> List[bool]:
    assert len(a) == len(b), 'sanity'
    return [
        a[i] ^ b[i]
        for i in range(len(a))
    ]


def apply_not(a: List[bool]) -> List[bool]:
    return [not v for v in a]


def process_signals() -> Dict[str, List[bool]]:
    n_inputs = int(input())
    n_outputs = int(input())
    input_signals = {}
    for _ in range(n_inputs):
        input_name, input_signal = input().split()
        input_signals[input_name] = list(map(signal_from_str, list(input_signal)))

    output_signals = {}
    for _ in range(n_outputs):
        output_name, operation, input_name_1, input_name_2 = input().split()
        a = input_signals[input_name_1]
        b = input_signals[input_name_2]

        negate = operation.startswith('N')
        if negate:
            operation = operation[1:]

        if operation == 'AND':
            values = apply_and(a, b)
        elif operation == 'OR':
            values = apply_or(a, b)
        elif operation == 'XOR':
            values = apply_xor(a, b)
        else:
            raise ValueError(f'Unexpected op: {operation}')

        if negate:
            values = apply_not(values)
        output_signals[output_name] = values

    return output_signals


if __name__ == '__main__':
    output_signals = process_signals()
    for name, values in output_signals.items():
        print(f'{name} {"".join(map(signal_to_str, list(values)))}')
