# A cubic-neighbor cap for 23-vertex, 42-edge residues

All graphs are finite, simple and undirected. Write f(k) for the minimum
number of edges of a graph of treewidth at least k.

**Theorem.** Let H have 23 vertices, 42 edges, eight vertices of degree
three and fifteen of degree four. Let L be its cubic vertices. If
H[L] has maximum degree at most two and has an isolated vertex, then

    tw(H) >= 9  implies  every quartic vertex has at most one cubic neighbor.

The proof uses the earlier complete classifications underlying
[the proof of f(9)=42](proof-nine.md), including their 29-, 34-, 35- and
36-edge families. These are explicit premises: this does not replace their
large enumerations with a classification-free proof. It does replace the
archived 23-vertex residue enumeration with a short finite reconstruction.
No archived 52-edge core classification is used.

## Reduction to a 20-vertex graph

Assume tw(H) >= 9 and let w be a quartic vertex with r >= 2 cubic
neighbors. Every cubic neighborhood is independent: eliminating a cubic
with an edge between its neighbors would preserve treewidth at least nine
and leave fewer than f(9)=42 edges. Likewise, two cubics have at most one
common neighbor. If they are adjacent, a common neighbor would already
violate independence. Otherwise, eliminating one inserts an edge between
two shared neighbors; eliminating the other then loses an edge.

The r cubic neighbors of w are independent. Their pairs of other neighbors
are nonadjacent pairs and are pairwise disjoint, by those same facts. None
of the endpoints belongs to N(w), since that would form a triangle with a
cubic vertex. Delete w and suppress its r now-degree-two neighbors. Each
suppression removes two edges and inserts one previously absent edge.
Surviving degrees are unchanged by suppression, so the resulting graph J
has treewidth at least eight and exactly

    |V(J)| = 22-r,   |E(J)| = 38-r,   #cubics(J) = 12-2r.

All other vertices are quartic. It is connected: a width-eight component
needs at least 34 edges, whereas another component of minimum degree
three needs at least six.

For r=3 this gives a 19-vertex, 35-edge minimum-degree-three graph, which
the earlier full 35-edge classification excludes. For r=4 it gives an
18-vertex, 34-edge such graph, excluded by the full 34-edge classification.
Hence r=2. We must cover J with twenty vertices, 36 edges, eight cubics,
twelve quartics, and treewidth at least eight.

## A complete necessary family for J

The following reduction is valid for every J with that degree profile and
treewidth bound; it does not assume that J came from H. We show that one
can eliminate one, two or three pairwise-distance-at-least-three cubics,
preserving 36 edges, to enter the existing 36-edge classification scope.
The remaining two-K4 obstruction is checked by the small independent
[source-only enumeration](proof-eleven-two-k4-incidence.md).

### Earlier classification premises

The proof uses the previously established f(8)=34 and the full earlier
classifications, including these consequences:

1. A minimum-degree-three graph of treewidth at least eight with 34 edges
   has at most seventeen vertices.
2. Such a graph with 35 edges has at most eighteen vertices; every
   eighteen-vertex survivor has exactly two cubics and sixteen quartics.
3. Any graph of treewidth at least seven with at most 29 edges has at
   most fifteen nonisolated vertices. This is the unrestricted consequence
   of the full 29-edge classification, not merely the minimum edge bound.
4. The complete 36-edge family covers orders 16–19, minimum degree three,
   maximum degree five, and at most five cubics.

Disconnected minimum-degree-three graphs are included: a width-eight
component needs at least 34 edges and another such-degree component
needs at least six, impossible at 34–36 edges. Premise 3 already allows
disconnected graphs and isolates.

### Cubic neighborhoods are independent

Eliminate a cubic y. If t edges already join its neighbors, this reduces
the edge count from 36 to 36-t and preserves treewidth at least eight.

If t=1, the remaining nineteen-vertex graph has minimum degree at least
three and 35 edges, contradicting premise 2. If t=2, the result has 34
edges. A possible degree-two neighbor could be suppressed to leave at
most 33 edges, contradicting f(8); if no such neighbor exists, premise 1
contradicts its nineteen vertices. If t=3, the edge bound fails directly.
Thus t=0 for every cubic y.

If some y has at least two cubic neighbors, eliminating it removes y
and converts at least two other cubics to degree four. The result has
nineteen vertices, at most five cubics, minimum degree three, and maximum
degree five. This gives the first reduction.

Henceforth assume J[C] has maximum degree at most one.

### Cubic codegree is at most one

Suppose distinct cubics y,z have at least two common neighbors. They
cannot be adjacent, because cubic neighborhoods are independent.
Eliminate y and then z. Their degrees remain three until elimination.
Two common neighbors create one edge in N(z), yielding an eighteen-vertex,
35-edge graph of minimum degree at least three. At most two other cubics
were adjacent to y or z, so at least four of the original eight remain
cubic. This contradicts the eighteen-vertex part of premise 2.

If they have all three neighbors in common, eliminating z loses three
edges and contradicts f(8) instead. Therefore every cubic pair has at
most one common neighbor.

### A useful degree-six obstruction

A graph K with eighteen vertices, 36 edges, minimum degree three, and
treewidth at least eight cannot have a degree-six vertex adjacent to a
cubic vertex. Delete the degree-six vertex: the graph has seventeen
vertices, thirty edges, minimum degree at least two, and treewidth at
least seven. The adjacent cubic now has degree two. Suppress it, losing
at least one edge. All sixteen other vertices remain nonisolated, since
their degrees were at least two and decrease by at most one. This
contradicts premise 3.

Now suppose a quartic q in J has three cubic neighbors y,z,w. No two of
these cubics are adjacent, and any two share only q. Eliminating y,z
therefore preserves all 36 edges and gives q degree six. The third cubic
w remains cubic: it was adjacent to neither eliminated cubic. The
remaining graph has eighteen vertices and minimum degree at least three,
contradicting the obstruction above. Every quartic consequently has at
most two cubic neighbors.

### A cubic edge yields a two-vertex reduction

Suppose u,v are adjacent cubics. Besides v, the two neighbors of u are
quartics, each with at most one other cubic neighbor. The vertex v has no
other cubic neighbor. Thus at most three other cubics are within distance
two of u, and some cubic z is at distance at least three.

Eliminate u,z. Their neighborhoods are disjoint, so no remaining degree
increases by more than one. The two eliminations preserve 36 edges.
They remove u,z and convert v to degree four, leaving at most five cubics,
maximum degree five, and eighteen vertices. This gives the second reduction.

### Independent cubics and the only packing obstruction

It remains that C is independent. Its 24 incidences meet Q, and the
twelve quartics each meet at most two cubics. Hence every quartic meets
exactly two cubics. Build a graph F on C with one edge for each quartic,
joining its two cubic neighbors. The codegree bound makes F simple;
every vertex has degree three.

An independent triple in F is a triple of cubics of pairwise distance at
least three in J. Eliminating them preserves 36 edges, leaves seventeen
vertices and exactly five cubics, and creates maximum degree at most five.
This gives the third reduction.

If F has no independent triple, its complement is triangle-free and has
minimum degree four. The neighborhoods of the ends of any complement
edge are disjoint, each has at least four vertices, and together they
partition the eight vertices. Each neighborhood is independent. Minimum
degree four then forces every edge between these two four-sets. Thus the
complement is K(4,4) and F consists of two disjoint K4s.

### Exhausting the two-K4 exception

The twelve quartics now correspond bijectively to the six edges in each
K4. Their remaining two neighbors form a 2-factor D on those twelve
vertices. Cubic-neighborhood independence forbids D edges between two
incident edges of a K4. Within each side, the only allowable edges are
the three opposite-edge pairs; every cross-side edge is allowed.

Suppose a internal opposite pairs are selected on one side and b on the
other. Their cross-side degree sums are 12-2a and 12-2b, so a=b. The
vertex permutations of K4 act transitively on its three opposite pairs,
therefore on subsets of each size 0,1,2,3 (size two follows by complements).
Independent permutations on the two K4s let us select the first a pairs
on both sides. Every cross-side completion is still enumerated.

With the K4 edges ordered 01,02,03,12,13,23, the opposite pairs are
(0,5),(1,4),(2,3). Enumerate all 6-by-6 Boolean matrices whose row and
column sums are two, reduced to one at the endpoints of the chosen
internal pairs. This gives exactly 67,950, 9,876, 2,172, and 720 matrices
for a=0,1,2,3 respectively: 80,718 candidate graphs in total.

The standalone Python checker enumerates all matrices without symmetry
pruning, proposes an order with integer-mask greedy elimination, and verifies
a width-seven order for every graph by independent explicit set fills.
Thus this exceptional pattern contradicts treewidth at least eight.
The counts are diagnostics; coverage follows from the exhaustive row
choices and the stated normalization. No C compiler or saved order stream
is required by the final checker.

### Inspecting the existing family

The complete 36-edge family contains no seventeen-vertex graph with five
cubics, so the third reduction cannot occur under the treewidth-eight
hypothesis. The nineteen-vertex cases number 465: 457 have four cubics
and no degree-five vertex, while eight have five cubics and one degree-five
vertex. They have only 71 eligible inverse triangles covering every
degree-five vertex; all 71 inverse graphs pass cubic-neighborhood
independence.

The relevant eighteen-vertex cases have four or five cubics, numbering
446 and thirteen respectively. There are 52 pairs of vertex-disjoint
inverse triangles covering all degree-five vertices. Nineteen pairs would
give one selected cubic at least two cubic neighbors, contradicting the
matching branch. Of the other 33 inverses, 32 violate maximum degree one
in the cubic-induced graph and one violates the proved cap of two cubic
neighbors per quartic. Thus this branch contributes no survivors.

Consequently every J under the theorem's hypotheses is isomorphic to one
of the 71 raw single-triangle inverses. These may contain duplicates or
graphs of smaller treewidth. They are a complete necessary family, not
assertions of exact treewidth. The count is independently reproduced by
both bit-mask and set-based inverse enumerators from the existing pinned
36-edge family; no archived small-36 family is used.


## Reconstructing every possible H

For each necessary J, select two of its eight cubics, called X. These
are the other two neighbors of the deleted quartic w and regain degree
four. Select two vertex-disjoint edges of J avoiding X. Subdivide each
with a new cubic, then add w adjacent to the two new vertices and X.

Every H under consideration occurs in this construction: the selected
edges are precisely the matching created by its two suppressions. Avoiding
X is necessary because the suppressed cubics had independent neighborhoods.
No isomorphism pruning is used; repeated constructions are harmless.

The checker independently constructs the 23-vertex graph and checks its
42-edge, eight-cubic/fifteen-quartic profile. It keeps every graph whose
cubic-induced subgraph has maximum degree at most two and an isolated
vertex, whose cubic neighborhoods are independent, and whose cubic pairs
have at most one common neighbor. Every removed graph violates an explicit
necessary condition proved above or a hypothesis of the theorem.

The complete direct enumeration has 726,624 inverse choices. The
cubic-induced condition removes 233,598; 493,026 target graphs remain.
Each has an independently checked width-eight elimination order, contrary
to tw(H) >= 9. This proves the theorem. Counts describe the finished run;
coverage follows from the exhaustive choices, not from matching a count.

### A faster check using a universal apex

For 66 of the 71 J reconstructions, a bounded order finder supplies a
width-seven order, independently checked by explicit Python set fills.
The checker also verifies that the same order followed by an apex is a
width-eight order of J plus a vertex adjacent to every vertex of J.

Every lift of such a J has width at most eight. Eliminate its two new
subdivision vertices first; each has degree three, and their original
endpoint pairs are disjoint. These eliminations restore the two edges
of J and possibly add edges from w to their endpoints. The remaining
graph is a subgraph of J plus a universal apex. Follow the checked order
of J and place w last. This covers every lift of that J at once.

If the bounded finder does not supply a width-seven order for J, the
checker draws no negative conclusion: it instead enumerates all its
target lifts and requires a checked width-eight order for each. This
fallback occurs for five J reconstructions and checks 39,760 lifts.
Failure to find an order at this final stage stops the program with an
error; it cannot produce a successful verification.

## Reproduction and dependencies

After reproducing the earlier classifications as documented in
[proof-nine.md](proof-nine.md#reproduction), run

```sh
python3 scripts/verify_two_k4_incidence.py
python3 scripts/verify_cubic_neighbor_cap.py
```

The second command requires a C compiler for a small, untrusted bounded
order finder. It defaults to `CC` (or `cc`) and portable `-O3` compilation;
`--native` optionally adds `-march=native`. The first command needs only
Python's standard library. Neither command requires new saved orders or
large certificate data. `--repository PATH` selects the repository holding
the earlier family when the checker is run from another directory.

The 36-edge input is `sources/nine/treewidth36-family.g6`, pinned by SHA256

    0f62f3d14d543515b12567c1d650d290a9a5369ab9931220e5d398a9d3999214

A hash establishes the identity of the supplied earlier family; its
completeness is the earlier classification premise. Full regeneration
uses `scripts/reproduce_nine.py --full` as documented in that proof,
including the broad 36-edge construction with its `--family31` input.
The smaller archived 36-edge residue family is not used.

The default finite reconstruction check took about four seconds on the
validation machine. To additionally reconstruct and check all 493,026
lifts, including those already covered by the universal-apex argument, run

```sh
python3 scripts/verify_cubic_neighbor_cap.py --all-lifts
```

The ordered 23-mask little-endian adjacency stream of this direct check
has SHA256

    259e01517e18e8c2d1aae447cace74155b6eaa2057df14049043972696738e17

The native finder tries a deterministic greedy min-fill order, then every
one-vertex and ordered two-vertex prefix. It is finite, uses no external
classification, and is not trusted to establish an upper bound. Python
requires an exact vertex permutation and recomputes every fill with sets.

## Corollary: the private four-cycle order-25 profile is impossible

Suppose a 25-vertex, 52-edge graph G has treewidth at least eleven, four
vertices of degree five and 21 of degree four. Suppose its high vertices
induce the cycle x-b-y-d-x and no low vertex is adjacent to two highs.
Each high therefore has three private low neighbors. Write A and B for
the private low neighborhoods of x and y.

First delete the opposite pair b,d. This removes ten edges and leaves
treewidth at least nine. The vertices x,y are now cubic, so the 42-edge
cubic-neighborhood fact proved above shows that A and B are independent.

A vertex of B cannot have two neighbors in A. To see this, delete x and
then that vertex of B: they are nonadjacent and had degrees five and
four, so 43 edges remain and treewidth is at least nine. Its two neighbors
in A are now nonadjacent degree-two vertices. Suppressing both loses at
least two edges, contradicting f(9)=42. The symmetric argument applies
to a vertex of A. Thus the edges between A and B form a matching of size
at most three.

Now delete x,y. The resulting H has 23 vertices and 42 edges, treewidth
at least nine, and exactly eight cubics: A union B together with b,d.
The latter two are isolated in H[L], since high neighborhoods were
private. Therefore H[L] has maximum degree one and at most three edges,
and the theorem applies. Its eight cubics have at least

    3*8 - 2*3 = 18

edges to the fifteen quartics. But each quartic can meet at most one cubic,
allowing at most fifteen such edges: a contradiction. This excludes the
private C4 profile (`011110`) without a new branching certificate.
