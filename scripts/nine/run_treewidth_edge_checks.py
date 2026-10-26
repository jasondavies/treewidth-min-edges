"""Shared compilation, graph6, and independent certificate helpers."""
import hashlib
import os
from pathlib import Path
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "scripts/nine/treewidth_edge_geng.c"
GENG = Path(os.environ.get("GENG_SOURCE", "/usr/share/nauty/geng.c"))
CC = shlex.split(os.environ.get("CC", "cc"))

def run(args, **kwargs):
    return subprocess.run([str(x) for x in args], check=True, text=True,
                          capture_output=True, **kwargs)

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def encode(a):
    bits = [int(j in a[i]) for j in range(1, len(a)) for i in range(j)]
    bits += [0] * ((-len(bits)) % 6)
    return chr(len(a) + 63) + "".join(
        chr(63 + sum(bits[i + j] << (5 - j) for j in range(6)))
        for i in range(0, len(bits), 6))

def masks(a):
    return tuple(sum(1 << w for w in ns) for ns in a)

def verify_order(a, order, bound):
    """Set-based fill verifier, independent of the C path-based verifier."""
    assert sorted(order) == list(range(len(a)))
    current = [set(ns) for ns in a]
    remaining = set(range(len(a)))
    width = 0
    for v in order:
        ns = current[v] & remaining
        width = max(width, len(ns))
        assert len(ns) <= bound
        for w in ns:
            current[w].update(ns - {w})
        remaining.remove(v)
    return width
