# Forty edges are insufficient for treewidth nine

**Result:** every finite simple undirected graph with at most 40 edges has
treewidth at most eight. This is the intermediate bound

\[
\boxed{41\le f(9)\le42.}
\]

The subsequent [41-edge exclusion](nine-41.md) establishes the exact value 42.
The full reproduction driver runs every dependency of this argument.

## 1. Reduce to degrees four and five

Use the earlier [39-edge exclusion](../proof-nine.md#39-edges) and
[34-edge optimum for treewidth eight](../proof.md). Suppose a
counterexample exists, and choose one, G, with the fewest vertices.
It is connected, has exactly 40 edges, and has minimum degree at least
four: eliminating a vertex of degree at most three never increases the
edge count, and preserves treewidth at least nine.

Deleting any vertex leaves treewidth at least eight, hence at least 34
edges. Thus G has maximum degree six.

The [34-edge classification](../proof.md#8-classification-at-34-edges-exactly-two-connected-graphs) gives just
two graphs of minimum degree at least three and treewidth at least eight,
on 16 and 17 vertices. Both are triangle-free. Deleting a degree-six vertex
from G would give one of these graphs. All

\[
\binom{16}{6}+\binom{17}{6}=20,384
\]

extensions have verified width-eight orders. Therefore every vertex of G
has degree four or five, and 16 <= |V(G)| <= 20.

A degree-four vertex lies in at most one triangle. If it lay in at least
two, eliminating it would remove four edges and add at most four, again
giving a smaller counterexample. The same argument bounds the number of
triangles at a degree-five vertex by four.

There are now two cases: G has a degree-five vertex, or G is quartic on
20 vertices.

## 2. The smaller classifications used below

The earlier [28-edge classification](../proof.md) says that the only
connected graphs with at most 28 edges and treewidth at least seven are
K8 and the 12-vertex graph F. The 34-edge classification also established
the 29-edge minimum-degree-three family through order 15: **280** graphs.
The base reproduction checks **518,071,774** minimum-degree-four cores
(with the slightly looser maximum-degree-eight bound) and retains the same
124 cores used here. Extending its
order-15 graphs by a full triangle-to-star move produces two candidates;
both have verified width-six orders. In particular, there is **no**
29-edge, order-16 graph of minimum degree at least three and treewidth
at least seven.

For 30 edges, first enumerate connected cores of minimum degree four and
treewidth at least seven. Their maximum degree is eight. Indeed, a vertex
of degree at least ten would leave at most 20 edges and treewidth at least
six. A degree-nine vertex would leave a 21-edge graph of minimum degree
at least three and treewidth at least six, necessarily K7 by the
[small 21-edge classification](../proof-nine.md#small-residue-classifications).
The original graph would then have eight vertices and 30 edges, impossible.

Consequently the required core enumeration is exactly

```
geng -c -d4 -D8 n 30:30       (9 <= n <= 15).
```

All **2,664,344,484** graphs were checked; **13,206** were retained.
[Full partition results](../sources/nine/treewidth30-core-results.json) and
[retained cores](../sources/nine/treewidth30-cores.g6) are saved.

To recover minimum-degree-three graphs, eliminate degree-three vertices.
If their neighborhoods contain t edges, elimination loses t edges. Since
treewidth at least seven requires at least 28 edges, a 30-edge graph can
lose zero, one or two edges. Reverse these possibilities as follows:

* Start with a retained 30-edge core.
* Or start with a 29-edge graph, replace a triangle by a degree-three
  star, and retain one of the three triangle edges. This adds one edge.
* Or start with K8 or F, make the same replacement, and retain two triangle
  edges. This adds two edges.
* Thereafter apply full triangle-to-star moves, retaining no triangle
  edges. These preserve the edge count.

Require minimum degree three after every move. Every intermediate graph
on the reverse path to a graph of treewidth at least seven must itself
have treewidth at least seven, so graphs with verified width-six orders
can be discarded.

The classifiers also use elementary size bounds. A full triangle-to-star
move creates a degree-three vertex and decreases each of the three old
degrees by one. Degree-three vertices cannot participate in a later move
that preserves minimum degree three. Thus the number of degree-three
vertices never decreases. Each move reduces the total excess over a
specified maximum degree by at most three, and any one degree by at most
one. The code applies these necessary bounds only to omit intermediates
that cannot reach the specified final order and degrees.

Two resulting subfamilies are used:

| Required residue | Number retained |
|---|---:|
| 30 edges, order 16, degrees 3,3,3,3,4,...,4 | 814 |
| 30 edges, order 13, degrees 3–5, at most five degree-three vertices | 4,885 |
| Same, order 14 | 22,446 |
| Same, order 15 | 12,959 |
| Same, order 16 | 1,235 |

[Quartic-residue classifier](../scripts/nine/classify_treewidth30_quartic.py),
[other residue classifier](../scripts/nine/classify_treewidth35.py), and
[quartic residue list](../sources/nine/treewidth30-quartic-family.g6).
These lists need only contain every possible residue; additional retained
graphs would not invalidate the final positive extension checks.

## 3. Exclude every graph with a degree-five vertex

Deleting that vertex from G gives a 35-edge graph H, of order 15 through
18, with degrees between three and five, at most five degree-three
vertices, and treewidth at least eight.

Eliminating a degree-three vertex of H cannot lose two or more edges, by
f(8)=34. It cannot lose exactly one either: the resulting 34-edge graph
would have minimum degree at least three and contain the triangle created
by elimination, contradicting the triangle-free 34-edge classification.
Thus only edge-preserving eliminations occur. H is obtained by full
triangle-to-star moves from a 35-edge core of minimum degree four.

Such a core has maximum degree seven, by f(7)=28. The possibilities are
exhaustive:

* A degree-seven vertex deletes to K8 or F.
* A degree-six vertex deletes to the 29-edge minimum-degree-three family.
  There is no order-16 residue, as checked above.
* If all degrees are four or five, the core has order 14 through 17 and
  has a degree-five vertex. Deleting it gives one of the 30-edge residues
  of orders 13 through 16 in the table. All degree-three vertices must
  be neighbors when it is restored; its other neighbors have degree four.
* An all-quartic 35-edge core is impossible, since 35 is odd.

The construction tests **2,701,005** nonisomorphic relevant core candidates,
retaining 95. Closing under full triangle-to-star moves and imposing the
required final degrees gives **93** possible H:

| Order of H | Number retained |
|---|---:|
| 15 | 7 |
| 16 | 49 |
| 17 | 28 |
| 18 | 9 |

[Classification results](../sources/nine/treewidth35-classification.json) and
[the 93 residues](../sources/nine/treewidth35-family.g6).

Restore the deleted degree-five vertex. Every degree-three vertex must
be its neighbor; remaining neighbors can only have degree four, because
degree six has already been excluded. There are **72,751** extensions.
Every one has a verified width-eight order. This excludes all four
degree patterns on 16 through 19 vertices, including the regular
order-16 case. The separate large regular enumeration is therefore no
longer needed as a logical dependency.

## 4. Exclude the quartic order-20 case

### Pairs with three or four common neighbors

Adjacent vertices cannot have two common neighbors, by the triangle bound.
For nonadjacent vertices u,v, their common neighbors are independent:
an edge between two common neighbors would put each in two triangles.

Deleting u,v leaves 32 edges and treewidth at least seven. Smooth the
common degree-two vertices. This preserves the treewidth lower bound
and cannot create isolated vertices among the survivors: an endpoint
incident to a removed degree-two vertex retains, or gains, an edge to
that vertex's other endpoint.

Four common neighbors would give at most 28 edges on fourteen vertices,
with no isolates. The component of treewidth at least seven must consume
all 28 edges and be K8 or F, an order contradiction.

With three common neighbors, the result must have exactly 29 edges on
fifteen vertices; at most 28 is impossible for the same reason. Every
smoothing must therefore replace its two edges by a new edge, preserving
all other degrees. The result has two degree-three vertices and thirteen
degree-four vertices. There are only three such 29-edge residues.
Subdivide any three distinct edges, attach two new vertices to all three
subdivision vertices, and attach one new vertex to each degree-three
vertex. All **10,962** extensions have width-eight orders, verified again
in Python. [Reproduction](../scripts/nine/check_treewidth40_quartic_codegree.py).

Thus every pair has at most two common neighbors.

### A four-cycle reduces to the 814 residues

Suppose G contains a four-cycle, and choose opposite vertices u,v. They
are nonadjacent and have exactly two common neighbors. Delete u,v and
smooth those two neighbors. The result has sixteen vertices and at most
30 edges, and still has treewidth at least seven.

The result has minimum degree at least three, even if a smoothing finds
an edge already present. To see this, write x,y for the other two neighbors
of a common neighbor c. If xy already exists, cxy is a triangle. Neither
x nor y can also be adjacent to u or v, since that would give c a second
triangle. Consequently their degrees before smoothing are four, and this
smoothing reduces them only to three. Two such triangles cannot share an
endpoint, by the triangle bound. The two smoothing edges also cannot
coincide: their subdivision vertices would have four common neighbors,
already excluded. Successful smoothings preserve the other degrees.

At most 28 edges contradicts the K8/F classification; 29 contradicts the
absence of order-16 minimum-degree-three 29-edge residues. The result
therefore has exactly 30 edges and degrees 3,3,3,3,4,...,4, so it is one of
the **814** classified graphs.

Reverse the operations: subdivide two distinct edges, add two vertices
adjacent to both subdivision vertices, and partition the four
degree-three vertices into two pairs, one pair for each new vertex.
There are three unordered partitions, giving

\[
814\binom{30}{2}\cdot3=1,062,270
\]

extensions. Every extension has a verified width-eight order.
[C reconstruction](../scripts/nine/treewidth40_four_cycle.c).

### No four-cycle

The remaining subcase is quartic order 20, with at most one triangle
through any vertex and no pair having two common neighbors. GENREG
enumerates this subcase, pruning partial graphs that already violate
these conditions. It also prunes a branch when a supergraph of every
completion has a verified width-eight order.

All **64** partitions completed. There were **1,622,068** verified
supergraph covers and **7** remaining leaf graphs, all with width-eight
orders. These are branch/leaf counts, not a count of distinct graphs in
the unpruned class.
[Results](../sources/nine/treewidth40-no-four-cycles.json) and
[build manifest](../sources/nine/treewidth40-no-four-cycles-manifest.json).

This completes the quartic case and hence the 40-edge exclusion.

## 5. Verification and reproduction

Every positive C certificate is checked through paths in the original
graph, independently of the fill operations used by the search. The
classifiers also check discarded orders in Python using sets. Finally,
an independent Python construction rebuilt **all 72,751 degree-five
extensions and all 1,062,270 four-cycle extensions**, and verified an
order for every graph. Its counts agree with the C constructions.
[Full final audit](../sources/nine/treewidth40-final-extension-audit.json).

The regular-generator callback and partitioning have separate small-case
audits against unpruned enumeration and nauty. Exact-key caching only
reuses a result after comparing the complete adjacency masks; hash
collisions alone cannot prune a graph. None of the incomplete mixed-case
template searches, heuristic witness searches, or experimental symmetry
pruning is used in this proof.

See [full reproduction](../proof-nine.md#reproduction). The driver regenerates
both prerequisite classifications, all the residue families above, and the
64-partition GENREG search. It also reconstructs all 72,751 degree-five and
1,062,270 four-cycle extensions independently in Python.
