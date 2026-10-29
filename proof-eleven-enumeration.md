# The two remaining quartic enumerations

These are the two enumeration components of the [52-edge exclusion](proof-eleven.md).
The [verification guide](verification-eleven.md) runs both, after checking their
finite premises. They apply to minimum-order counterexamples, not arbitrary
52-edge graphs.

## Girth at least five

Every component in a quartic graph of girth at least five has at least
1+4+12=17 vertices: the first two distance layers around a vertex must be
distinct, or there is a triangle or four-cycle. A 26-vertex graph in this
class is therefore connected. GENREG's restriction to connected graphs
loses no instances here.

## Pruning proof

GENREG fills adjacency rows in order. When the adapter is called, all
vertices before `start` have their final neighborhoods. Let A be the
partial graph at this node. Construct U by retaining every edge of A and
adding every pair v,w satisfying all of the following:

1. Both vertices are in the unfinished suffix.
2. Both currently have degree less than four.
3. Their distance in A is greater than three, or no path connects them.

Every girth-at-least-five quartic completion of A is a subgraph of U:
vertices whose rows or degrees are complete cannot receive another edge;
a new edge between vertices already joined by a path of length at most
three would create a cycle of length at most four. Later edge additions
cannot remove that cycle.

Consequently, a verified width-ten elimination order of U proves that
every completion at this node has treewidth at most ten. The adapter prunes
only on such a verified order. If its greedy heuristic fails, it continues
the exhaustive generation. At each remaining leaf, it runs the exact
width-ten checker and independently verifies every positive elimination
order using original paths through the eliminated set.

The adapter is inserted before the generator advances its completed row.
It does not change the generator's canonical-labeling or partitioning
rules. All 256 modulo partitions must finish before an exclusion can be
concluded. A negative checker answer instead stops the search and must be
certified independently in Python.

## Square families

For a chosen vertex v, encode shared external neighbors of its four neighbors
by a graph J on four vertices. The square-cap and square-direction lemmas in
[the main proof](proof-eleven.md) leave five types: an edge, two adjacent
edges, two disjoint edges, a three-edge star, and a four-vertex path.
Every other neighbor slot is private. This determines the radius-two prefix;
edges outside the completed first five neighborhoods remain unknown.
The root is chosen with maximum square incidence, so its number of squares
bounds the number at every vertex. Root canonicalization preserves that
choice. `verify_eleven_square_roots.py` regenerates the catalogue and checks
that each family is contained in its corresponding archived root.

The completion kernels process adjacency rows exhaustively, up to the stated
root-preserving symmetries. They propagate degree four, triangle-freeness,
common-neighbor bounds, and the root's maximum-square cap. The
[square-direction lemma](proof-eleven-quartic-square-directions.md) also
supplies the necessary marked-residue restrictions: independent cubic
neighborhoods, bounded common neighbors, and the restrictions obtained by
eliminating independent sets that dominate the other cubic vertices once.
The propagated kernel applies these to every completed square. The final
kernel additionally uses the [path exclusion](proof-eleven-quartic-path-certificate.md)
at every vertex. These are necessary conditions, so propagation cannot
remove a counterexample.

The shared threshold filter deletes vertices and eliminates only fully known
neighborhoods, applying the earlier edge minima and complete small-edge
classifications. Its implementation and mathematical comments are in
[treewidth_threshold_graph35.h](research/eleven/scripts/treewidth_threshold_graph35.h).
Uniform width-ten covers are elimination orders of supergraphs containing
all allowed completions; the code verifies each order before pruning.
A failed heuristic leaves the branch to exhaustive enumeration.
The [interval-cover code](research/eleven/scripts/treewidth_interval_cover.h)
and [degree-cover code](research/eleven/scripts/treewidth_degree_cover_forbidden.h)
state the supergraph constructions. These sources, canonicalization, and
the enumeration logic remain trusted parts of the computer-assisted proof.

The five archived stages hand off exactly their unfinished canonical prefixes:

| Stage | Roots | Completed terminals | Splits or cuts | Unfinished roots handed off |
| --- | ---: | ---: | ---: | ---: |
| Corner restrictions | 5 | 12,047 | 681 | 219 |
| Propagated constraints | 219 | 17,230 | 770 | 103 |
| Path exclusion | 103 | 14,099 | 711 | 158 |
| Cooperative continuation | 158 | 109,313 | 2,481 | 163 |
| Final continuation | 163 | 13,842 | 252 | 0 |

An export does not prove exclusion. Every exported prefix must be covered
in the next stage. The series auditor checks hashes, canonical child sets,
and frontier correspondence. The selected full command also reruns every
terminal search: 43,376 adaptive terminals and 123,155 cooperative terminals,
as well as 2,162 adaptive splits and 2,733 cooperative cuts. No unfinished
prefix or unresolved graph is accepted. See the
[original coverage audit](research/eleven/sources/treewidth-eleven-quartic-complete-audit.json)
and [replay wrapper](scripts/replay_eleven.py).

The archive contains the checkpoint directories, generated source, executables,
and frontiers. The replay wrapper maps their original paths into an isolated
mount namespace, preserving source hashes. The retained historical source
files are byte-for-byte originals; their integrity inventory is
[SHA256.json](research/eleven/SHA256.json).
