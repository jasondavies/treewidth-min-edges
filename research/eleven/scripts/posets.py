"""Small-instance exact tools. A poset is a tuple of inclusive upper-set bitmasks."""
from functools import lru_cache


def bits(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def natural_posets(n):
    """All transitive relations compatible with 0,...,n-1 (not isomorph-free).

    Every n-element poset has such a labeling, so invariant checks cover all
    isomorphism types. Counts are not counts of labeled or unlabeled posets.
    """
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    for mask in range(1 << len(pairs)):
        up = [1 << i for i in range(n)]
        for k, (i, j) in enumerate(pairs):
            if mask >> k & 1:
                up[i] |= 1 << j
        if all(up[j] & ~up[i] == 0 for i in range(n) for j in bits(up[i])):
            yield tuple(up)


def downsets(up):
    return tuple(sum(1 << j for j in range(len(up)) if up[j] >> i & 1)
                 for i in range(len(up)))


def ideals(up):
    down = downsets(up)
    return [mask for mask in range(1 << len(up))
            if all(down[i] & ~mask == 0 for i in bits(mask))]


def antichains(up):
    return [mask for mask in range(1 << len(up))
            if all(up[i] & mask == 1 << i for i in bits(mask))]


def ideal_lattice(up):
    elements = ideals(up)
    order = tuple(sum(1 << j for j, b in enumerate(elements) if a & ~b == 0)
                  for a in elements)
    return elements, order


def extensions(up):
    down = downsets(up)
    full = (1 << len(up)) - 1

    def rec(done, prefix):
        if done == full:
            yield prefix
        for x in bits(full ^ done):
            if down[x] & ~done == 1 << x:
                yield from rec(done | (1 << x), prefix + (x,))

    yield from rec(0, ())


def extension_count(up):
    down = downsets(up)
    full = (1 << len(up)) - 1
    @lru_cache(None)
    def count(done):
        if done == full:
            return 1
        return sum(count(done | (1 << x)) for x in bits(full ^ done)
                   if down[x] & ~done == 1 << x)
    return count(0)


def words(up, labels):
    return {"".join(labels[i] for i in extension) for extension in extensions(up)}


def intersection_order(orders):
    orders = list(orders)
    n = len(orders[0])
    up = [(1 << n) - 1] * n
    for order in orders:
        for pos, x in enumerate(order):
            up[x] &= sum(1 << y for y in order[pos:])
    return tuple(up)


def canonical_occurrences(word):
    counts = {}
    out = []
    for label in word:
        counts[label] = counts.get(label, 0) + 1
        out.append((label, counts[label]))
    return out


def canonical_intersection(language):
    ordered = sorted(language)
    tokens = sorted(canonical_occurrences(ordered[0]))
    indices = {token: i for i, token in enumerate(tokens)}
    orders = [tuple(indices[token] for token in canonical_occurrences(word))
              for word in ordered]
    return intersection_order(orders), "".join(token[0] for token in tokens)
