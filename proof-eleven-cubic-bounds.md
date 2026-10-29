# Cubic restrictions at a proved global edge minimum

Suppose the current interval represents graphs H with treewidth at least
k >= 4 and at most M=f(k) edges, where f(k) is a previously proved edge
lower bound. Any actual H must therefore have exactly M edges. A cubic
vertex has independent neighbors, since eliminating it otherwise loses an
edge while preserving treewidth at least k.

Let C consist of vertices whose current degree interval is exactly [3,3].
These are guaranteed cubics, not merely vertices with three known neighbors.

1. Any two vertices x,y in C have at most one common neighbor. If adjacent,
   a common neighbor already violates the independence of their
   neighborhoods. If nonadjacent with two common neighbors, eliminating x
   creates an edge between the common neighbors and leaves y cubic.
   Eliminating y then loses an edge, contradicting M=f(k). Consequently,
   two known common neighbors reject a family. Once one common neighbor
   is known, forbid each unknown second-common-neighbor edge.

2. For any vertex v, let t be its actual number of neighbors in C. Those
   t cubics are independent (otherwise a cubic neighborhood contains an
   edge). Their other neighbor pairs are disjoint by rule 1, and each pair
   is nonadjacent by cubic neighborhood independence. Delete v, then
   eliminate its t cubic neighbors, now of degree two. These eliminations
   do not interact and each loses one edge. The resulting graph has at
   most M-deg(v)-t edges and treewidth at least k-1. Hence

       deg(v)+t <= M-f(k-1) = c.

   With t0 known neighbors in C, this tightens the degree upper bound to
   c-t0. If a degree lower bound L(v) satisfies L(v)+t0=c, every other
   possible edge from v to C is forbidden. If it exceeds c, reject.

3. Every vertex in C has degree three, so exactly 3|C| directed incidences
   run from all vertices to C. The number incident with v is at most

       b(v)=min(c-L(v), |P(v) intersect C|).

   If sum b(v)<3|C|, reject. If equality holds, every capacity is attained;
   whenever b(v)=|P(v) intersect C|, all those possible edges are forced.
   This is a necessary incidence count, not an assumption about an
   unassigned edge.

The same rules remain valid with an independently proved order-dependent
lower bound f(k-1,n-t-1) in place of f(k-1), but the supplied patch uses only
the global bound c=M-f(k-1), avoiding any circular dependence on order bounds.

The trigger must remain equality with a proved GLOBAL minimum, not equality
with an order-dependent bound. The initial 52-edge lower bound for k=11 is
available from the previously proved f(10)>=47 and the parity/minimum-order
argument, independently of the desired 52-edge exclusion.

These rules are implemented in `Bounds.tighten` in
[verify_branch_refutation.py](scripts/verify_branch_refutation.py). They only
strengthen terminal reductions; they do not change the catalogue or branch
choices. Existing traces can close earlier under the stronger bounds.

## Deleting a cubic neighbor without an exact-minimum assumption

There is also a useful inequality away from a global edge minimum. Let
$H$ have treewidth at least $k\ge4$, at most $E$ edges and $n$ vertices.
Choose a vertex $v$ and a set $S$ of its degree-three neighbors. Then

\[
\deg_H(v)+|S|+f(k-1,n-1-|S|)\le E,
\]

where $f(k-1,r)$ is any independently established edge lower bound for
$r$-vertex graphs of treewidth at least $k-1$.

To prove this, delete $v$. Every vertex of $S$ now has degree two. Its
induced components are paths or cycles. Suppressing a path of $t$ such
vertices removes its $t-1$ internal edges and two boundary edges, and
adds at most one edge: at least $t$ edges disappear. A cycle component
has no outside neighbors, so removing its $t$ vertices removes $t$ edges.
The resulting graph therefore has at most $E-\deg_H(v)-|S|$ edges.
Deleting $v$ lowers treewidth by at most one; degree-at-most-two
eliminations preserve treewidth when it is at least three. This proves
the inequality. The argument does not require the cubic vertices to be
independent.

The C proposer uses this inequality only to select promising explicit
traces: delete $v$, then eliminate the selected cubic neighbors. The
independent checker applies its existing interval operations to every
step and must reach an existing contradiction. No new numerical premise
or proof opcode is needed. For a single cubic whose other two neighbors
are already adjacent, the proposer also recognizes the extra edge lost
by its suppression.
