# A four-step exclusion of one complete 52-edge profile

One of the order-25 profiles has a short mathematical exclusion. Its
certificate is **440 bytes of uncompressed JSON** and specifies only four
vertex operations. No enumeration, symmetry reduction, or archived search
result is needed to check it.

This family was numbered **20** in the original search. This result
excludes every completion of this root; it does not exclude all 52-edge
graphs or replace the other parts of the lower-bound proof.

## The complete family being excluded

There are 25 labeled vertices, numbered 0 through 24. Vertices 0, 1, 2, 3
have degree five, and all other vertices have degree four. Thus every
completion has exactly 52 edges. The four high-degree neighborhoods are
fully specified:

| Vertex | Its complete neighborhood |
| ---: | --- |
| 0 | 2, 3, 4, 6, 7 |
| 1 | 3, 5, 8, 9, 10 |
| 2 | 0, 3, 4, 11, 12 |
| 3 | 0, 1, 2, 5, 13 |

All remaining edges between the degree-four vertices are arbitrary, subject
to their prescribed degrees. The [machine-readable root](sources/eleven-profile20.txt)
records these same neighborhoods. No minimal-counterexample restrictions
on triangles, common neighbors, connectivity, or cubic-neighbor counts are
assumed.

## Proof

Suppose a completion $G$ has treewidth at least eleven.

Delete vertices 0 and 2. They are adjacent and each has degree five, so
exactly nine edges disappear. The resulting graph has 43 edges and treewidth
at least nine, since deleting two vertices lowers treewidth by at most two.

Vertex 4 now has degree two. Eliminate it: remove it and join its two
neighbors if necessary. This removes two edges and adds at most one,
leaving at most 42 edges. Its degree is less than nine, so this operation
preserves the lower bound of nine on treewidth.

Vertex 3 was not adjacent to 4, so that elimination does not change its
degree. Its remaining neighbors are exactly 1, 5, and 13. The edge $1-5$ already exists. Eliminating vertex 3 therefore removes three edges
and adds at most two, leaving **at most 41 edges**. Again, its degree is
less than nine, so the resulting graph still has treewidth at least nine.

This contradicts the earlier theorem that
[treewidth at least nine requires at least 42 edges](proof-nine.md).
Therefore every completion of this profile has treewidth at most ten.

| Operation | Remaining vertices | Edge upper bound | Treewidth lower bound |
| --- | ---: | ---: | ---: |
| Start | 25 | 52 | 11 |
| Delete 0 | 24 | 47 | 10 |
| Delete 2 | 23 | 43 | 9 |
| Eliminate 4 | 22 | 42 | 9 |
| Eliminate 3 | 21 | 41 | 9 |

The elimination fact used here follows from
$\operatorname{tw}(G)\le\max(\deg(v),\operatorname{tw}(G_v))$, where $G_v$
is the graph after eliminating $v$. A decomposition of $G_v$ has a bag
containing the filled clique $N(v)$; attach the bag $N(v)\cup\{v\}$ to it.

## Independent certificate checking

Run:

```sh
python3 scripts/verify_profile_refutation.py \
  sources/eleven-profile20-refutation.json \
  --prefix sources/eleven-profile20.txt
```

Only the standard-library
[verifier](scripts/verify_profile_refutation.py) and the
[certificate](sources/eleven-profile20-refutation.json) are required.
The optional `--prefix` pins the claim to the separate root file.
The verifier starts with every completion of that profile, assumes its
treewidth is at least eleven, checks the four operations, and derives
the contradiction. It does not trust claimed intermediate bounds in the
certificate: those bounds are recomputed.

The sole external numerical premise is **$f(9)\ge42$**. The checker fixes
this premise in its source and states it in its output. Thus independence
means independence from this profile's search implementation and records;
it does not mean the earlier treewidth-nine theorem has been reproved.

### Checking incomplete neighborhoods

For each vertex $u$, the checker maintains certain neighbors $A_u$, possible
neighbors $B_u$, and degree bounds $L_u\le\deg(u)\le U_u$. It also maintains
an edge upper bound $E$ and a treewidth lower bound $k$.

Deletion of $v$ lowers $k$ by one and decreases $E$ by at least $L_v$.
Neighbor degree bounds are updated according to whether adjacency to $v$
is certain, optional, or impossible.

Elimination requires $U_v<k$. If $t$ edges are already certain within
$A_v$, its edge-count change is at most

$$
\max_{L_v\le d\le U_v}\left(\binom d2-d-t\right).
$$

Certain neighbors are filled into a clique, as are possible neighbors in
the possible graph. The degree upper bounds use the same elementary
[uniform fill bound](#the-uniform-degree-bound)
as the earlier completion-cover checker. Each possible neighbor can lose
at most one incident edge, giving the new degree lower bound; certain
new edges can further improve that lower bound. Saturated degree upper
bounds remove impossible optional edges.

These operations preserve every actual completion in the interval family.
The tests check all 4,096 triples $A\subseteq G\subseteq B$ on four vertices,
with both exact and interval degree information, every deleted or eliminated
vertex, and both operations: **65,536 invariant checks**. They also reject
incomplete traces, repeated vertices, malformed roots, and wrong root
identities.

## The uniform degree bound

Maintain sets $A_u\subseteq N(u)\subseteq B_u$ of certain and permitted
neighbors, and an upper bound $d(u)\le D_u$. Initially these follow directly
from the supplied prefix and the degree profile: an $n$-vertex, 52-edge
minimum-order counterexample has $104-4n$ vertices of degree five and the
others of degree four.

Before eliminating a vertex, tighten $D_u$ to $|B_u|$ when necessary. If
$D_u=|A_u|$, remove all optional neighbors of $u$ from the permitted sets.
Repeat to stability. These operations retain every compatible graph.

For a proposed next vertex $v$, require $D_v\le10$. If $u\in B_v$ is
actually adjacent to $v$, eliminating $v$ removes one edge at $u$ and
adds at most

$$
a_u=\min\bigl(|B_v\setminus(A_u\cup\{u\})|,
              D_v-1-|A_v\cap A_u|\bigr)
$$

new edges there. The first bound counts permitted missing neighbors; the
second subtracts the certain common neighbors from the available degree.
Thus set

$$
D'_u=\begin{cases}
D_u-1+a_u,&u\in A_v,\\
\max(D_u,D_u-1+a_u),&u\in B_v\setminus A_v.
\end{cases}
$$

The second case includes the possibility that $uv$ was absent. Fill a clique
on $A_v$ in the certain graph and on $B_v$ in the permitted graph, then remove
$v$. These inclusions and bounds remain valid for every completion.
Induction along the supplied order proves the universal width-ten bound.

