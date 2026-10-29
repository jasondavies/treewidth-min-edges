"""Bounded quartic order programs, with optional untrusted native production.

The caller must independently check every successful returned order.
"""
from contextlib import contextmanager
import ctypes
from itertools import combinations
import os
from pathlib import Path
import shlex
import subprocess
import tempfile


def validate_program(program):
    if (not isinstance(program, tuple) or len(program) not in (1, 2)
            or any(type(v) is not int or not 0 <= v < 26 for v in program)
            or len(set(program)) != len(program)):
        raise ValueError('Invalid one- or two-vertex order prefix.')


def read_program(data):
    try:
        tag = next(data)
        if type(tag) is not int:
            raise ValueError('Invalid order-program tag.')
        if 0 <= tag < 26:
            program = (tag,)
        elif tag == 26:
            program = (next(data), next(data))
        else:
            raise ValueError('Invalid order-program tag.')
    except StopIteration as error:
        raise ValueError('The certificate ended within or before an order program.') from error
    validate_program(program)
    return program


def encode_program(program):
    validate_program(program)
    return bytes(program if len(program) == 1 else (26, *program))


def interpret_program(graph, program):
    """Execute at most 26 elimination steps, with no search or backtracking."""
    validate_program(program)
    if len(graph) != 26:
        raise ValueError('An order program requires 26 vertices.')
    current = {v: set(row) for v, row in enumerate(graph)}
    order = []
    while current:
        def score(v):
            neighbors = current[v]
            fill = sum(w not in current[u] for u, w in combinations(neighbors, 2))
            return fill, len(neighbors), v

        vertex = program[len(order)] if len(order) < len(program) else min(current, key=score)
        neighbors = current.pop(vertex)
        if len(neighbors) > 10:
            return None
        order.append(vertex)
        for u in neighbors:
            current[u].remove(vertex)
            current[u].update(neighbors - {u})
    return order


def propose_program(graph, interpreter=interpret_program):
    """Generation only: try single vertices, then distinct ordered pairs."""
    for first in range(26):
        program = (first,)
        order = interpreter(graph, program)
        if order is not None:
            return program, order
    for first in range(26):
        for second in range(26):
            if first == second:
                continue
            program = (first, second)
            order = interpreter(graph, program)
            if order is not None:
                return program, order
    raise ValueError('No width-ten order found using the available prefixes.')


@contextmanager
def native_interpreter(compiler=None):
    """Compile an optional proposer; its output still requires Python checking."""
    command = shlex.split(compiler or os.environ.get('CC', 'cc'))
    if not command:
        raise ValueError('The C compiler command is empty.')
    source = Path(__file__).with_name('quartic_order_program.c')
    with tempfile.TemporaryDirectory(prefix='quartic-order-program-') as directory:
        library_path = Path(directory) / 'order-program.so'
        result = subprocess.run(
            command + ['-O3', '-std=c11', '-Wall', '-Wextra', '-Werror',
                       '-fPIC', '-shared', str(source), '-o', str(library_path)],
            capture_output=True, text=True,
        )
        if result.returncode:
            raise ValueError('Could not compile the optional order helper:\n' + result.stderr)
        library = ctypes.CDLL(str(library_path))
        function = library.minfill26_prefix
        function.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.c_int,
                             ctypes.c_int, ctypes.POINTER(ctypes.c_ubyte)]
        function.restype = ctypes.c_int

        def interpret(graph, program):
            validate_program(program)
            if len(graph) != 26:
                raise ValueError('An order program requires 26 vertices.')
            masks = (ctypes.c_uint32 * 26)(*(sum(1 << u for u in row) for row in graph))
            order = (ctypes.c_ubyte * 26)()
            second = program[1] if len(program) == 2 else -1
            if function(masks, program[0], second, order):
                return list(order)
            return None

        yield interpret
