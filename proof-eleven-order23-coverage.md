# Independently checked order-23 exclusion

The compact proof excludes every minimum-order counterexample with 23 vertices
and 52 edges. It uses **6,640 bytes of coverage data**, **3,480,956 bytes of
family proofs**, and a short [pigeonhole argument](proof-eleven-order23-anchor-finish.md).
Other vertex counts still require separate proofs.

Check the complete order-23 component with:

```sh
python3 scripts/verify_order23_anchor_finish.py \
  sources/eleven-order23-refutations.bin.xz --workers 4
```

Parallel verification requires Python 3.11 or newer. Omit `--workers 4` for
serial verification with Python 3.10. Every supplied mathematical proof is
checked afresh; saved reports and advertised counts are not accepted as evidence.
The premises are the earlier edge minima through treewidth ten and the written
minimum-counterexample reduction. A fresh full replay of the 231 supplied
proofs and the anchor finish passed in 731.76 seconds with four workers on
the development machine, including with Python assertion statements disabled.

## Coverage from an empty graph

The reduction gives twelve vertices of degree five and eleven of degree four.
Relabel them so the degree-five vertices come first. The starting interval is
`[23, 0, 0, ..., 0]`: every edge is initially optional, with those prescribed
degrees.

The original coverage tree completes the neighborhoods of vertices 0, 1, and 2.
At each branch, the checker enumerates every neighbor selection up to explicitly
checked interchangeable-vertex classes. Every choice has one child. A leaf is:

- a contradiction from the existing local necessary conditions;
- a supplied sequence of deletions and eliminations, checked with the interval bounds; or
- an explicit permutation into a named catalogue family.

At an original `c` catalogue leaf, the map preserves the degree classes and
**every certain edge exactly**. The image of the possible edges must be a subset
of the target family's possible edges. Thus every completion belongs to the
target family, and complete vertex neighborhoods are preserved by the map.

The first 375 catalogue entries are historical depth-three prefixes; the proposer
appended 50 unmatched families. Neither this former census nor its counts are
trusted. The checked tree references 218 original entries and all 50 appended
entries, for 268 families. Unused entries do not affect coverage; 103 seeds are
already excluded by the local rules.

This original tree contains 66 branch nodes, 1,200 local contradiction leaves,
12 trace leaves, and 469 catalogue-reference leaves. The checker uses no graph
library, canonical-labeling program, archived census, or generator.

## Four refinements and the counting argument

The v2 coverage certificate retains the original tree and catalogue and appends
four small covers for families 18, 22, 25, and 57. Each completes one further high
neighborhood. Together they have 4 branch nodes, 112 local contradictions, and
68 explicit inclusion maps into supplied family proofs.

A refinement's `i` map requires `target known ⊆ mapped current known` and
`mapped current possible ⊆ target possible`, preserving degree classes.
Every refinement and its full dependency graph is checked; cycles are rejected.
The complete verifier requires all terminal dependencies to have checked proofs.

The [branch-proof kernel](proof-eleven-branch-certificates.md) checks the 231
retained family proofs, including [neighborhood projections and short
programs](proof-eleven-v3-certificates.md) and [edge splits](proof-eleven-v4-edge-splits.md).
This leaves 33 original catalogue families with a common checked property:
each of their three completed high vertices has a low neighbor, and those low
neighborhoods are pairwise disjoint.

The [anchor argument](proof-eleven-order23-anchor-finish.md) applies the original
coverage first with any chosen high vertex, then with any chosen adjacent high
pair. It follows that all twelve high vertices need low neighbors and no low
vertex can serve two of them. There are only eleven low vertices. This finishes
the order-23 exclusion without separate proofs of the remaining 33 families.

The ordinary family verifier deliberately retains its narrower meaning:

```sh
python3 scripts/verify_order23_refutations.py \
  sources/eleven-order23-refutations.bin.xz
```

It checks all 231 proofs and returns **2**, reporting 33 of the 264 terminal
family obligations missing. The explicit anchor-finishing command above adds
the counting argument and establishes the complete order-23 exclusion.

## Verification

```sh
python3 scripts/verify_order23_coverage.py sources/eleven-order23-coverage.json.xz
```

Coverage alone is not exclusion. The [anchor finisher](proof-eleven-order23-anchor-finish.md)
also verifies all supplied family proofs and the final counting argument.
