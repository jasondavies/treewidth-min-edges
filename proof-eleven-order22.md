# No minimum-order 52-edge counterexample has 22 vertices

This is a hand reduction using the already established threshold results
f(9)=42, f(10)=47, and f(11)≥52. It does not use the incomplete direct
22-vertex enumeration.

Suppose a graph of treewidth at least eleven with 52 edges exists, and
choose one, G, of minimum order. Low-degree elimination and vertex deletion
give 4≤deg(v)≤5. Write L for the degree-four vertices and H for the
degree-five vertices. If |V(G)|=22, the degree sum gives |L|=6 and |H|=16.

## Local restrictions

For any vertex v, let t be the number of edges among its neighbors.
Eliminating v changes the edge count by binom(deg(v),2)−deg(v)−t and
preserves the lower bound on treewidth, because deg(v)<11. Therefore each
vertex of L belongs to at most one triangle: two would produce a smaller
52-edge counterexample, and three or more would contradict f(11)≥52.

**The neighbors in H of any vertex in L form a clique.** Otherwise delete
two nonadjacent such neighbors. They have degree five, so the resulting
graph has 42 edges and treewidth at least nine. Their common degree-four
neighbor now has degree two; eliminating it leaves at most 41 edges and
still treewidth at least nine, contradicting f(9)=42.

Consequently every vertex in L has at most two neighbors in H: three would
form a triangle in its neighborhood, giving at least three triangles
through that degree-four vertex.

**If a vertex in L has two neighbors in H, each of those neighbors has at
least two neighbors in L.** To prove this, suppose v∈H has just one
neighbor u∈L and is adjacent to another H-neighbor a of u. Let b,c,d be the
other three neighbors of v, all in H. If two of b,c,d were nonadjacent,
deleting them would leave a 42-edge graph in which v is cubic and its
neighborhood contains the edge ua. Eliminating v would then lose at least
one edge, again contradicting f(9)=42. Hence b,c,d form a triangle.
If a were nonadjacent to b, deleting a,b gives the same contradiction,
using the edge cd among v's remaining neighbors. Similarly a is adjacent
to c and d. Thus the four H-neighbors of v form K4. Eliminating v now
loses at least one edge (there are at least six edges in its neighborhood),
contradicting f(11)≥52. This proves the assertion.

## The boundary has at most six vertices

Let D=N_G(L)∩H. In the bipartite graph of edges between L and D, every
L-vertex has degree at most two. A D-vertex of degree one can only be
adjacent to an L-vertex of degree one, by the preceding assertion.
Remove all these degree-one D-vertices together with their distinct
L-neighbors. All remaining D-vertices have degree at least two, while
remaining L-vertices still have degree at most two. Counting edges gives
at most as many remaining D-vertices as remaining L-vertices. Hence

    |D| ≤ |L| = 6.

Also e(G[L])≤9. If G[L] is triangle-free, this is Mantel's bound on six
vertices. Otherwise take a triangle T. Each of the three other vertices
has at most one neighbor in T, since two would give a vertex of T a second
triangle. Thus there are at most 3+3+3=9 edges in G[L].

## Replace L by its boundary clique

Write l=e(G[L]). Deleting L removes 24−l edges, so G[H] has 28+l edges.
Let H' be G[H] with D made a clique. Then

    |E(H')| ≤ 28+l+binom(|D|,2) ≤ 28+9+15 = 52.

The graph H' has only sixteen vertices. Let J be G[L∪D], also with D made
a clique. It has at most twelve vertices and treewidth at most ten: this
is immediate with at most eleven vertices; with twelve, it is not complete
(each L-vertex still has degree four). Any noncomplete twelve-vertex graph
has a width-ten decomposition consisting of the two bags that omit,
respectively, the endpoints of a nonedge.

The graph obtained from G by completing D is the clique-sum of H' and J.
Glue their decompositions at bags containing D. Therefore

    tw(G) ≤ max(tw(H'),tw(J)).

Since tw(G)≥11 and tw(J)≤10, H' has treewidth at least eleven. If H' has
fewer than 52 edges this contradicts the lower bound; otherwise its smaller
order contradicts the choice of G. Thus order 22 is impossible.

