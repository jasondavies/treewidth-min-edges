#!/usr/bin/env python3
"""Independently check that supplied clauses are jointly inconsistent.

This does NOT justify their graph-theoretic interpretation. Each input
clause must separately be derived from the graph family being excluded.
"""
import argparse
import json
import lzma
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify(certificate):
    require(certificate.get('format') == 'positive-rup-v1', 'Unknown format.')
    n = certificate['variables']
    require(type(n) is int and n > 0, 'Invalid variable count.')
    def checked_clause(clause):
        require(isinstance(clause, list) and all(type(x) is int and 0 < abs(x) <= n for x in clause),
                'Invalid clause.')
        require(len(set(clause)) == len(clause), 'Repeated literal.')
        return tuple(clause)
    clauses = [None] + [checked_clause(c) for c in certificate['inputs']]
    require(all(clauses[1:]), 'An empty premise is not accepted.')
    for step in certificate['steps']:
        require(isinstance(step, list) and len(step) == 2, 'Invalid proof step.')
        clause, hints = checked_clause(step[0]), step[1]
        require(isinstance(hints, list) and all(type(h) is int and 0 < h < len(clauses) for h in hints),
                'Hint is not an earlier clause.')
        assigned = {-literal for literal in clause}
        conflict = any(-literal in assigned for literal in assigned)
        for hint in hints:
            if conflict:
                break
            premise = clauses[hint]
            if any(literal in assigned for literal in premise):
                continue
            unknown = [literal for literal in premise if -literal not in assigned]
            require(len(unknown) <= 1, 'A hint is neither unit nor conflicting.')
            if unknown:
                assigned.add(unknown[0])
            else:
                conflict = True
        require(conflict, 'No reverse-unit-propagation contradiction.')
        clauses.append(clause)
    require(clauses[-1] == (), 'Proof does not end with the empty clause.')
    return len(certificate['inputs']), len(certificate['steps'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('certificate', type=Path)
    args = parser.parse_args()
    raw = args.certificate.read_bytes()
    if args.certificate.suffix == '.xz':
        raw = lzma.decompress(raw)
    inputs, steps = verify(json.loads(raw))
    print(f'PASS: {inputs} supplied clauses imply a contradiction in {steps} checked RUP steps.')
    print('This is propositional verification only; graph-theoretic input obligations remain.')


if __name__ == '__main__':
    main()
