"""Reconstruct the logical part of the archived quartic-path SAT encoding.

Uses only the standard library. Graph-theory units appended by the historical
teacher are deliberately excluded: the enclosing proof must justify them.
The counter variables have the explicit interpretation documented in at_most.
"""
from itertools import combinations


class Formula:
    def __init__(self, variables=0):
        self.variables = variables
        self.clauses = []

    def fresh(self):
        self.variables += 1
        return self.variables

    def add(self, *literals):
        self.clauses.append(list(literals))

    def gate(self, left, right, *, conjunction):
        result = self.fresh()
        if conjunction:
            self.add(-result, left)
            self.add(-result, right)
            self.add(result, -left, -right)
        else:
            self.add(result, -left)
            self.add(result, -right)
            self.add(-result, left, right)
        return result

    def at_most(self, literals, bound):
        """Add a staggered sequential counter and return its threshold map.

        Entry (k,j) means at least k+1 of literals[:j+k+1] are true.
        Assigning that meaning satisfies every clause whenever the cardinality
        bound holds. This constructive extension is enough for UNSAT soundness.
        The variable and clause ordering matches the archived encoding.
        """
        size = len(literals)
        if type(bound) is not int or not 0 <= bound <= size:
            raise ValueError('Invalid cardinality bound')
        if bound == size:
            return {}
        if bound == size - 1:
            self.add(*(-literal for literal in literals))
            return {}
        if bound == 0:
            for literal in literals:
                self.add(-literal)
            return {}
        thresholds = {}

        def threshold(k, j):
            key = (k, j)
            if key not in thresholds:
                thresholds[key] = self.fresh()
            return thresholds[key]

        for j in range(size - bound):
            self.add(-literals[j], threshold(0, j))
            for k in range(bound):
                current = threshold(k, j)
                if j + 1 < size - bound:
                    self.add(-current, threshold(k, j + 1))
                if k + 1 < bound:
                    self.add(-literals[j + k + 1], -current,
                             threshold(k + 1, j))
                else:
                    self.add(-literals[j + bound], -current)
        return thresholds


def formula(root, *, lex=True):
    """Return (CNF, edge list, block ends) for a fixed exact radius-two root."""
    if (len(root) != 26 or any(type(row) is not int or row < 0 or row >> 26
                              for row in root)
            or any(root[u] >> u & 1 for u in range(26))
            or any(bool(root[u] >> v & 1) != bool(root[v] >> u & 1)
                   for u, v in combinations(range(26), 2))):
        raise ValueError('Malformed simple undirected root')
    if any(root[v].bit_count() != 4 for v in range(5)):
        raise ValueError('The first five neighborhoods must be exact quartic rows')
    if any(root[u] >> v & 1 for u in range(5, 26) for v in range(u + 1, 26)):
        raise ValueError('The radius-two root must leave later rows unspecified')
    if root[0] != 30:
        raise ValueError('The root neighbors must be vertices one through four')
    cap = sum((root[0] & root[v]).bit_count() == 2 for v in range(1, 26))
    if cap != 3:
        raise ValueError('This encoding is for the three-square path case')
    edges = list(combinations(range(26), 2))
    variables = {edge: i for i, edge in enumerate(edges, 1)}
    cnf = Formula(len(edges))
    blocks = {}

    def edge(u, v):
        return variables[min(u, v), max(u, v)]

    for v in range(26):
        incident = [edge(u, v) for u in range(26) if u != v]
        cnf.at_most([-literal for literal in incident], len(incident) - 4)
        cnf.at_most(incident, 4)
    blocks['degrees'] = len(cnf.clauses)
    for u, v in edges:
        if u < 5:
            cnf.add(edge(u, v) if root[u] >> v & 1 else -edge(u, v))
    blocks['root'] = len(cnf.clauses)
    for u, v, w in combinations(range(26), 3):
        cnf.add(-edge(u, v), -edge(u, w), -edge(v, w))
    blocks['triangles'] = len(cnf.clauses)
    two_common = {}
    for u, v in edges:
        common = [cnf.gate(edge(u, w), edge(v, w), conjunction=True)
                  for w in range(26) if w not in (u, v)]
        one = cnf.gate(common[0], common[1], conjunction=False)
        two = cnf.gate(common[0], common[1], conjunction=True)
        for literal in common[2:]:
            cnf.add(-two, -literal)
            both = cnf.gate(one, literal, conjunction=True)
            two = cnf.gate(two, both, conjunction=False)
            one = cnf.gate(one, literal, conjunction=False)
        two_common[u, v] = two
    blocks['common_neighbors'] = len(cnf.clauses)

    def pair(u, v):
        return two_common[min(u, v), max(u, v)]

    for v in range(26):
        cnf.at_most([pair(u, v) for u in range(26) if u != v], cap)
        for a, b, c in combinations((u for u in range(26) if u != v), 3):
            cnf.add(-edge(v, a), -edge(v, b), -edge(v, c),
                    -pair(a, b), -pair(a, c), -pair(b, c))
    blocks['square_directions'] = len(cnf.clauses)
    if lex:
        dynamic = [(u, v) for u, v in edges if u >= 5]
        for x, y in combinations(range(5, 26), 2):
            if root[x] != root[y]:
                continue
            permutation = list(range(26))
            permutation[x], permutation[y] = y, x
            previous = cnf.fresh()
            cnf.add(previous)
            for u, v in dynamic:
                a, b = edge(u, v), edge(permutation[u], permutation[v])
                if a == b:
                    continue
                cnf.add(-previous, -a, b)
                following = cnf.fresh()
                # following iff previous and (a == b).
                cnf.add(-following, previous)
                cnf.add(-following, -a, b)
                cnf.add(-following, a, -b)
                cnf.add(-previous, -a, -b, following)
                cnf.add(-previous, a, b, following)
                previous = following
    blocks['lex'] = len(cnf.clauses)
    return cnf, edges, blocks
