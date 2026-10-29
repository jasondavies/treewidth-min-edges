# Two further order-24 exclusions using the earlier 29-edge classification

This reduction uses an additional classification premise, beyond the
numerical minima used by ordinary branch certificates and beyond the
28-edge premise used by `verify_order24_smoothing.py`:

> There is no connected graph on 16 vertices, with 29 edges, minimum
> degree at least three, and treewidth at least seven.

This is already proved in [proof-nine.md, Small residue classifications](proof-nine.md#small-residue-classifications).
The proof reconstructs all minimum-degree-three 29-edge graphs of
treewidth at least seven through order 15 from the 124 surviving
minimum-degree-four cores and inverse moves from $K_8$ and $F$. There are
280 graphs through order 15. The seven order-15 graphs have only two
distinct legal triangle-to-star extensions, and both have width-six
orders. The relevant complete reconstruction is
[`classify_treewidth34.py`](scripts/nine/classify_treewidth34.py), followed
by the order-16 check in
[`classify_treewidth35.py`](scripts/nine/classify_treewidth35.py).
The more restricted reconstruction in `extend29.py` alone does not prove
this premise, because it restricts the number of cubic vertices.

This premise retains the earlier enumeration dependency: the 29-edge
core enumeration in [proof.md, Section 8](proof.md#8-classification-at-34-edges-exactly-two-connected-graphs)
checks 518,071,774 cores and retains 124. Its runtime is substantial;
checking the small recipes below does not reproduce that enumeration or
prove the completeness of the saved 280-graph family. The repository's
full `reproduce_nine.py --full` workflow regenerates the prerequisites and
the subsequent closure; see [its reproduction instructions](proof-nine.md#reproduction).
No new large enumeration is needed for this order-24 reduction once the
earlier classification is accepted.

The disconnected and smaller-edge cases follow from existing facts.
Any component of treewidth at least seven needs at least 28 edges.
Any other component of a graph of minimum degree at least three needs
at least six edges. Thus a graph of minimum degree at least three,
at most 29 edges, and treewidth at least seven is connected. If it has
at most 28 edges, the earlier classification makes it $K_8$ or the
12-vertex graph $F$, so it cannot have 16 vertices. Consequently the
stated premise excludes all graphs on 16 vertices with minimum degree
at least three, at most 29 edges, and treewidth at least seven.

In the order-24 counterexample profiles, the eight high vertices have
degree five, and the sixteen low vertices have degree four. For profiles
202 and 203, every low has exactly one high neighbor. Hence the induced
low graph has minimum degree three.

For either profile, delete the independent high vertices $1,4,5,7$.
This removes exactly 20 edges and leaves treewidth at least seven.
Eliminate the remaining high vertices in order $0,2,3,6$. Their current
degrees are $3,2,2,1$, respectively, so each elimination preserves the
treewidth-seven lower bound. Charging all missing fill edges as new
gives the following edge upper bounds:

| Step | Initial deletions | Eliminate 0 | Eliminate 2 | Eliminate 3 | Eliminate 6 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Edges at most | 32 | 32 | 31 | 30 | 29 |

All sixteen lows remain, and no original edge between two lows was
removed. The result therefore has minimum degree at least three and
at most 29 edges, contradicting the classification above.

The computation only involves high-vertex neighborhoods, which the
catalogue fixes completely. Unknown original edges between lows cannot
affect the degree of an eliminated high. They can make a charged fill
edge already present, which only decreases the actual edge count.

The separate checker uses the format `order24-high-smoothing29-v1`.
It checks arbitrary supplied recipes with safe eliminated degree below
seven and an induced-low minimum-degree bound of three. It does not
change the earlier 28-edge checker or ordinary branch-certificate rules.
An exploratory scan of all 364 catalogue profiles found 20 recipes.
The supplied certificate and the builder's default selection contain
only profiles 202 and 203, the two additions to the previously covered
families. The other 18 already have separate proofs.

```sh
python3 scripts/verify_order24_smoothing29.py
```

The first command verifies catalogue coverage afresh, then checks the
reductions relative to the explicitly stated classification premise.
It does not claim that other order-24 families have been excluded.

The broader question about nonisolated vertices also has an affirmative
answer conditional on the same classification: a graph with at most
29 edges and treewidth at least seven has at most 15 nonisolated
vertices. In a connected 29-edge graph, deleting a degree-one vertex or
suppressing a degree-two vertex leads to the 28-edge classification
(or to an impossible smaller edge count), leaving at most 13 original
vertices. If minimum degree is at least three and order exceeds 16,
repeated cubic eliminations preserve this minimum degree until order
16: a neighborhood with two or more edges would leave fewer than 28
edges, while a one-edge loss would already force $K_8$ or $F$. An
all-degree-at-least-four graph has at most 14 vertices. Thus a larger
graph would yield an excluded order-16 graph. Finally, a disconnected
graph has one component with at least 28 edges and at most one other
edge; if that other edge exists, the large component is $K_8$ or $F$,
giving at most 14 nonisolated vertices. This broader consequence is not
needed by the recipe checker.
