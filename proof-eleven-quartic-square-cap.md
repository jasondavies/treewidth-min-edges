# At most four squares through a quartic vertex

**Lemma.** Let $G$ be a finite simple four-regular graph on 26 vertices,
with no triangles and treewidth at least eleven. Every pair of vertices
has at most two common neighbors, and every vertex lies in at most four
four-cycles.

This hand proof uses only the earlier bounds $f(9)\ge42$ and $f(10)\ge47$.
It needs no graph classification or computer certificate. The separate
[quartic triangle exclusion](proof-eleven-triangle-certificates.md)
supplies the triangle-free hypothesis in the minimum-counterexample argument.

## Two elementary facts

Eliminating a vertex means completing its neighborhood to a clique and
removing it. Eliminating a vertex of degree $d<k$ preserves a treewidth
lower bound of $k$: otherwise attach the removed vertex and its neighbors
as a bag to a width-$(k-1)$ decomposition of the result. If its neighborhood
already has $t$ edges, the edge count changes by exactly

\[
\binom d2-d-t.
\]

Also, every graph $H$ with treewidth at least ten and $m$ edges satisfies

\[
m\ge47,\qquad \deg_H(u)\le m-42\quad\text{for every vertex }u.\tag{1}
\]

The second inequality follows by deleting $u$ and applying $f(9)\ge42$.

## Common neighbors and root normalization

Suppose nonadjacent vertices $x,y$ have $r\ge3$ common neighbors. Deleting
$x,y$ leaves 44 edges and treewidth at least nine. Their common neighbors
are independent, by triangle-freeness, and now have degree two. Suppressing
all $r$ preserves the treewidth lower bound and loses at least $r$ edges,
leaving at most 41 edges, contrary to $f(9)\ge42$. Coincident replacement
edges only reduce the count further. Adjacent vertices have no common
neighbor, so every pair has at most two common neighbors.

Fix a root $v$ and name its four independent neighbors $1,2,3,4$. Every
other vertex meets at most two of them, and each pair $i,j$ has at most
one common neighbor besides $v$. Thus the four-cycles through $v$
correspond to the edges of a simple graph $J$ on $\{1,2,3,4\}$. Write
$x_{ij}$ for the additional common neighbor associated with edge $ij$.
All these vertices are distinct: a coincidence would meet at least
three root neighbors.

There are at most six such cycles. If there are six, the shared vertices
complete all four neighbor degrees. If there are five, relabel the missing
pair as $34$. Vertices $3,4$ each have one further neighbor, denoted
$p_3,p_4$. These are distinct from every $x_{ij}$, since a coincidence
would meet three root neighbors. They are distinct from each other,
since otherwise $J$ would also contain $34$. Simplicity and triangle-freeness
exclude coincidences with $v,1,2,3,4$. This accounts for every possible
identification in the two cases.

## Six incident squares

Delete $x_{12}$, leaving 48 edges and treewidth at least ten. Eliminate
$1,2,3,4$, then $v$. The exact current neighborhoods and guaranteed
internal edge counts are:

| Vertex | Current neighbors | Internal edges at least | Edge change at most |
| --- | --- | ---: | ---: |
| $1$ | $v,x_{13},x_{14}$ | 0 | 0 |
| $2$ | $v,x_{23},x_{24}$ | 0 | 0 |
| $3$ | $v,x_{13},x_{23},x_{34}$ | 2 | 0 |
| $4$ | $v,x_{14},x_{24},x_{34}$ | 3 | $-1$ |
| $v$ | $x_{13},x_{14},x_{23},x_{24},x_{34}$ | 8 | $-3$ |

For vertices $3,4$, the internal edges include the edges from $v$ to
the listed shared neighbors, filled by preceding eliminations. Before
eliminating $v$, its neighborhood contains the two edges
$x_{13}x_{14},x_{23}x_{24}$ and all three pairs within each of
$\{x_{13},x_{23},x_{34}\}$ and $\{x_{14},x_{24},x_{34}\}$: eight distinct
edges altogether.

All eliminated degrees are at most five, so treewidth remains at least
ten. The result has at most $48-1-3=44$ edges, contradicting $f(10)\ge47$.

## Five incident squares

Delete $x_{13}$, leaving 48 edges and treewidth at least ten. Eliminate
$1,3,2,4$ in that order:

| Vertex | Current neighbors | Internal edges at least | Edge change at most |
| --- | --- | ---: | ---: |
| $1$ | $v,x_{12},x_{14}$ | 0 | 0 |
| $3$ | $v,x_{23},p_3$ | 0 | 0 |
| $2$ | $v,x_{12},x_{23},x_{24}$ | 2 | 0 |
| $4$ | $v,x_{14},x_{24},p_4$ | 2 | 0 |

The resulting graph $H_0$ has at most 48 edges and treewidth at least ten.
By (1), its maximum degree is at most six. The root now has exactly the
six neighbors

\[
S=\{x_{12},x_{14},x_{23},x_{24},p_3,p_4\}.
\]

Its neighborhood has at least eight edges: $x_{12}x_{14}$, $x_{23}p_3$,
and all three pairs within each of $\{x_{12},x_{23},x_{24}\}$ and
$\{x_{14},x_{24},p_4\}$.

Eliminate $v$. This changes the edge count by at most
$\binom62-6-8=1$. The resulting graph $H$ has 20 vertices, $m\le49$ edges,
and treewidth at least ten.

Only the six vertices in $S$ can have gained fill edges; the other fourteen
have degree at most four. Moreover, $x_{24}$ was already adjacent to four
of the other five vertices of $S$. Eliminating $v$ removes one incident
edge and adds at most one, so $\deg_H(x_{24})\le6$. Apply (1) to the other
five vertices of $S$ and sum degrees:

\[
2m\le14\cdot4+6+5(m-42)=5m-148.
\]

Thus $3m\ge148$, forcing the integer $m\ge50$, contrary to $m\le49$.
This excludes the five-square case and proves the lemma.

The cases with one to four four-cycles through a vertex remain outside
this reduction. A subsequent [square-direction argument](proof-eleven-quartic-square-directions.md)
and a 156-byte certificate exclude the four-square case using the
additional marked-residue theorem. Five rooted types with one to three
squares still require exclusions.
