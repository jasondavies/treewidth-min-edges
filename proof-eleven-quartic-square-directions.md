# Six possible square-incidence types in a quartic obstruction

Let G be a triangle-free four-regular graph on 26 vertices with treewidth
at least eleven. The [square-cap lemma](proof-eleven-quartic-square-cap.md)
proves that every pair of vertices has at most two common neighbors and
that every vertex lies in at most four squares.

We use the proved
[marked-square neighborhood restriction](proof-eleven-marked-residue.md#application-to-a-quartic-square):
for a square x-a-y-b-x, delete x,y and suppress a,b. The four cubic
vertices L in the resulting graph H are the private neighbors of x and y.
They form a proper subgraph of K(2,2), with the two private pairs as its
parts. For every independent S contained in L such that every vertex of
L-S has exactly one neighbor in S, no two members of S have a common
neighbor outside L in H.

That restriction uses the complete marked-H22 characterization and the
independent check of 983 quartic reconstructions of its exception. It does
not use the archived 52-edge high-core classification.

## Disjoint square directions force adjacent opposite corners

Suppose two squares through v use disjoint pairs of its neighbors:

    v-a-p-b-v,       v-c-q-d-v.

Then p and q are adjacent. Assume otherwise and reduce the first square
by deleting v,p and suppressing a,b. Its four cubics are

    L = {c,d,s,t},

where s,t are the other two neighbors of p. These four vertices are
all distinct: any coincidence across the private pairs would give v,p
three common neighbors. The two private pairs are independent by
triangle-freeness.

The vertex q survives outside L. It cannot equal a or b, and cannot be
adjacent to a or b, because then q would meet three neighbors of v.
It is not a neighbor of v, by triangle-freeness, and it is not a neighbor
of p by the supposition. Thus q is a quartic outside L and remains a
common neighbor of c,d in H.

If c,d have no common neighbor inside L, take S to consist of c,d and
every member of {s,t} having no neighbor among c,d. The set S is
independent, and every vertex of L-S has exactly one neighbor in S.
The neighborhood restriction forbids their common outside neighbor q.
Consequently c,d must have a common neighbor in L. But they already have
the distinct common neighbors v,q in G, so this would be a third common
neighbor, again impossible. Hence pq is an edge.

Disjoint square directions are therefore allowed, but the edge pq is
forced; they must not simply be discarded.

## Three pairwise incident square directions are impossible

For a vertex v, define J_v on its four neighbors. Put ab in J_v when a,b
have a common neighbor other than v. Such a neighbor is unique by the
common-neighbor bound. Distinct edges of J_v have distinct extra common
neighbors: otherwise that vertex and v would have at least three common
neighbors.

Suppose J_v contains a triangle on a,b,c. Denote the extra common neighbors
for ab,ac,bc by p,q,r. The exact neighborhoods have the form

    N(a) = {v,p,q,alpha},
    N(b) = {v,p,r,beta},
    N(c) = {v,q,r,gamma}.

The three fourth neighbors alpha,beta,gamma are distinct, and none is any
of v,p,q,r or any neighbor of v. Simplicity excludes repeats within an
individual row; a fourth neighbor equal to the remaining shared corner
would meet three neighbors of v; equality between two fourth neighbors
would give the corresponding pair a third common neighbor. Adjacency
between two neighbors of v is excluded by triangle-freeness.

Reduce the square a-v-b-p-a by deleting a,b and suppressing v,p.
Now L={q,alpha,r,beta}, with parts {q,alpha} and {r,beta}. The vertices
q,r are nonadjacent, since both meet c; they share the quartic outside
neighbor c in H. If d is the fourth neighbor of v, suppressing v removes
the edge cv and inserts cd, which was absent by triangle-freeness. The
vertex p cannot meet c, since it already meets a,b and would then have
three common neighbors with v. Thus c remains quartic and outside L. If alpha,beta were also nonadjacent, the only possible
edges in H[L] would be the disjoint edges q-beta and alpha-r.
Choose S to contain q,r and every remaining isolated vertex of H[L].
This is an independent set that dominates every vertex of L-S exactly
once, contradicting the common outside neighbor c. Thus alpha-beta is
an edge.

The analogous reductions on a,c and b,c force alpha-gamma and beta-gamma.
These three edges make a triangle in G, a contradiction. Therefore J_v
is triangle-free.

## Exhaustive root catalogue

A vertex on a square has a nonempty J_v. Enumerate all 63 nonempty simple
graphs on four labeled vertices, retain the triangle-free graphs with at
most four edges, and take the least mask over all 24 explicit vertex
permutations. There are six types:

| Type | Edges | Labeled representatives |
|---|---:|---:|
| One edge and two isolated vertices | 1 | 6 |
| Three-vertex path and an isolate | 2 | 12 |
| Two disjoint edges | 2 | 3 |
| Three-edge star | 3 | 4 |
| Four-vertex path | 3 | 12 |
| Four-cycle | 4 | 3 |

In particular, the only four-square type is a four-cycle. The triangle
and triangle-with-pendant-edge types are excluded by the preceding hand
proof, not by a stored search result.

For a normalized root prefix, label the root0 and its neighbors1..4.
Create one distinct extra common neighbor for each edge of J, then give
each root neighbor enough distinct private neighbors to reach degree four.
There are 17-|E(J)| named vertices. Any identification between private
neighbors of different root neighbors would introduce another J edge or
violate the common-neighbor bound. Identifying a private neighbor with
an existing shared corner would give three root-neighbor incidences.
Thus this naming covers every completion up to relabeling.

For each two disjoint edges of J, add the forced edge between their shared
corners. This adds one edge for the matching and path types, two for the
four-cycle, and none for the other types. Unspecified edges remain free.

The source-only catalogue is regenerated with

```sh
python3 scripts/quartic_square_profiles.py
```

To print the four-cycle root as a one-line branch prefix:

```sh
python3 scripts/quartic_square_profiles.py --mask 30
```

## Excluding the four-square type

For a minimum-order 52-edge counterexample, the ordinary branch checker
excludes the four-cycle prefix using only two neighborhood branches and
thirteen numeric trace leaves. The saved certificate is 156 compressed
bytes and uses the original v1 format; no new proof opcode is needed.
Its root is regenerated from the catalogue and pinned exactly before replay.
The premise checker requires the original v1 format: a later structural rule
using this maximum-three conclusion is not allowed to prove its own premise.

```sh
python3 scripts/verify_quartic_four_square.py
```

Consequently every vertex of a triangle-free quartic minimum-order
52-edge counterexample lies in at most three squares. All five remaining incidence types are covered by the archived completion
searches. Their later stages also use the [path exclusion](proof-eleven-quartic-path-certificate.md)
globally. See [the enumeration proof](proof-eleven-enumeration.md).
The hand corollaries and catalogue normalization remain explicit premises;
the branch checker also uses its stated minimum-counterexample and earlier
edge-minimum premises.
