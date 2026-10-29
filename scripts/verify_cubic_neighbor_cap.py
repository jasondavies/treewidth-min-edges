#!/usr/bin/env python3
"""Verify the 23-vertex cubic-neighbor cap relative to earlier classifications.

The bounded C order finder is untrusted. Every successful order is checked
by independent Python set fills. Failure to find an order never proves a bound. The opt-in --without-isolate
flag checks the stronger theorem; the default family remains unchanged.
"""
import argparse
from collections import Counter
from contextlib import contextmanager
import ctypes
from hashlib import sha256
import json
import os
from pathlib import Path
import shlex
import struct
import subprocess
import tempfile
import time

from cubic_cap_reconstruction import (
    intermediate_graphs, require, target_lifts, universal_apex, validate_graph, verify_order,
)


@contextmanager
def order_proposer(*, native=False, compiler=None):
    command = shlex.split(os.environ.get('CC', 'cc') if compiler is None else compiler)
    require(bool(command), 'The compiler command is empty')
    source = Path(__file__).resolve().with_name('cubic_cap_order.c')
    with tempfile.TemporaryDirectory(prefix='cubic-cap-') as directory:
        library = Path(directory) / 'orders.so'
        result = subprocess.run(command + ['-O3', '-std=c11', '-shared', '-fPIC']
                                + (['-march=native'] if native else [])
                                + [str(source), '-o', str(library)], capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError('Could not compile the untrusted order finder:\n' + result.stderr)
        loaded = ctypes.CDLL(str(library))
        propose = loaded.propose
        propose.argtypes = [ctypes.POINTER(ctypes.c_uint32), ctypes.c_int, ctypes.c_int,
                            ctypes.POINTER(ctypes.c_ubyte)]
        propose.restype = ctypes.c_int

        def find(graph, width):
            validate_graph(graph)
            require(type(width) is int and 0 <= width < len(graph), 'Invalid width')
            out = (ctypes.c_ubyte * len(graph))()
            attempts = propose((ctypes.c_uint32 * len(graph))(*graph), len(graph), width, out)
            require(attempts >= 0, 'Native order finder rejected its input')
            return None if attempts == 0 else list(out)

        yield find


def check(repository, propose, *, all_lifts=False, without_isolate=False):
    """Exhaust the inverse family; ``None`` from the proposer is only unknown."""
    require(type(without_isolate) is bool, 'without_isolate must be a boolean')
    started = time.monotonic()
    counts, lifted = Counter(), Counter()
    digest = sha256()
    for _, _, graph in intermediate_graphs(repository, counts):
        order = propose(graph, 7)
        if order is not None:
            verify_order(graph, order, 7)
            verify_order(universal_apex(graph), list(order) + [20], 8)
            counts['universal_apex_orders'] += 1
            if not all_lifts:
                continue
        else:
            counts['individual_lift_families'] += 1
        for _, _, target in target_lifts(graph, lifted, require_isolate=not without_isolate):
            order = propose(target, 8)
            require(order is not None, 'Bounded search did not find a lifted width-eight order')
            verify_order(target, order, 8)
            counts['checked_lifts'] += 1
            digest.update(struct.pack('<23I', *target))
    return {'status': 'verified-relative-to-prior-classifications',
            'all_lifts': all_lifts, 'requires_isolated_cubic': not without_isolate, 'intermediate': dict(counts), 'lifts': dict(lifted),
            'checked_graph_sha256': digest.hexdigest(), 'seconds': time.monotonic() - started}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--native', action='store_true')
    parser.add_argument('--compiler')
    parser.add_argument('--all-lifts', action='store_true',
                        help='also check each lift covered by a universal-apex order')
    parser.add_argument('--without-isolate', action='store_true',
                        help='check the stronger theorem without requiring an isolated cubic')
    args = parser.parse_args()
    with order_proposer(native=args.native, compiler=args.compiler) as propose:
        report = check(args.repository, propose, all_lifts=args.all_lifts, without_isolate=args.without_isolate)
    print(json.dumps(report, sort_keys=True))


if __name__ == '__main__':
    main()
