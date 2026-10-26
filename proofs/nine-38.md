# Treewidth nine requires at least 39 edges

This is a computer-assisted consequence of the existing treewidth-eight
work, with only a one-graph enumeration as an additional computational
dependency. It replaces the proposed search through 32,670,330 graphs.

All graphs are finite, simple, and undirected. We use two established local
results from the [base classification](../proof.md):

1. Every graph of treewidth at least eight has at least 34 edges.
2. Every connected graph with at most 28 edges and treewidth at least seven
   is K8 or the 12-vertex graph F, both having exactly 28 edges.

The second result depends on the earlier 96,841,893-core classification.
The argument here does not replace that earlier computation.

## Reduction to a quartic graph on 19 vertices

Suppose a graph with at most 38 edges and treewidth at least nine exists.
Choose such a graph G with the fewest vertices. It is connected.

Eliminating a vertex means making its neighborhood a clique and removing
the vertex. If the vertex has degree d, then

    tw(G) <= max(d, tw(G after elimination)).

Indeed, a tree decomposition of the eliminated graph has a bag containing
the new neighborhood clique, to which one can attach a bag containing that
clique and the removed vertex. For d <= 3, elimination also does not
increase the number of edges. Minimality therefore gives minimum degree
at least four.

For every vertex v, tw(G-v) >= 8. Thus G-v has at least 34 edges, giving

    4 <= deg(v) <= |E(G)| - 34 <= 4.

Consequently G is 4-regular, with exactly 38 edges and 19 vertices.

## No triangles

Suppose u,a,b form a triangle. Choose a neighbor v of u outside that
triangle; such a neighbor exists because u has degree four.

The graph G-v has 34 edges and treewidth at least eight. In G-v, u has
degree three, and two of its remaining neighbors a,b are adjacent.
Eliminating u therefore removes three edges and adds at most two. The
result has at most 33 edges and still has treewidth at least eight,
contradicting result 1.

Thus G is triangle-free.

## No 4-cycles

Suppose v and x are opposite vertices of a 4-cycle, and let r >= 2 be
their number of common neighbors. They are nonadjacent because G is
triangle-free. Deleting v and x removes exactly eight edges, leaving a
graph J with 17 vertices, 30 edges, and treewidth at least seven.

The r common neighbors now have degree two and are mutually nonadjacent.
Eliminate all of them. Each remains degree two until its elimination,
because no elimination adds edges incident to another common neighbor.
Each elimination removes two edges and adds at most one, preserving
treewidth at least seven. The resulting graph L therefore has at most
30-r edges.

If r >= 3, L has at most 27 edges, contradicting result 2 applied to a
component of maximum treewidth.

If r=2, L has at most 28 edges. In fact it must have exactly 28, by the
same result. Consequently both eliminations added a new edge between the
two neighbors of the eliminated vertex. These operations leave the degrees
of surviving vertices unchanged. Every vertex surviving in L was adjacent
to at most one of v,x (the two common neighbors were eliminated), so its
degree in J, and hence in L, is at least three.

Thus L has 15 vertices, exactly 28 edges, minimum degree at least three,
and treewidth at least seven. A component of treewidth at least seven must,
by result 2, be K8 or F and use all 28 edges. All other components would
then be isolated vertices, impossible because the minimum degree is at
least three. Thus L is K8 or F. But those graphs have eight or twelve
vertices, whereas L has fifteen. This contradiction excludes 4-cycles.

## The remaining girth-five case

We have reduced a counterexample to a connected 4-regular graph on 19
vertices with girth at least five. There is exactly one such graph up to
isomorphism, the Robertson graph. Its width-eight elimination order rules
it out.

This last finite assertion is reproduced directly, without downloading a
graph archive, by:

```sh
python scripts/nine/check_treewidth_nine_girth5.py
```

The script compiles geng and runs

```sh
geng -c -t -f -d4 -D4 19 38:38
```

This produces one graph (about 0.35 CPU seconds in the initial local run):

```text
R???C@_E?KI_I`bGCi?f?ocAoGAQO?
```

For this labeling, the order 0,1,...,18 has elimination width eight.
The script verifies that order independently with Python sets. Source
fingerprints, generation output, and the order are saved in
the fresh report written to `sources/nine/treewidth-nine-girth5.json`.

The count agrees with the [published regular graph table](https://www.mathe2.uni-bayreuth.de/markus/reggraphs.html),
but the reproduction does not rely on that table for completeness.

Therefore no graph with at most 38 edges has treewidth at least nine:

    f(9) >= 39.
