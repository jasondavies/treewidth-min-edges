# Excluding the last order-25 high profile: the claw

This excludes the private high-claw profile `001011` by two small exhaustive
checks, without a large branch certificate. The checker is
[scripts/verify_order25_claw.py](scripts/verify_order25_claw.py).

The premises are the minimum-order 52-edge reduction, the earlier edge
minima, the earlier complete 29-, 34-, 35- and 36-edge classifications,
and the [one-degree-five H23 theorem](proof-eleven-one-high-cubic-cap.md).
The latter theorem includes the general J20 packing and two-K4 premises
stated in its proof. No archived 52-edge classification is used.

## 1. A 21-vertex residue

Suppose a minimum-order counterexample G has four degree-five highs whose
induced graph is a claw. Its twenty-one other vertices have degree four,
and all low attachments to highs are private. Let the center be h and the
leaves be h1,h2,h3. The center has two private low neighbors A; each leaf
has four private low neighbors Bi; seven lows have no high neighbor.

Delete the three leaves and suppress h, now of degree two. The two members
of A are nonadjacent: deleting any two high leaves makes h cubic in a
42-edge graph of treewidth at least nine, where cubic neighborhoods must
be independent. Suppression therefore adds a new edge. The result J has
21 vertices, 36 edges and treewidth at least eight. Its twelve cubics C
are B1 union B2 union B3; its other nine vertices are quartic.

The local facts used here are proved under
[local propagation rules](proof-eleven-branch-certificates.md#why-the-local-propagation-rules-are-valid).
A low vertex lies in at most one triangle: otherwise eliminating it
preserves treewidth at least eleven with no increase in edges, contrary
to minimum order (or the already excluded smaller edge counts).

Consequently each Bi induces a matching. Also, a low vertex v in Bi has
at most one neighbor in any other Bj. If it had two, these two common low
neighbors of v and hj would be independent (an edge between them creates
two triangles at a low endpoint). Delete the nonadjacent v,hj, leaving
43 edges and treewidth at least nine, and suppress those two independent
degree-two vertices. At most 41 edges remain, contrary to f(9)=42.

Edges between different Bi in fact form a single matching. Indeed, for v in Bi, delete the other two high leaves. The
23-vertex residue has nine cubics (the other two groups and h), thirteen
quartics and the unique high hi. The cubic-induced graph has maximum
degree two: each low cubic has at most one same-group neighbor and at
most one other-group neighbor by the existing local restrictions, and h
is isolated among the cubics. The one-high theorem says that its quartic
neighbor v has at most one neighbor in the other two groups combined.

Thus J[C] is the union of two matchings. Its components are paths and
even cycles. In particular its maximum degree is two.

## 2. Restrictions forced by the earlier small-edge classifications

In any such J of treewidth at least eight, cubic neighborhoods are
independent. Eliminating a cubic with exactly one internal neighborhood
edge leaves 20 vertices, 35 edges and minimum degree at least three,
contrary to the full 35-edge classification (maximum order 18).
With two internal edges the result has 34 edges: if a degree-two vertex
appears, suppressing it violates f(8)=34; otherwise its minimum degree
is at least three and its order contradicts the full 34-edge classification.
Three internal edges would leave only 33 edges immediately.

Two cubics have at most one common neighbor. They cannot be adjacent if
they have a common neighbor, by neighborhood independence. With exactly
two common neighbors, eliminating both leaves 19 vertices, 35 edges and
minimum degree at least three, again impossible. Three common neighbors
leave at most 33 edges, contrary to f(8). This also excludes 4-cycles in C,
so its even cycle components have length at least six.

Every quartic has at most two cubic neighbors. Otherwise eliminate two
of the cubic neighbors of a quartic w. Their neighborhoods are independent
and intersect only in w, so the resulting graph still has 36 edges and
w has degree six. A third cubic neighbor remains cubic. Delete w and
suppress that third neighbor, now degree two. This produces a graph of
treewidth at least seven with at most 29 edges and 17 nonisolated vertices:
after deleting w all other degrees are at least two, and suppressing one
degree-two vertex lowers any surviving degree by at most one. This
contradicts the earlier 29-edge consequence that a graph of treewidth at
least seven has at most 15 nonisolated vertices.

The twelve cubics contribute 36 degree incidences. At most 18 go to the
nine quartics, so C has at least nine edges. A 12-vertex union of paths
and cycles with at least nine edges has at most three path components,
including isolated vertices as paths of order one.

These applications of the earlier connected classifications have no
unmentioned disconnected case. At treewidth eight, one component needs
at least 34 edges, while a second component of minimum degree at least
three needs at least six. At most 36 edges cannot accommodate both.

## 3. A small weighted-packing lemma

Let D join two cubics when they have a common quartic neighbor. The
quartic cap and cubic-pair codegree restriction make D simple, with

    degree_D(v) <= 3 - degree_C(v).

D is disjoint from C squared: an adjacent cubic pair sharing a quartic
would violate cubic-neighborhood independence; a pair at distance two
in C would otherwise have two common neighbors.

The conflict graph F = C squared union D joins exactly pairs that are
adjacent or have intersecting neighborhoods in J. An independent triple
S in F therefore consists of three nonadjacent cubics with pairwise
disjoint neighborhoods. Seek one with

    sum over v in S of (1 + degree_C(v)) >= 7.

The checker enumerates all 34 possible types of C: partitions into at
most three paths, together with no even cycle, one of lengths 6,8,10,12,
or two cycles of length six. For each type it considers every triple
satisfying the displayed weight bound that is independent in C squared.
If no suitable triple exists in F, each such triple must contain a D edge.

The finite search exhausts these edge-covering conditions, subject to the
D degree capacities. At an uncovered triple it branches on the first
selected available pair, excluding preceding pairs. These branches are
disjoint and cover every possible D. Exhausted capacities forbid the
remaining incident pairs. A terminal may specify only a partial D, so the
checker explicitly requires that every surviving terminal saturates all
capacities before drawing a uniqueness conclusion.

There is exactly one surviving case: C is two 6-cycles, and D is the
opposite-pair matching on each cycle. All other types have a suitable
weighted independent triple. This finite check uses only 342 search nodes.

The exceptional case has treewidth at most five, so cannot be J. In each
6-cycle, attach its three distinct quartic neighbors to opposite pairs.
Eliminate the six cycle vertices in the order 0,3,1,4,2,5. The checker
verifies that the width is at most four, leaving only a triangle on those
three quartics. The two cycles use six distinct quartics because each
quartic has at most two cubic neighbors. The original induced graph on
all nine quartics has 12 edges. After the two eliminations it has at most
18 edges, so has treewidth at most five by f(6)=21. The whole J therefore
has treewidth at most five.

## 4. Three disjoint triangles in the prior 36-edge family

A suitable independent triple S thus exists. Eliminate its three cubics.
Each neighborhood is independent and the neighborhoods are disjoint,
so all three eliminations preserve the 36-edge count and every remaining
degree stays between three and five. The result has 18 vertices and

    12 - sum over v in S of (1 + degree_C(v))

cubics, a number between three and five. It belongs to the earlier complete
36-edge family with maximum degree at most five and at most five cubics.
This is the same explicitly cited prior family used by the general J20
packing theorem; its complete construction includes the 31-edge input.

The inverse replaces three vertex-disjoint triangles by new cubic centers.
Every triangle vertex has degree four or five before the inverse. Every
triangle contains at least one degree-five vertex, because the removed
cubic had at most two cubic neighbors. All degree-five vertices of the
18-vertex graph lie in the selected triangles: J originally had maximum
degree four.

The checker reads the hash-pinned prior family and enumerates every such
triple of triangles. There are 2,815 eligible bases with three cubics,
446 with four, and 13 with five. Only eight inverse choices satisfy the
conditions. Every one has a cubic with at least three cubic neighbors,
contradicting the established maximum degree two of C. No inverse survives.

This exhausts the alternatives, and excludes the high-claw profile.

## Reproduction

```sh
python3 -O scripts/verify_order25_claw.py
```

The source-only check takes about two seconds. It first checks the exact
claw/private-incidence premise against the independently generated
order-25 catalogue, then executes the finite weighted-packing check and
all prior-family inverses. It does not accept saved search statuses.
The earlier classifications and one-high theorem remain explicit premises;
the script does not claim to reprove those larger results by itself.

For the complete order-25 check, freshly replay the 38 stored branch
certificates and apply the private-cycle and claw reductions:

`python3 -O scripts/verify_order25_complete.py`

An optional parallel replay is available on Python 3.11 or later:

`python3 -O scripts/verify_order25_complete.py --workers 4 --output order25-report.json`

Add `--check-new-premises --native` to replay the finite two-K4, no-isolate
H23 and one-high H23 checks as well. The earlier 29/34/35/36 classification
premises remain explicit. The master accepts no saved verification reports,
rejects duplicate or unknown roots and checks explicit maps to canonical roots, and fails unless every catalogue
profile is covered. It does not claim coverage of the other vertex counts.
