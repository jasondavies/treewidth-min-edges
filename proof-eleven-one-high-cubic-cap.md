# Cubic-neighbor cap beside a unique degree-five vertex

**Theorem.** Let H be a simple graph with 23 vertices and 42 edges, with
nine vertices of degree three, thirteen of degree four, and one vertex z
of degree five. Let L be its cubic vertices. If H[L] has maximum degree
at most two and tw(H) is at least nine, every quartic neighbor of z has
at most one neighbor in L.

This uses the earlier complete classifications and the general J20
packing reduction in [the cubic-neighbor proof](proof-eleven-cubic-neighbor-cap.md),
including its [two-K4 finite lemma](proof-eleven-two-k4-incidence.md).
It does not use an archived 52-edge classification or a failed treewidth
search as an exclusion. No isolated-cubic hypothesis is needed.

## Reduction to the same 71 intermediate graphs

Suppose a quartic neighbor w of z has r cubic neighbors. Then r is two
or three. Since f(9)=42, each cubic has an independent neighborhood, and
two cubics have at most one common neighbor: eliminating a cubic with a
triangle, or two cubics sharing two neighbors, would preserve treewidth
at least nine while leaving fewer than 42 edges.

The r cubic neighbors of w are therefore independent. Their other two
neighbors are nonadjacent, these pairs are pairwise disjoint, and they
avoid the other neighbors of w. Delete w, then suppress these r
degree-two vertices. Each suppression adds a new edge; it does not
change the degrees of its endpoints. The resulting J has treewidth at
least eight, 22-r vertices, and 38-r edges.

If r=3, deleting w reduces z to degree four, and no other surviving
vertex changes degree. J has 19 vertices, 35 edges, six cubics and
thirteen quartics. This contradicts the earlier complete 35-edge,
minimum-degree-three classification, whose survivors have at most
18 vertices. There is no disconnected exception: a treewidth-eight
component already needs at least 34 edges, whereas another component
of minimum degree three needs at least six.

If r=2, w's remaining neighbor q besides z is quartic. After deleting w,
z drops from degree five to four and q from four to three. J has
20 vertices, 36 edges, eight cubics and twelve quartics. The general J20
packing argument therefore places it in the same 71 reconstructed
intermediate graphs as the earlier cap theorem. This step does not use
an isolated cubic or the degree sequence of H beyond the calculation above.

## Exhaustive inverse construction and positive checks

For each intermediate J, choose a cubic q and a quartic z. Choose two
vertex-disjoint edges avoiding q and z. Subdivide them with new vertices
and add w adjacent to both subdivision vertices, q and z. This restores
exactly the required degree sequence. Every H in the reduction occurs:
the two suppressed edges are distinct, disjoint and avoid q,z by the
cubic restrictions already proved.

For 66 intermediate graphs the checker finds and verifies a width-seven
order of J and a width-eight order of its universal-apex extension. Every
inverse lift has width at most eight: first eliminate the two inserted
cubics, after which the remaining graph is a subgraph of J plus a
universal apex. These positive orders cover all lifts of those 66 graphs.

For the five other intermediates, the checker enumerates all inverse
choices, keeping only H[L] maximum degree at most two, independent cubic
neighborhoods and cubic-pair codegree at most one. It checks an explicit
width-eight elimination order of each remaining graph, independently of
the order proposer.

The complete portable run checks 162,680 inverse choices, of which 47,400
fail the cubic degree condition. All 115,280 remaining targets have
verified width-eight orders. Each fallback intermediate contributes
23,056 targets. The target-stream SHA256 is

```text
19867337c3e41dd5f5fafe024f6040bf5e4470e07498c11d3792a82ed2025ece
```

Reproduce using the source-only checker:

```sh
python3 -O scripts/verify_one_high_cubic_cap.py --native
```

The recorded full portable replay took 20.16 seconds on one CPU. It
regenerates the 71 intermediates from the earlier catalogue; no stored
list of the five fallbacks or saved positive-order status is trusted.
A missing order aborts the check.

## Explicit application to order-25 families

Start with the minimum-order 52-edge counterexample profile with four
high vertices of degree five and twenty-one lows of degree four, with
all high neighborhoods exact. Delete a nonadjacent pair of highs. Apply
this rule only when the exact residual degrees are nine threes, thirteen
fours and one five. The unique residual degree-five vertex is an original
high and hence its whole neighborhood is exact.

As in the [no-isolate projection](proof-eleven-cubic-neighbor-cap-extension.md),
each low cubic belongs to one deleted-parent group. A private low has at
most one neighbor in each group. A low with a remaining high parent
already uses its one-triangle allowance on its two high parents, so it
has no same-group neighbor, at most one other-group neighbor, and at most
one remaining high neighbor. Thus its cubic degree is at most two.
The checker also requires this bound on every residual cubic that was
originally high, whose neighborhood is exact. These checks establish
H[L] maximum degree at most two.

The theorem applies only to residual quartics adjacent to the unique
high. Two known cubic incidences refute the family. One known incidence
forbids every other possible cubic incidence at that quartic.

The explicit JSON node is `['u']` for a contradiction and `['u', child]`
for a nonempty projection. Binary opcodes 23 and 22 encode these nodes
in `52-edge-branch-refutation-v10`. The checker recomputes the conditions,
projects on copies, and retains the original normalized parent for
postorder references. Older `Bounds`, normalization, numerical traces,
programs and explicit projections keep their previous meanings.
Version names are parsed as canonical integers, so version 10 cannot be
misread as version zero. Opcodes 20 and 21 remain reserved for a separate quartic-square rule.

The supplied `000001.bin.xz` excludes the single-edge high profile. Its
2,852-node proof was generated in 0.373 seconds and independently replayed;
it occupies 2,956 compressed bytes. It contains 331 one-high projections
and 42 one-high terminal contradictions. This is a profile certificate,
not by itself a complete order-25 exclusion.
