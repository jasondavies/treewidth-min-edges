# The 41-edge case

**Result:** no graph with at most 41 edges has treewidth at least nine.
Together with the certified 42-edge witness, this proves **f(9)=42**.
All enumerations and the final independent reconstruction have completed.

## Reduction to one residue family

Choose a minimum-order graph G with 41 edges and treewidth at least nine,
if one exists. The [40-edge exclusion](nine-40.md) and
low-degree elimination imply that G is connected and has minimum degree
four. Vertex deletion and f(8)=34 give maximum degree seven.

Deleting a degree-seven vertex leaves one of the two 34-edge graphs of
minimum degree at least three and treewidth at least eight. All **30,888**
seven-neighbor extensions have verified width-eight orders.

For degree six, the 35-edge classification has been broadened beyond the
restrictions used at 40 edges. Its 95 minimum-degree-four cores and full
triangle-to-star closure give **130** minimum-degree-three graphs of
treewidth at least eight, on 13 through 18 vertices. No order or prospective
degree-five filter was used in this closure. Every one of their
**1,126,359** six-neighbor extensions has a verified width-eight order.
[Classification](../sources/nine/treewidth35-all-classification.json) and
[extension results](../sources/nine/treewidth41-high-degree-exclusions.json).

Thus G has only degrees four and five, with these possibilities:

| Vertices | Degree four | Degree five |
|---|---:|---:|
| 17 | 3 | 14 |
| 18 | 8 | 10 |
| 19 | 13 | 6 |
| 20 | 18 | 2 |

There is always a degree-five vertex. Deleting one gives a graph H with
36 edges, order 16 through 19, degrees three through five, at most five
degree-three vertices, and treewidth at least eight. Conversely, restore
the deleted vertex by joining it to all degree-three vertices and enough
degree-four vertices to give it degree five. Degree-five vertices cannot
be neighbors, because degree six has already been excluded.

## Classifying the 36-edge cores

A minimum-degree-four 36-edge core of treewidth at least eight has maximum
degree eight, by f(7)=28. Choose a vertex of maximum degree:

| Maximum degree | Residue after deletion |
|---|---|
| 8 | K8 or F (28 edges) |
| 7 | The complete 29-edge minimum-degree-three family |
| 6 | A 30-edge minimum-degree-three graph, maximum degree six, at most six degree-three vertices, order at most 16 |
| 5 | A 31-edge minimum-degree-three graph, maximum degree five, at most five degree-three vertices, order 14–16 |
| 4 | A quartic graph of order 18 |

The broader 30-edge closure has **73,517** retained graphs through order
16 and with at most six degree-three vertices, without a maximum-degree
restriction on intermediates. It is generated from the earlier 30-edge
cores and the 28/29-edge families.

The complete quartic order-18 GENREG search retains **413** graphs. Its
1,024 partitions cover 195,854,903 branches using verified supergraphs
and check 2,039,930 leaf graphs. These are not counts of all graphs in the
unpruned class.

## The 31-edge residues

A 31-edge minimum-degree-four core of treewidth at least seven has maximum
degree nine. Degree at least eleven would leave at most 20 edges and
treewidth at least six. Degree ten would leave the unique 21-edge
minimum-degree-three graph of treewidth at least six, K7, forcing an
impossible eight-vertex 31-edge graph.

Therefore enumerate connected graphs of orders 9–15 with exactly 31 edges
and degrees between four and nine. A verified pruning rule makes this
enumeration much smaller: if the current induced partial graph P has n
vertices and a width at most 6-(N-n) order, every N-vertex extension has
treewidth at most six. Add the N-n missing vertices to every bag of a
decomposition of P. The order is independently verified before pruning;
an unsuccessful or interrupted bounded search never prunes.

All **1,792** partitions completed, with **36,385,309** checked leaf
graphs, **236,175,966** verified prefix covers, and **882,135** retained
cores. The retained lists agree with the complete unpruned enumerations
at orders 9–12. A separate partition audit agrees with an unsplit run.

Recover the required minimum-degree-three graphs by inverse degree-three
eliminations. From 31 edges, the first edge-losing elimination can leave
30, 29, or 28 edges. Start with the corresponding lower-edge family,
replace a triangle by a degree-three star, and retain respectively one,
two, or three of the triangle edges. Then close under full triangle-to-star
moves, which preserve the edge count.

One minimum-degree issue requires care. An elimination losing two edges
could make a neighbor degree two. That neighbor would have adjacent
neighbors in the resulting 29-edge graph; eliminating it would leave at
most 27 edges while preserving treewidth at least seven, impossible.
Thus the 29-edge residue has minimum degree three. If three edges are
lost, the 28-edge residue is K8 or F. A one-edge loss preserves minimum
degree three and decreases the number of degree-three vertices, so the
broader 30-edge family contains every needed residue.

The resulting needed 31-edge family has 1,019,117 graphs of order 14,
2,538,974 of order 15, and 981,553 of order 16. Every graph has maximum
degree five, minimum degree three, and at most five degree-three vertices.

## Recover the 36-edge residues and restore the last vertex

For a 36-edge minimum-degree-three graph of treewidth at least eight,
degree-three elimination can preserve the edge count or lose one edge.
A loss of at least three would contradict f(8)=34. A loss of two gives
34 edges and a triangle. A degree-two vertex in that result would itself
contradict f(8)=34 by elimination; otherwise the triangle contradicts the
triangle-free 34-edge classification. A one-edge loss gives a member of
the complete 35-edge minimum-degree-three family.

Consequently start with the 36-edge cores above, or a partial
triangle-to-star move retaining one edge in a 35-edge graph, and close
under full moves. Retain the required orders 16–19, maximum degree five,
and at most five degree-three vertices. The necessary intermediate
bounds use the fact that each full move creates a permanent degree-three
vertex and reduces each of three old degrees by one.

The [classifier](../scripts/nine/classify_treewidth36.py) retains exactly
**53,898** possible residues:

| Order | Retained residues |
|---:|---:|
| 16 | 14,143 |
| 17 | 29,945 |
| 18 | 9,345 |
| 19 | 465 |

The [classification report](../sources/nine/treewidth36-classification.json)
and [complete final residue list](../sources/nine/treewidth36-family.g6)
are included. Restoring the degree-five vertex gives **22,489,604**
extensions. Every one has a width-eight elimination order, checked by the
C verifier using paths in the original graph. The independent Python audit
rebuilds all these extensions using sets and checks each elimination order
by explicit filling. Its count agrees exactly with the C construction.

[Final C report](../sources/nine/treewidth41-extensions.json),
[Python audit report](../sources/nine/treewidth41-audit.json).

This excludes the final degree patterns and completes the lower bound.
The separate 21-vertex, 42-edge witness has a width-nine order and a closed
set of 115,440 width-eight elimination prefixes excluding the full vertex
set. These certify treewidth exactly nine, proving **f(9)=42**.

See [full reproduction](../proof-nine.md#reproduction). No experimental
matching-extension searches or unfinished template searches are dependencies
of this proof.
