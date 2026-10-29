# Short 35-edge reductions for 29 order-24 profiles

The same reduction excludes 29 catalogue profiles using the complete
earlier 34- and 35-edge classifications. Profile 69 gives a concrete
example and replaces the largest ordinary branch proof.
The 35-edge premise is the full minimum-degree-three classification of
130 graphs, with orders at most 18, recorded in
[the 41-edge proof](proofs/nine-41.md). It is not merely the narrower
93-graph family used in the initial 40-edge argument.

Suppose a completion G had treewidth at least eleven. The high vertices
0, 1, 2 are independent, so deleting them removes exactly fifteen edges
and leaves a 21-vertex, 37-edge graph of treewidth at least eight.
High vertices 3 and 7 now have degree two, with disjoint neighbor pairs

    N(3) = {15,16},       N(7) = {4,23}.

Suppress both vertices, adding each replacement edge if it is absent.
This preserves treewidth at least eight and leaves a graph J with
nineteen vertices and at most 35 edges.

Every survivor still has degree at least three. Before suppression, the
seven lows attached to deleted highs have degree three. All other lows
have degree four; the other highs have degrees four or five. The four
suppression endpoints are distinct and none is one of those seven cubic
lows. Even if a replacement edge already existed, an endpoint therefore
loses at most one incidence and retains degree at least three. This
argument gives no degree credit for the replacement edges.

Now distinguish the possible edge counts. Fewer than 34 edges contradicts
f(8)=34. At 34 edges, the complete classification permits only 16 or 17
nonisolated vertices. At 35 edges, every minimum-degree-three graph of
treewidth at least eight belongs to the full family with order at most 18.
Both alternatives contradict the nineteen vertices of J. If a graph in
either case were disconnected, a width-eight component already consumes
at least 34 edges; minimum degree three leaves no room for another
component, so the connected classification applies.

The recipe checker validates the exact high neighborhoods against the
independently checked catalogue. It charges a possible new fill edge when
bounding the remaining edge count and gives no fill-edge credit when
bounding surviving degrees:

```sh
python3 scripts/verify_order24_smoothing35.py
```

For every supplied recipe, the checker verifies three independent high
vertex deletions, two degree-at-most-two suppressions, nineteen surviving
vertices, an upper edge bound of 35, and a surviving degree lower bound of
three. Thus the same classification argument applies without assuming
that the other profiles share the example's particular neighborhoods.

The source JSON records only each catalogue index and its five operations.
The 29 checked indices are

    29, 31, 32, 33, 34, 37, 69, 75, 86, 90, 94, 95, 98, 101, 102,
    103, 105, 106, 119, 120, 129, 130, 141, 146, 150, 164, 188, 202, 243.

No branch search or new graph catalogue is required. These are order-24
profile exclusions relative to the stated earlier classification premises;
they do not by themselves prove the complete 52-edge exclusion.
