# Three more order-24 exclusions from the 28-edge classification

This is an additional, explicitly conditional reduction. It uses the
classification in [proof.md, Section 4](proof.md#4-graphs-with-at-most-28-edges-and-treewidth-at-least-seven):
every connected graph with at most 28 edges and treewidth at least seven
is either $K_8$ or the specified 12-vertex graph $F$. Both have exactly
28 edges. The classification is a stronger premise than the numerical
minimum $f(7)=28$; the ordinary branch-certificate checker does not use it.

The independently checked order-24 catalogue describes every possible
minimum-order 52-edge counterexample on 24 vertices by its eight
degree-five high vertices, the graph they induce, and all their incidences
with the sixteen degree-four low vertices. Each low vertex has at most
two high neighbors. Consequently its degree in the induced low graph
is at least two.

Choose four independent high vertices and delete them. Exactly 20 edges
are removed, and treewidth remains at least $11-4=7$. Next eliminate the
other four high vertices, in an order in which each has degree at most
two. Eliminating a degree-one vertex removes one edge. Eliminating a
degree-two vertex removes its two incident edges and adds at most one
edge between its neighbors. These eliminations preserve treewidth at
least seven. Their complete neighborhoods are determined by the profile
and earlier fill edges; unknown edges between low vertices can only
decrease the edge total compared with charging every missing fill edge.

For the three previously uncertified catalogue profiles below, the result
has at most 28 edges:

| Catalogue index | Delete these highs | Eliminate these highs |
| ---: | --- | --- |
| 2 | 0, 1, 2, 3 | 4, 5, 6, 7 |
| 94 | 0, 5, 6, 7 | 1, 2, 3, 4 |
| 188 | 0, 1, 2, 6 | 3, 4, 5, 7 |

In the first two rows all four eliminated highs have degree two; in the
last row their degrees are two, two, two, and one. In each case the upper
bounds on the successive edge totals are 32, 31, 30, 29, and 28.

All sixteen low vertices remain nonisolated: none of their original
edges to other low vertices was removed. A component with treewidth at
least seven would, by the classification, be $K_8$ or $F$ and use all
28 available edges. It would leave every other vertex isolated. This is
impossible with sixteen nonisolated vertices, because $K_8$ and $F$ have
only eight and twelve vertices. This excludes the three profiles.

The recipe checker validates the same argument for any catalogue index;
it has no list of exceptional indices. A scan of all 364 profiles finds
13 qualifying recipes, including these three. The other ten already have
ordinary branch proofs totaling only 532 uncompressed bytes, so removing
them would give no meaningful space saving.

```sh
python3 scripts/verify_order24_smoothing.py
```

The first command verifies catalogue coverage afresh before checking the
recipes. It certifies only the named reductions relative to the stated
classification premise; it does not certify the remaining order-24
families or other vertex counts.
