# Nine order-24 exclusions through a 20-vertex residue

The small recipe file excludes catalogue roots
3, 13, 29, 32, 33, 209, 243, 298, and 308.
The checker regenerates its candidate residues from the earlier complete
36-edge family, checks fresh width-seven orders where available, and
exhausts the remaining exact-neighborhood embeddings. It stores neither
large branch proofs nor lists of complete 24-vertex graphs.

The additional premise is the general J20 packing reduction proved in
[the cubic-neighbor-cap proof](proof-eleven-cubic-neighbor-cap.md): every
20-vertex, 36-edge graph of degree sequence 3^8,4^12 and treewidth at least
eight occurs among the checked inverse constructions from the earlier
36-edge classification. This reduction uses the earlier full 29-, 34-,
35-, and specified 36-edge classifications, and the
[two-K4 incidence lemma](proof-eleven-two-k4-incidence.md).
None of these dependencies is an archived 52-edge classification.

## The symbolic reduction

The original graph G has 24 vertices, eight of degree five (the high
vertices) and sixteen of degree four (the lows). All high neighborhoods
are fixed by its catalogue root. Suppose tw(G) is at least eleven.

A recipe selects three independent highs S. Their deletion removes
exactly fifteen edges, leaving 21 vertices, 37 edges, and treewidth at
least eight. It also selects a fourth high w whose remaining degree is
two, with neighbors u and v. Suppress w.

Every other vertex's degree after deleting S is known exactly from the
high-incidence root. The checker requires that these twenty degrees are
eight threes and twelve fours, and that both u and v have degree at least
four. If uv was already an edge, suppression would leave a 20-vertex,
35-edge graph with minimum degree at least three and treewidth at least
eight. The earlier full 35-edge classification has no such graph: its
minimum-degree-three survivors have at most eighteen vertices.
Consequently uv must be absent in a hypothetical counterexample.

Suppression therefore inserts uv, preserves every other degree, and gives
J with twenty vertices, thirty-six edges, degree sequence 3^8,4^12, and
treewidth at least eight. Its four surviving original high vertices have
fully specified neighborhoods, including the inserted edge if relevant.
No assumption is made about the unknown low-low edges of G.

The supplied recipes are:

| Catalogue root | Deleted highs | Suppressed high |
|---:|---|---:|
| 3 | 0,1,2 | 7 |
| 13 | 0,3,5 | 1 |
| 29 | 0,1,4 | 5 |
| 32 | 5,6,7 | 2 |
| 33 | 1,5,6 | 4 |
| 209 | 1,3,5 | 0 |
| 243 | 3,4,5 | 2 |
| 298 | 0,1,4 | 2 |
| 308 | 0,3,4 | 2 |

The checker obtains the roots from an independently verified catalogue;
it checks every condition above rather than trusting the recipe table.

## Exhausting the possible residues

The general packing reduction yields 71 raw intermediate candidates J.
The implementation calls the shared inverse enumerator from the
cubic-neighbor-cap proof, preserving its case distinctions: the one-vertex
inverse branch does not receive restrictions derived only in the later
matching branch. The three-vertex branch has no eligible classified base.

Freshly proposed orders, independently checked by filling neighborhoods,
give treewidth at most seven for 66 candidates. These cannot be J. Failure
to find an order for the other five is not an exclusion or a lower-bound
certificate; all five remain in the next exhaustive check.

For each candidate, map the four surviving original highs injectively to
its twenty vertices. Enumerate every degree-compatible ordered map and
check the exact adjacencies and nonadjacencies among the four images.
For each original low, record its exact residual degree and its four-bit
neighbor mask to those highs. These sixteen signatures have fixed
multiplicities. The sixteen unused vertices of the candidate must have
exactly the same signature multiplicities relative to the chosen images.

Every graph isomorphism respecting the original partial graph induces
one of these maps and equal multiplicities. None exists for any of the
five candidates and any of the nine recipes. Thus all 45 embedding tests
exclude their complete possible families. The check deliberately ignores
additional low-low constraints, so this failure is already sufficient.
It uses no graph-isomorphism program or unverified canonicalization.

## Reproduction

```sh
python3 -O scripts/verify_order24_twenty_residue.py --native
```

The command checks catalogue coverage, regenerates the 71 candidates from
the pinned earlier family, verifies the 66 width-seven orders, and checks
all 45 impossible embeddings. Its recorded complete run took 5.84 seconds.
The only new data file is `sources/eleven-order24-twenty-residue.json`.

The check is relative to the stated packing theorem and earlier complete
classifications. To regenerate the small computational ingredient of the
packing proof, also run:

```sh
python3 -O scripts/verify_two_k4_incidence.py
```

The earlier large classification prerequisites retain their existing
reproduction commands. The exact treewidth of the five fallback graphs,
and whether any are isomorphic to one another, are not needed.
