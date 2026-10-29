#!/usr/bin/env python3
"""Check that the archived five roots cover the regenerated square catalogue.

The hand square-direction lemmas and the separate four-square certificate
are premises. This checks the interface to the archived completion searches.
"""
from collections import defaultdict
import json
from pathlib import Path

from quartic_square_profiles import catalogue


def verify(path):
    records = json.loads(Path(path).read_text())['roots']
    expected = {row['mask']: row['prefix'] for row in catalogue() if len(row['edges']) <= 3}
    covered = set()
    for record in records:
        values = list(map(int, record['prefix'].split()))
        if len(values) != 28 or values[:2] != [26, 5] or not record['covered']:
            raise RuntimeError('Unexpected archived root format or unfinished root.')
        old = values[2:]
        if any(a < 0 or a >> 26 or a >> v & 1 for v, a in enumerate(old)):
            raise RuntimeError('Invalid adjacency row.')
        if any(bool(old[u] >> v & 1) != bool(old[v] >> u & 1)
               for u in range(26) for v in range(26)):
            raise RuntimeError('Asymmetric archived root.')
        matches = []
        for mask, prefix in expected.items():
            new = prefix[2:]
            # These archives use the same root-neighbor labeling. Vertices
            # outside the first five can differ by names within attachment groups.
            def groups(a):
                result = defaultdict(list)
                for v in range(5, 26):
                    result[a[v] & 31].append(v)
                return result
            left, right = groups(old), groups(new)
            if {k: len(v) for k, v in left.items()} != {k: len(v) for k, v in right.items()}:
                continue
            mapping = list(range(26))
            for key in left:
                for u, v in zip(left[key], right[key]):
                    mapping[u] = v
            # The normalized family must lie inside the archived family:
            # every archived required edge is present, and the five completed
            # neighborhoods agree exactly. Extra forced corner edges are fine.
            mapped = [sum(1 << mapping[v] for v in range(26) if old[u] >> v & 1)
                      for u in range(26)]
            if (all(mapped[u] & ~new[mapping[u]] == 0 for u in range(26))
                    and all(mapped[u] == new[u] for u in range(5))):
                matches.append(mask)
        if len(matches) != 1 or matches[0] in covered:
            raise RuntimeError('Unknown or duplicate archived square root.')
        covered.add(matches[0])
    if covered != set(expected):
        raise RuntimeError('Incomplete square-root coverage.')
    return sorted(covered)


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[1]
    print('PASS: archived square roots cover masks', verify(
        root / 'research/eleven/sources/treewidth-eleven-quartic-complete-audit.json'))
