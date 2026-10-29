# Certified order-24 incidence-profile coverage

The certificate is **212,492 bytes**, compressed from 758,274 bytes. It
proves that the supplied 364 incidence-profile representatives cover every
minimum-order 52-edge counterexample on 24 vertices. It does **not** exclude
any of those profiles. Every representative still needs a separate proof.

Only [the verifier](scripts/verify_order24_catalogue.py) and
[the certificate](sources/eleven-order24-catalogue.bin.xz) are needed to check
coverage. The checker uses the standard library and runs no generator,
canonicalizer, nauty, or geng:

```sh
python3 scripts/verify_order24_catalogue.py sources/eleven-order24-catalogue.bin.xz --output /tmp/order24-profiles.txt
```

## Why the high-graph catalogue is exhaustive

A 24-vertex counterexample has eight degree-five vertices (high vertices)
and sixteen degree-four vertices (low vertices). Its induced high graph has
maximum degree at most five.

Start with the unique graph on zero vertices. At each order 1 through 8,
the checker takes **every listed representative of the previous order** and
adds a new vertex with **every possible neighbor subset** that respects
maximum degree five. For each extension, the certificate supplies the index
of a representative at the next order and a permutation mapping the
extension to that representative. The checker verifies bijectivity and
every edge/nonedge under the map. Missing maps fail verification.

Deleting any vertex from a graph of maximum degree five leaves a graph of
maximum degree five. Thus induction proves completeness at each order.
There are 89,107 checked extension maps in all. The order-eight list contains
7,459 representatives; 7,248 of them have at least eight edges, matching the
historical high-graph count. The verifier does not need to certify pairwise
nonisomorphism: duplicates would enlarge the subsequent exhaustive work but
could not cause a missing case. The proposed generator happens to produce
one representative per class.

## Why every high/low incidence pattern is covered

Use the elementary local restrictions for minimum-order 52-edge
counterexamples already proved in the
[branch-certificate documentation](proof-eleven-branch-certificates.md):

* A low vertex is in at most one triangle; a high vertex in at most four.
* The high neighbors of a low vertex form a clique, so there are at most two.
* A high pair has at most one shared low neighbor.
* If two nonadjacent high neighbors of a high vertex are deleted, its
  remaining neighborhood is independent. Otherwise a cubic elimination
  would produce fewer than 42 edges at treewidth at least nine.

One additional boundary restriction is used: **a shared low neighbor can
only join high vertices that each have at least two low neighbors.** Here
is its proof. Suppose a high vertex `v` has a unique low neighbor `u`, shared
with another high vertex `a`. The high vertices `v,a` are adjacent. Write
`b,c,d` for the other three high neighbors of `v`. If any pair among `b,c,d`
is nonadjacent, delete that pair. The residual graph has 42 edges and
treewidth at least nine; `v` is cubic and its neighborhood contains the edge
`u-a`, a contradiction after eliminating `v`. Thus `b,c,d` form a triangle.
If `a` is nonadjacent to one of them, delete that pair and use the edge on
the other two to obtain the same contradiction. Hence the four high
neighbors of `v` form a clique, placing `v` in at least six triangles,
contrary to the high triangle bound.

For each high-graph representative, let `capacity[v] = 5 - high_degree[v]`.
The checker enumerates every subset of its edges whose endpoints both have
capacity at least two. A selected edge receives one distinct shared low
neighbor. No other shared low neighbors are possible by the restrictions.
Assignments exceeding a capacity are rejected; each remaining capacity
unit is supplied by a private low neighbor. Assignments needing more than
sixteen low vertices are rejected; unused low vertices have no high neighbor.

This describes all edges incident to high vertices. The low--low edges are
left unspecified. The triangle and nonadjacent-high-neighbor restrictions
are evaluated on each completed incidence pattern. Of 120,192 feasible
attachments, 1,026 survive those restrictions.

For every surviving attachment, the certificate supplies a representative
index and a permutation of the eight high vertices. The checker verifies
that this permutation preserves both the high graph and its marked edges
(the pairs with a shared low neighbor). This suffices for the full incidence
pattern: private counts are fixed by the degrees and marks, shared low
neighbors correspond to marked pairs, and all remaining low vertices are
free. The low vertices within each type are interchangeable.

Thus the 364 supplied profiles cover every necessary case. No numerical
count alone establishes coverage: all extension and attachment maps are
checked explicitly.

## Certificate format

The uncompressed format starts with ASCII `O24C1\n`. At each order 1–8,
two little-endian 32-bit integers give representative and map counts, followed
by 32-bit graph encodings and 32-bit target/permutation pairs. Pair `u<v` has
bit position `v(v-1)/2+u`. A permutation packs the new label of old vertex `i`
into bits `3i..3i+2`. Every eligible vertex extension, in the explicitly
defined order, consumes one map.

The final block has profile and map counts, 64-bit profile encodings, and
target/permutation pairs for every valid attachment. A profile encoding is
`(high_edges << 28) | marked_edges`. The high graphs and attachment masks
are visited in the order recorded/defined by the format. The checker
rejects mismatched counts, invalid permutations, incorrect maps, truncation,
trailing data, and malformed compression.

The files are independent of the archived 364-profile enumeration. Tests
exercise full coverage and deliberate omissions/corruption. An exclusion
bundle can identify its roots by these profile encodings plus independently
checked relabelings, completing the bridge from arbitrary order-24
counterexamples to individual profile certificates.

## Complete order-24 exclusion

The [aggregate checker](proof-eleven-order24-compact.md) combines this
independently checked catalogue with short reduction recipes and stored
branch certificates. It verifies complete coverage of all 364 profiles.

```sh
python3 scripts/verify_order24_compact.py --check-premises
```
