# A small reconstruction domain for marked 42-edge residues

The finite reconstruction check is complete, relative to the explicit
earlier-classification premises below. It proves the marked-residue
characterization and checks the required reconstructions of its exception.
It does not, by itself, exclude every 52-edge graph.

The prerequisite is the earlier result f(9)=42, together with the complete
34-, 35-, and specified 36-edge classifications in the treewidth-nine proof.
No classification from the archived 52-edge computation is a premise.

## The marked residue

Let H be a simple graph with 22 vertices and 42 edges, with four vertices
of degree three and eighteen of degree four. Write L for its cubic vertices
and suppose tw(H) is at least nine. The application singles out a quartic
vertex w adjacent to two members of an independent set S contained in L,
where every member of L minus S has exactly one neighbor in S. The graph
H[L] is a proper subgraph of K(2,2).

The finite check establishes that every such H is isomorphic to

```text
UqGOOICQ@GB?Oo_oCG?c@?E??c?@?o?`G?IC?@Q?
```

For this implication, no lower-bound certificate for the displayed graph
is needed. A checked width-eight order excludes a reconstruction; a checked
isomorphism identifies it as this permitted exception. An unresolved graph
would make the computation fail, rather than being classified as an exception.

## Two consequences of f(9)=42

Every cubic neighborhood in H is independent. Eliminating a cubic vertex
whose neighborhood already contains an edge preserves treewidth at least
nine and loses at least one edge, contradicting f(9)=42.

Two cubic vertices have at most one common neighbor. If they are adjacent,
a common neighbor already contradicts the preceding fact. Otherwise,
eliminating one inserts an edge between two shared neighbors; the other
remains cubic, and eliminating it then loses an edge, again a contradiction.

Also H is two-connected. A disconnected graph, or a graph decomposed at a
cut vertex, has treewidth equal to the maximum among its pieces. A piece
with treewidth at least nine would already require all 42 edges. Every
other piece has an edge because H has minimum degree three, which is
impossible. In particular, H-w is connected.

## Delete one vertex and smooth its cubic neighbors

Put r=|N_H(w) intersect L|. The mark gives 2 <= r <= 4. These r vertices
are independent, since two adjacent ones would form a triangle with w.
For each, its two neighbors other than w are nonadjacent. These pairs
are pairwise disjoint: two cubics already share w, so cannot share another
neighbor.

Delete w and suppress all r of these degree-two vertices. Each suppression
inserts one new edge and removes two. The replacement edges form a matching,
and every surviving degree is preserved by the suppressions. The resulting
connected graph J therefore has exactly

    |V(J)| = 21-r,    |E(J)| = 38-r,    tw(J) >= 8.

Its cubic vertices consist of the 4-r original cubics not adjacent to w
and the 4-r quartic neighbors of w. Every other vertex has degree four.
There are exactly three possibilities:

| r | Order of J | Edges | Cubic vertices | Classified residues |
|---:|---:|---:|---:|---:|
| 2 | 19 | 36 | 4 | 457 |
| 3 | 18 | 35 | 2 | 9 |
| 4 | 17 | 34 | 0 | 1 |

This uses no further suppression, no degree-zero deletion, and no
quartic 18-vertex/36-edge case.

The complete 36-edge classifier covers orders 16 through 19, minimum
degree three, maximum degree five, and at most five cubic vertices. The
first row lies within every bound. Completeness requires its `--family31`
input, the broad 30-edge family, and the complete quartic order-18 search;
the version omitting `--family31` is explicitly only exploratory. The
full 35-edge classification and the 34-edge classification cover the
other two rows. The independent audit checks these exact scopes, source
hashes, and the saved reports' complete status.

These earlier classifications are explicit mathematical dependencies.
The small checker does not itself replace their full regeneration. That
regeneration is available through `scripts/reproduce_nine.py --full` with
the prerequisites specified in the treewidth-nine proof.

## Exhaustive inverse construction

For each J in the table:

1. Choose 4-r of its 2(4-r) cubic vertices, forming X. These are the
   vertices that were quartic neighbors of w.
2. Choose an r-edge matching in J avoiding X. Subdivide each chosen edge
   once, creating a set Z of r new cubic vertices.
3. Add w adjacent to every member of X and Z.

This returns exactly 22 vertices and 42 edges, with four cubic vertices
L=(cubic vertices of J minus X) union Z and eighteen quartic vertices.
Every original marked H occurs: its smoothing edges are a matching,
and none meets X, since otherwise the corresponding subdivision vertex
would have adjacent neighbors w and a member of X.

The matching/avoidance choices give exactly

    990,306 + 46,872 + 11,889 = 1,049,067

constructions. These counts are diagnostics; the verifier traverses the
choices directly. It may reject a construction violating either cubic
minimum-edge consequence proved above, or the required marked pattern.
The latter requires a suitable independent S with at least two vertices
in Z. This retains every target: choose its originally marked w before
applying the reduction, and those marked cubic neighbors become members
of Z. The verifier need not retain another reconstruction of the same
unmarked graph with an unsuitable choice of w.

Every surviving construction must then receive either a width-eight
elimination order, verified by explicit filling, or a bijection to the
displayed exception, verified on every vertex pair. Neither a heuristic
failure nor an unfinished family is an exclusion proof.

## Checked results and source-only reproduction

Of the 1,049,067 inverse constructions, 998,030 meet the target conditions.
The C producer supplies width-eight orders for 998,029 and an exact
exception isomorphism for one. Independent Python enumeration and replay
checks every choice and every supplied order or map, and rejects missing
or extra records. The recorded separate run took 62.22 CPU seconds for
production and 44.01 seconds for independent replay.
The final portable pipeline, with both processes sharing one CPU, completed
the same full check in 107.04 seconds without saving a transcript.

The portable command rebuilds an untrusted producer, independently derives
the 467 starting graphs from the earlier classified sources, and checks
its output as a stream:

```sh
python3 -O scripts/verify_marked_residue_reconstructions.py --native
```

The `--native` flag affects only producer compilation. The command needs
a C compiler and Python's standard library; it reads the earlier
`sources/nine` families already present in the repository. Their hashes
pin the precise classification premises. It neither reads nor writes a
large reconstruction transcript by default. An optional `--output FILE.xz`
saves a checked transcript atomically. This is a source-only reproduction
of the finite check, not a replacement for regenerating its earlier
classification prerequisites.

## Application to a quartic square

Let G be a triangle-free four-regular graph on 26 vertices with treewidth
at least eleven. The [square-cap lemma](proof-eleven-quartic-square-cap.md)
gives at most two common neighbors for every vertex pair. For a square
x-a-y-b-x, the opposite vertices x,y therefore have exactly the common
neighbors a,b. Deleting x,y leaves 44 edges and treewidth at least nine.
Suppress a,b, which now have degree two. Their replacement edges are new
by triangle-freeness and vertex-disjoint because a,b already share x,y.

Write L for the two private neighbors of x and the two private neighbors
of y. The replacement edges avoid L: an endpoint meeting x or y would
form a triangle with a or b. Thus the resulting H has 22 vertices, 42
edges, and exactly the four cubics L. Each private pair is independent,
so H[L] is a subgraph of K(2,2). It is proper, since a four-cycle among
cubics would violate the two-common-neighbor consequence of f(9)=42.

If an eligible independent exact-dominating S in L had two members with
a common neighbor outside L, the marked-residue theorem would identify H
as the exception. The following reconstruction check excludes that case.
Consequently, **every such S has pairwise disjoint neighborhoods outside
L**. This is a local restriction, not an exclusion of all square cases.

For the quartic square application, choose any two vertex-disjoint edges
of the exception avoiding its four cubics. Subdivide them, add the two
opposite square vertices, and distribute the cubics between the latter
in all three unordered balanced ways. After the previously proved
triangle and common-neighbor restrictions, this gives 983 constructions.
All have independently checked width-ten orders:

```sh
python3 -O scripts/verify_exceptional_quartic_square.py --native
```

This command generates the graphs and obtains fresh proposed orders; it
uses no archived order file. Its recorded full run took 0.23 seconds.
The retained checkers import the fixed graph identity and strict graph6 decoder
from `scripts/marked_residue_common.py`. The residue producer's C header
is generated from that shared identity at compilation time. Its maps are
still checked against the Python identity on every vertex pair.

The tests exercise the pinned family inputs, width and map verification,
truncated and extra proof records, malformed orders, the required marked
pair, and cleanup of an invalid producer without publishing its output.
