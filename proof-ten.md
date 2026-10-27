# Treewidth ten requires exactly 47 edges

**Result (2026-10-27):** for finite simple undirected graphs,

\[
\boxed{f(10)=47,}
\]

where $f(k)$ is the minimum number of edges at treewidth $k$. This is a
completed local computer-assisted proof, using the earlier result $f(9)=42$
and the saved 34-, 35-, and 36-edge classifications. External review and
novelty assessment remain pending.

The useful shortcut is that **we need not classify all 42-edge graphs of
treewidth nine**. A 47-edge witness exists. To prove its optimality, only
the very restricted 46-edge case remains, and that case reduces directly
to families already classified for the treewidth-nine proof.

## 1. Reduce the lower bound to a quartic graph on 23 vertices

Suppose a graph with at most 46 edges has treewidth at least ten. Choose
one with the fewest vertices. It is connected, since one component has
the same treewidth as the whole graph.

Eliminating a vertex $v$ means completing its neighborhood to a clique and
then removing it. If $H$ is the resulting graph,

\[
\operatorname{tw}(G)\le\max(\deg(v),\operatorname{tw}(H)).
\]

Eliminating a vertex of degree at most three never increases the number
of edges. It would produce a smaller counterexample, so $G$ has minimum
degree at least four.

For every vertex $v$, deleting $v$ leaves treewidth at least nine, and
therefore at least 42 edges by the
[treewidth-nine result](proof-nine.md). Consequently

\[
4\le\deg(v)\le |E(G)|-42\le4.
\]

Thus $G$ is quartic, has exactly 46 edges, and has 23 vertices. This already
excludes every graph with fewer than 46 edges.

## 2. The graph is triangle-free

Suppose $u,a,b$ form a triangle. Choose a neighbor $v$ of $u$ other than
$a,b$. Deleting $v$ leaves 42 edges and treewidth at least nine. In that
graph, $u$ has degree three, with two adjacent neighbors. Eliminating $u$
therefore leaves at most 41 edges while preserving treewidth at least
nine, contradicting $f(9)=42$.

## 3. A four-cycle reduces to existing small families

Suppose $G$ contains a four-cycle. Choose opposite vertices $x,y$, which
are nonadjacent because $G$ is triangle-free. Let $C=N(x)\cap N(y)$ and
$r=|C|$, where $2\le r\le4$.

Deleting $x,y$ leaves 38 edges, 21 vertices, and treewidth at least eight.
The vertices in $C$ are pairwise nonadjacent and now have degree two.
Smooth each of them: delete it and add the edge between its two neighbors
if that edge is not already present. This preserves treewidth at least
eight. No smoothing affects another vertex of $C$.

Write $H$ for the resulting graph. It has $21-r$ vertices. Each successful
smoothing removes one edge overall; a smoothing whose replacement edge
already exists removes two. If there are $t$ such duplicate replacements,

\[
|E(H)|=38-r-t.
\]

### Duplicate replacements are impossible

For a common neighbor $c$, its two other neighbors are not adjacent in
$G$, since that would form a triangle. Neither is adjacent to $x$ or $y$,
again by triangle-freeness. Thus a duplicate replacement can occur only
when two vertices of $C$ have the same pair of other neighbors.

Since $\operatorname{tw}(H)\ge8$ and $f(8)=34$, we have $t\le4-r$.
For $r=4$ this gives $t=0$. For $r=2$ or $3$, the only possible positive
value is $t=1$ (with just two common neighbors, at most one replacement
can duplicate another).

In this one-duplicate case, every surviving vertex has degree at least
three. The endpoints of the duplicated replacement had degree four after
deleting $x,y$ and lose just one degree; all other smoothings preserve
the surviving degrees. Vertices outside $C$ lose at most one incident
edge when $x,y$ are deleted.

* If $r=2,t=1$, then $H$ has 35 edges, 19 vertices, and minimum degree
  three. The complete [35-edge classification](sources/nine/treewidth35-all-classification.json)
  contains no such graph of treewidth at least eight: its largest order is 18.
* If $r=3,t=1$, then $H$ has 34 edges and 18 vertices, again of minimum
  degree three. The [34-edge classification](proof.md#8-classification-at-34-edges-exactly-two-connected-graphs)
  has only the two graphs of orders 16 and 17.

Both are contradictions. Hence all replacement edges are distinct and new.

### The remaining residue lists

Successful smoothings preserve every surviving degree. Precisely the
$2(4-r)$ neighbors of $x,y$ outside $C$ now have degree three; all other
vertices of $H$ have degree four. The complete possibilities are:

| Common neighbors $r$ | Edges of $H$ | Vertices | Degree-three vertices | Retained residues |
|---:|---:|---:|---:|---:|
| 2 | 36 | 19 | 4 | 457 |
| 3 | 35 | 18 | 2 | 9 |
| 4 | 34 | 17 | 0 | 1 |

These are subsets of the already completed
[36-edge family](sources/nine/treewidth36-family.g6),
[35-edge family](sources/nine/treewidth35-all-family.g6), and
[34-edge family](sources/nine/treewidth34-family34.g6).
The 36-edge classification covers orders 16–19, maximum degree at most
five, and at most five degree-three vertices, so it includes every residue
in the first row. No new large classification is needed.

Reconstruct $G$ from a residue by choosing $r$ distinct edges to subdivide,
adding $x,y$ adjacent to all subdivision vertices, and splitting the
$2(4-r)$ degree-three vertices equally between $x$ and $y$. Exchanging
$x,y$ gives the same unlabeled graph, so there are three partitions when
$r=2$, one when $r=3$, and none to choose when $r=4$.

The number of constructions is

\[
457\binom{36}{2}\cdot3
+9\binom{35}{3}
+\binom{34}{4}
=863,730+58,905+46,376
=\boxed{969,011}.
\]

Every construction has a verified width-nine elimination order. The C
search checks every positive order using paths in the original graph.
A separate Python implementation rebuilds **every** construction with
sets and independently checks its order by explicit filling.
[Enumeration report](sources/ten/treewidth46-four-cycles.json),
[independent audit](sources/ten/treewidth46-four-cycle-audit.json).

Thus no counterexample can contain a four-cycle.

## 4. The girth-five case

The remaining possibility is a connected quartic graph on 23 vertices
with girth at least five. There are **3,917** such graphs up to isomorphism.
We regenerated the entire family with unmodified GENREG and verified a
width-nine elimination order for each graph, independently in Python.
The count agrees with
[Meringer's regular-graph tables](https://www.mathe2.uni-bayreuth.de/markus/reggraphs.html).

[Generated family](sources/ten/treewidth46-girth5.g6),
[check report](sources/ten/treewidth46-girth5.json).

This excludes the final case. Therefore

\[
\boxed{f(10)\ge47.}
\]

## 5. A 47-edge witness

Take the quartic 23-vertex graph of girth five encoded by

```text
Vs`AA?cG`?A_C_CA@_?S?AA?@`OAgOAT??aG?CW??G`_
```

and add the edge **{1,10}**, using graph6's zero-based vertex labels.
The resulting graph has 47 edges, two vertices of degree five, and 21
vertices of degree four. It is triangle-free, with a four-cycle created
by the added edge. Its graph6 encoding is

```text
Vs`AA?cGb?A_C_CA@_?S?AA?@`OAgOAT??aG?CW??G`_
```

The [certificate](sources/witness47.json.gz) gives a
width-ten order and **410,333** eliminated-vertex sets closed under all
width-nine elimination steps, including the empty set and excluding the
full set. The closure verifier explicitly fills eliminated vertices;
it is separate from the path-based algorithm that generated the states.
This proves treewidth exactly ten, so

\[
\boxed{f(10)=47.}
\]

The witness was found by adding every nonedge to the 3,917 girth-five
quartic graphs: **810,819** augmentations. Three labeled augmentations
failed the width-nine test; the certificate above independently verifies
one of them. No classification or uniqueness claim at 47 edges is made.

## 6. Reproduction

The prerequisites are [the treewidth-nine proof](proof-nine.md), $f(8)=34$,
and the three saved residue families linked above. The new code reuses
`scripts/nine`'s C checker and independent Python reference routines.
It has no dependency on the original research workspace.

Use Python 3.10 or newer, without `-O`, and a C compiler. Multicore checks
use `--workers` (16 below). The driver works in a separate output directory
and leaves the checkout unchanged.

**Verify the saved data and all final certificates:**

```sh
python3 scripts/reproduce_ten.py --output /tmp/treewidth-ten-check --workers 16
```

This verifies the 47-edge witness, independently reconstructs all 969,011
four-cycle cases, and checks the 3,917 saved girth-five graphs. It does
not re-establish the completeness of the saved graph families.

**Regenerate all new treewidth-ten computations:** obtain `gendef.h`,
`genreg.c`, `main.c`, and `optmid.c` from
[GENREG revision 5](https://svn.code.sf.net/p/genreg/code/trunk/), then run:

```sh
python3 scripts/reproduce_ten.py \
  --genreg-source /path/to/genreg \
  --output /tmp/treewidth-ten-new --workers 16
```

This also builds unmodified GENREG and regenerates the complete girth-five
family, comparing the output with the saved list. It still uses the
previously established treewidth-eight/nine classifications.

**Regenerate every prerequisite as well:**

```sh
python3 scripts/reproduce_ten.py --full \
  --genreg-source /path/to/genreg \
  --output /tmp/treewidth-ten-full --workers 16
```

This first invokes the full treewidth-nine pipeline, including its
28/34-edge prerequisites, and uses its freshly regenerated residue lists.
The earlier pipeline also needs nauty and `pkg-config`; see
[its requirements](proof-nine.md#reproduction). Most of the cost is in
these earlier classifications. Their completed stages and partitions are
checkpointed. On restart, the inexpensive new treewidth-ten checks rerun.
Source or option changes require a fresh output directory.

The [drawing script](scripts/draw_witness47.py) uses only Python's standard
library. It checks the graph against the certificate and highlights the
added edge {1,10} in blue:

```sh
python3 scripts/draw_witness47.py
```

For a Python-only check of the witness:

```sh
python3 scripts/ten/verify_treewidth_ten_witness.py
```

To regenerate its closed-state certificate:

```sh
python3 scripts/ten/certify_treewidth_ten_witness.py \
  --input sources/witness47.g6 --output /tmp/tw10-witness
```

The exploratory single-edge witness search is also included. After the
new-computations run above has generated the quartic family:

```sh
cc -O3 scripts/ten/treewidth47_add_edge.c -o /tmp/tw10-add-edge
/tmp/tw10-add-edge < /tmp/treewidth-ten-new/runs/girth23/graphs.g6 \
  > /tmp/tw10-candidates.g6
```

The [saved reports](sources/ten/README.md) record counts and provenance.
The 24-vertex quartic search and its 48-edge witnesses were exploratory;
they are not dependencies of $f(10)=47$.
