"""Explicit proved quartic consequences used by the P4 theory certificate.

Dependencies: triangle exclusion, codegree2, square directions, the independently
checked v1 C4 exclusion, and marked-H22 plus its exceptional-square lift check.
These functions do not modify the original branch-proof inference rules.
"""
from itertools import combinations
from verify_branch_refutation import Contradiction, require, force, forbid, normalise

def quartic_structure_bad(known):
    """Previously proved quartic consequences, applied only by this explicit standalone projection."""
    if any(len(row) > 4 for row in known):
        return True
    squares = [0] * 26
    for u, v in combinations(range(26), 2):
        common = len(known[u] & known[v])
        if common > 2 or (v in known[u] and common):
            return True
        if common == 2:
            squares[u] += 1
            squares[v] += 1
    if max(squares) > 3:
        return True
    for v in range(26):
        for triple in combinations(sorted(known[v]), 3):
            if all((known[a] & known[b]) - {v} for a, b in combinations(triple, 2)):
                return True
    return False

def project_quartic_structure_basic(known, possible, degree):
    require(len(degree) == 26 and degree == [4] * 26,
            'Quartic structural rule requires order26 with all degrees four.')
    if quartic_structure_bad(known):
        raise Contradiction('A proved quartic structural restriction is violated.')
    for v in range(26):
        neighbors = sorted(known[v])
        if len(neighbors) != 4:
            continue
        a = neighbors[0]
        for b in neighbors[1:]:
            c, d = [u for u in neighbors if u not in (a, b)]
            first = (known[a] & known[b]) - {v}
            second = (known[c] & known[d]) - {v}
            if first and second:
                p, q = next(iter(first)), next(iter(second))
                if q not in known[p]:
                    force(known, possible, p, q)
                    return 1
    changes = 0
    for u, v in combinations(range(26), 2):
        if v not in possible[u] or v in known[u]:
            continue
        known[u].add(v)
        known[v].add(u)
        bad = quartic_structure_bad(known)
        known[u].remove(v)
        known[v].remove(u)
        if bad:
            forbid(known, possible, u, v)
            changes += 1
    return changes

def project_marked_squares(known, possible, degree):
    """Project only original G edges; virtual H suppression fills stay local."""
    require(len(degree) == 26 and degree == [4] * 26, 'Quartic scope required.')
    all_vertices = set(range(26))
    for x, y in combinations(range(26), 2):
        if len(known[x]) != 4 or len(known[y]) != 4:
            continue
        common = sorted(known[x] & known[y])
        if len(common) != 2:
            continue
        a, b = common
        if len(known[a]) != 4 or len(known[b]) != 4:
            continue
        deleted = {x, y, a, b}
        px, py = sorted(known[x] - {a,b}), sorted(known[y] - {a,b})
        pa, pb = sorted(known[a] - {x,y}), sorted(known[b] - {x,y})
        if len(deleted) != 4 or any(len(row) != 2 for row in (px,py,pa,pb)):
            raise Contradiction('Invalid square-corner geometry.')
        if len(set(px+py+pa+pb) - deleted) != 8:
            raise Contradiction('A triangle or excess codegree meets the square.')
        cubic_list = px + py
        cubic = set(cubic_list)
        remaining = all_vertices - deleted
        cross = [(u,v) for u in px for v in py]
        fills = {frozenset(pa), frozenset(pb)}
        survivors = 0
        common_known = [set(range(26)) for _ in range(26)]
        union_possible = [set() for _ in range(26)]
        # The all-four pattern is excluded by the original f(9)=42 cubic rule.
        for pattern in range(15):
            ca, cb = [row.copy() for row in known], [row.copy() for row in possible]
            try:
                for i,(u,v) in enumerate(cross):
                    (force if pattern >> i & 1 else forbid)(ca,cb,u,v)
                for u,v in (tuple(px),tuple(py)):
                    forbid(ca,cb,u,v)
                zero_pairs = set()
                for size in (2,3,4):
                    for vertices in combinations(cubic_list,size):
                        selected = set(vertices)
                        if any(ca[v] & selected for v in selected):
                            continue
                        if any(len(ca[v] & selected) != 1 for v in cubic-selected):
                            continue
                        zero_pairs.update(frozenset(pair) for pair in combinations(vertices,2))
                while True:
                    normalise(ca,cb,degree)
                    before = (tuple(map(frozenset,ca)),tuple(map(frozenset,cb)))
                    # H is G-deleted with two virtual added edges, never copied to G.
                    ha = [row & remaining for row in ca]
                    for fill in fills:
                        u,v = tuple(fill)
                        ha[u].add(v); ha[v].add(u)
                    for c in cubic_list:
                        neighbors = sorted(ha[c])
                        for u,v in combinations(neighbors,2):
                            if v in ha[u]:
                                raise Contradiction('A cubic has a triangle in the marked residue.')
                            forbid(ca,cb,u,v)
                        for u in neighbors:
                            for v in sorted(ha[u] & cb[c] & remaining):
                                forbid(ca,cb,c,v)
                    for u,v in combinations(cubic_list,2):
                        common_neighbors = ca[u] & ca[v] & remaining
                        limit = 0 if frozenset((u,v)) in zero_pairs or v in ca[u] else 1
                        if len(common_neighbors) > limit:
                            raise Contradiction('Marked residue common-neighbor cap violated.')
                        if len(common_neighbors) == limit:
                            for z in sorted((ca[u] & cb[v] & remaining)-common_neighbors):
                                forbid(ca,cb,v,z)
                            for z in sorted((ca[v] & cb[u] & remaining)-common_neighbors):
                                forbid(ca,cb,u,z)
                    after = (tuple(map(frozenset,ca)),tuple(map(frozenset,cb)))
                    if before == after:
                        break
            except Contradiction:
                continue
            survivors += 1
            for v in range(26):
                common_known[v] &= ca[v]
                union_possible[v] |= cb[v]
        if not survivors:
            raise Contradiction('All marked square patterns are excluded.')
        changed = 0
        for u,v in combinations(range(26),2):
            if v in common_known[u] and v not in known[u]:
                force(known,possible,u,v); changed += 1
            elif v in possible[u] and v not in union_possible[u]:
                forbid(known,possible,u,v); changed += 1
        if changed:
            return changed
    return 0

def project_quartic_structure(known, possible, degree):
    changed = project_quartic_structure_basic(known, possible, degree)
    return changed or project_marked_squares(known, possible, degree)
