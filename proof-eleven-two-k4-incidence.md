# A finite two-K4 incidence lemma

Every graph in the following family has treewidth at most seven. Start
with two disjoint copies of K4 and subdivide all twelve edges once.
Add a graph of degree two on the twelve subdivision vertices, subject to
this restriction: an added edge within one copy may join only subdivision
vertices corresponding to disjoint original edges. Added edges between
copies are unrestricted. The resulting graph has twenty vertices,
thirty-six edges, eight cubic vertices, and twelve quartic vertices.

This statement is established by a small exhaustive check below. It has
no dependency on the earlier large edge-minimum classifications. It is
a lemma about this family, not a classification of all thirty-six-edge
graphs.

## The structural consequence

Suppose J has twenty vertices, eight of degree three and twelve of degree
four. Let C be its cubic vertices. Assume:

- C is independent;
- each quartic vertex has at most two neighbors in C;
- the neighbors of each cubic vertex are independent;
- two distinct cubic vertices have at most one common neighbor.

Then either three cubic vertices have pairwise disjoint neighborhoods,
or J has treewidth at most seven.

Indeed, the eight cubics supply twenty-four incidences with the twelve
quartics. This equals the total capacity of two incidences per quartic,
so every quartic is adjacent to exactly two cubics. Construct a graph R
on C, with one edge for each quartic, joining its two cubic neighbors.
The common-neighbor hypothesis makes R simple, and R is 3-regular.
Three cubics with pairwise disjoint neighborhoods are exactly an
independent triple in R.

If there is no such triple, the complement of R is a triangle-free
4-regular graph on eight vertices. For any edge uv of the complement,
its two neighborhoods are disjoint independent four-element sets.
Together they contain all vertices. Degree four then forces every edge
between the sets: the complement is K(4,4), so R is two disjoint copies
of K4.

Each quartic now corresponds to one edge of one K4. Its two remaining
neighbors are quartic, and these remaining edges form a graph of degree
two on twelve vertices. Cubic-neighborhood independence forbids an edge
joining two quartics representing incident edges of a K4. This is
exactly the family in the first paragraph, so the finite check applies.

## Four exhaustive cases

Number the six edges of each K4 in the order

    01, 02, 03, 12, 13, 23.

The only permitted pairs within one six-vertex side are the three
opposite-edge pairs (0,5), (1,4), and (2,3). They are disjoint, so any
subset of them may be selected. If a pairs are selected on the first
side and b on the second, the numbers of edges joining the sides are
12-2a and 12-2b respectively; hence a=b.

Permutations of the four vertices of a K4 act transitively on its three
opposite-edge pairs. Consequently they act transitively on subsets of
each fixed size: for size two use complements; sizes zero and three are
unique. Relabel the two K4 copies independently. For each a in {0,1,2,3},
we may therefore assume that both sides select the first a pairs.

What remains is a 6 by 6 zero-one matrix describing the edges between
sides. A vertex incident with a selected internal pair has matrix degree
one; every other vertex has matrix degree two. All matrices with these
row and column sums are enumerated. Their counts are:

| Internal pairs per side | Matrices |
|---:|---:|
| 0 | 67,950 |
| 1 | 9,876 |
| 2 | 2,172 |
| 3 | 720 |
| Total | 80,718 |

No graph-isomorphism program or unverified canonicalization is used.
Some graphs may occur more than once, which does not affect exhaustion.

## Reproduction

Run:

```sh
python3 -O scripts/verify_two_k4_incidence.py
```

The standalone script requires only Python's standard library. It
constructs every matrix row by row, preserving its prescribed sum and
remaining column capacities. It rejects a partial row only if a column
would need a negative number of edges or more edges than there are rows
left. Thus every allowed matrix is visited.

For each graph, a greedy algorithm using integer adjacency masks proposes
an elimination order. A separate checker using sets fills every eliminated
neighborhood and checks that its size is at most seven. A failed heuristic
or invalid order aborts the computation; neither counts as an exclusion.
No graph file, elimination-order file, C compiler, or external package is
needed.

All 80,718 graphs pass. The full standalone run took 10.67 seconds. An
independently implemented C enumerator gave the same counts and graph
stream, with all orders also checked by Python. The common diagnostic
SHA256 of the graph stream is

```text
b0dacb8d9d1b94e4093cccb2bedc58618ab38430f636f1a910d9b17988b67b47
```

Tests compare matrix counts against an independent dynamic program,
check the normalization explicitly over all twenty-four permutations
of K4, and reject malformed or false width-seven orders. The counts and
hash are diagnostics; soundness comes from exhaustive generation and
checking every order.
