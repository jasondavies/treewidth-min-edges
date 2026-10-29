#!/usr/bin/env python3
"""Check a complete 52-edge profile exclusion, relative to f(9) >= 42.

Only the Python standard library is needed. No search, nauty, checkpoint,
or stored success report is used. The external mathematical premise is
explicit: every graph of treewidth at least nine has at least 42 edges.
"""
import argparse
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


class Interval:
    """Overapproximate every graph compatible with the initial profile."""

    def __init__(self, prefix):
        require(isinstance(prefix, list) and len(prefix) >= 2
                and all(type(x) is int for x in prefix), 'Invalid prefix.')
        n, start, *masks = prefix
        require(21 <= n <= 26 and len(masks) == n and 0 <= start <= n,
                'Invalid profile dimensions.')
        require(all(0 <= a < 1 << n for a in masks), 'Invalid adjacency mask.')
        self.remaining = set(range(n))
        self.known = [{u for u in range(n) if a >> u & 1} for a in masks]
        self.lower = [5 if v < 104 - 4 * n else 4 for v in range(n)]
        self.upper = self.lower.copy()
        for v in range(n):
            require(v not in self.known[v], 'Loop in profile.')
            require(all(v in self.known[u] for u in self.known[v]), 'Asymmetric profile.')
            require(len(self.known[v]) <= self.upper[v], 'Degree exceeds profile.')
            if v < start:
                require(len(self.known[v]) == self.upper[v], 'Unfinished processed vertex.')
        self.possible = [row.copy() for row in self.known]
        for u in range(start, n):
            for v in range(u + 1, n):
                if (len(self.known[u]) < self.upper[u]
                        and len(self.known[v]) < self.upper[v]):
                    self.possible[u].add(v)
                    self.possible[v].add(u)
        self.edges = 52
        self.width = 11

    def step(self, operation, v):
        require(type(v) is int and v in self.remaining, 'Invalid or removed vertex.')
        require(operation in ('delete', 'eliminate'), 'Unknown operation.')
        changed = True
        while changed:
            changed = False
            for u in sorted(self.remaining):
                self.lower[u] = max(self.lower[u], len(self.known[u]))
                self.upper[u] = min(self.upper[u], len(self.possible[u]))
                require(self.lower[u] <= self.upper[u], 'Inconsistent degree interval.')
                if self.upper[u] == len(self.known[u]):
                    optional = self.possible[u] - self.known[u]
                    if optional:
                        changed = True
                    for w in optional:
                        self.possible[w].remove(u)
                    self.possible[u] -= optional
        certain = self.known[v].copy()
        permitted = self.possible[v].copy()
        low = max(self.lower[v], len(certain))
        high = min(self.upper[v], len(permitted))
        require(0 <= low <= high, 'Inconsistent degree interval.')
        old_lower, old_upper = self.lower.copy(), self.upper.copy()
        if operation == 'delete':
            require(self.width > 1, 'Deletion would exhaust the width bound.')
            self.edges -= low
            self.width -= 1
            for u in permitted:
                self.lower[u] = max(0, old_lower[u] - 1)
            for u in certain:
                self.upper[u] = old_upper[u] - 1
        else:
            require(high < self.width, 'Elimination might lose the width lower bound.')
            internal = sum(len(self.known[u] & certain) for u in certain) // 2
            self.edges += max(d * (d - 1) // 2 - d - internal
                              for d in range(low, high + 1))
            for u in permitted:
                # If uv exists, at most this many new edges can be filled at u.
                added = min(len(permitted - self.known[u] - {u}),
                            high - 1 - len(certain & self.known[u]))
                require(added >= 0, 'Inconsistent possible neighborhood.')
                bound = old_upper[u] - 1 + added
                self.upper[u] = bound if u in certain else max(old_upper[u], bound)
                self.lower[u] = max(0, old_lower[u] - 1)
            for u in certain:
                self.known[u] |= certain - {u}
            for u in permitted:
                self.possible[u] |= permitted - {u}
        self.remaining.remove(v)
        for u in self.remaining:
            self.known[u].discard(v)
            self.possible[u].discard(v)
            self.lower[u] = max(self.lower[u], len(self.known[u]))
            self.upper[u] = min(self.upper[u], len(self.possible[u]))
        self.known[v].clear()
        self.possible[v].clear()
        self.lower[v] = self.upper[v] = 0
        return {'operation': operation, 'vertex': v, 'degree_interval': [low, high],
                'remaining_vertices': len(self.remaining), 'edges_at_most': self.edges,
                'treewidth_at_least': self.width}


def verify_certificate(certificate, expected_prefix=None):
    require(certificate.get('format') == '52-edge-interval-refutation-v1', 'Unknown format.')
    prefix = certificate['prefix']
    if expected_prefix is not None:
        require(prefix == expected_prefix, 'Certificate proves a different profile.')
    state = Interval(prefix)
    steps = certificate['steps']
    require(isinstance(steps, list) and len(steps) <= len(state.remaining), 'Invalid steps.')
    trace = []
    for step in steps:
        require(isinstance(step, list) and len(step) == 2, 'Invalid step.')
        trace.append(state.step(*step))
    # This checker has one fixed external premise, not bounds supplied by the prover.
    require(state.width == 9 and state.edges < 42, 'No contradiction to f(9) >= 42.')
    return trace


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('certificate', type=Path)
    parser.add_argument('--prefix', type=Path, help='Pin the claim to this one-line profile.')
    args = parser.parse_args()
    certificate = json.loads(args.certificate.read_text())
    expected = list(map(int, args.prefix.read_text().split())) if args.prefix else None
    trace = verify_certificate(certificate, expected)
    for row in trace:
        lo, hi = row['degree_interval']
        print(f"{row['operation']} {row['vertex']}: degree {lo}..{hi}; "
              f"{row['remaining_vertices']} vertices; <= {row['edges_at_most']} edges; "
              f"treewidth >= {row['treewidth_at_least']}")
    print('PASS: every completion of the supplied 52-edge profile has treewidth at most ten.')
    print('Premise: f(9) >= 42 (the earlier treewidth-nine theorem).')
    print('This covers this entire profile, not all 52-edge graphs.')


if __name__ == '__main__':
    main()
