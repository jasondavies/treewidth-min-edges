# The order23 exclusion by two choices of anchors

Under the minimum-counterexample reductions, an order23 graph has twelve
vertices of degree five (the **high** vertices) and eleven vertices of degree
four (the **low** vertices). This argument excludes that case using the original
root-coverage certificate, four small refinement covers, and the retained
family-exclusion proofs. It does not require a direct proof of every family
listed in the original catalogue.

The verifier checks every supplied family proof before applying the argument
below. Each refinement is also checked in full, and every terminal dependency
of every refinement must have a supplied proof. Thus a refinement is completely
resolved before any structural conclusion is drawn. In particular, the
argument never transfers designated anchors through a refinement's inclusion
map.

## What the coverage certificate establishes

The original root proof and catalogue are unchanged. Its first node completes
the neighborhood of high vertex 0; each child next completes high vertex 1.
The remaining branches enumerate complete neighborhoods modulo explicitly
checked twin permutations. A branch that closes by a local contradiction or
an ordinary numerical trace cannot contain a counterexample.

At a surviving original catalogue leaf, the existing `c` rule gives a
permutation preserving the degree classes, all known edges exactly, and
containment of possible edges. The family-exclusion proofs and the four
refinements resolve most of these original leaves. The finisher computes the
remaining original catalogue indices itself; it does not accept an advertised
count or a list of asserted exclusions.

For each remaining original target, the finisher checks:

1. Exactly high vertices 0, 1, 2 have complete known neighborhoods.
2. Each of these vertices has at most four high neighbors, and hence at least
   one low neighbor.
3. No two of them share a low neighbor.

With the pruned 231-member proof bundle, 33 original targets remain, and every
one passes these tests. Four other original families are resolved by refinement
covers: 18, 22, 25, 57. Their covers contain four neighborhood-branch nodes,
112 local-contradiction leaves, and 68 explicit inclusion maps into supplied
family proofs.

## Why the designated anchors are preserved

Initially every unlabelled high vertex other than 0 belongs to the same twin
class. Consequently high vertex 0 can be any chosen high vertex of a hypothetical
counterexample. Moreover, if it has a specified high neighbor, the first
neighborhood representative can label that neighbor 1: the selected high
neighbors form a prefix of the high twin class, beginning at 1. The finisher
checks this prefix property and that the next branch completes vertex 1.

After a vertex's neighborhood is complete, normalization sets its possible
neighbors equal to its known neighbors. It cannot then be an optional neighbor
in any later branch. The twin permutations used to select neighborhood
representatives act only on optional neighbors, so they fix completed vertices.
In particular, later branches preserve the designated vertices 0 and 1. A shared
low neighbor may acquire another label, but remains a shared low neighbor.

At an original `c` leaf, equality of the known-edge graphs sends every completed
high vertex to a completed high vertex of the target. Thus vertices 0 and 1 map
to two of its three completed high anchors. Their exact high/low neighborhoods
are preserved. This equality is why the fingerprints are taken from original
`c` targets, after discharging all refinements, rather than from arbitrary
inclusion-map targets.

## Two rootings give the contradiction

First choose an arbitrary high vertex h and label it 0. Coverage cannot end in
a resolved family or a contradiction leaf. In an unresolved original target,
the image of h has at most four high neighbors. Because h has degree five, it
has a low neighbor. Since h was arbitrary, **each of the twelve high vertices
has at least one low neighbor**.

Now suppose a low vertex l has two high neighbors u and v. The high neighbors
of a low vertex form a clique, by the already established local restriction.
For completeness, if u and v were nonadjacent, deleting them would leave
42 edges and treewidth at least nine, with l of degree two. Eliminating l loses
at least one edge without lowering that treewidth, contradicting the certified
42-edge minimum for treewidth nine. Hence u and v are adjacent.

Label u as 0 and choose its specified high neighbor v as 1 in the first
neighborhood representative. Complete their neighborhoods. The known shared
low neighbor persists through all later twin permutations. Any surviving
original `c` target would therefore have two completed high anchors sharing a
low neighbor, contradicting the third fingerprint check. Thus **each low
vertex is adjacent to at most one high vertex**.

The twelve high vertices require at least twelve high-low incidences, while
the eleven low vertices permit at most eleven. This contradiction excludes
order23.

## Verification and reproduction

`verify_order23_coverage.py` checks v1 coverage as before. Its v2 extension
checks all refinement trees, rejects duplicate or unknown refinement indices,
rejects cyclic dependencies, and computes the final required catalogue indices.
An inclusion leaf records an explicit permutation and checks
`target known ⊆ mapped current known` and
`mapped current possible ⊆ target possible`.

The explicit master command is:

```sh
python3 scripts/verify_order23_anchor_finish.py \
  sources/eleven-order23-refutations.bin.xz \
  --coverage sources/eleven-order23-coverage.json.xz
```

It first independently verifies all supplied mathematical certificates, then
checks the coverage and the structural conditions above. The ordinary
partial-bundle verifier remains available and does not silently apply this
additional argument.

The default master command is serial and supports Python 3.10. Optional parallel
verification requires Python 3.11 or newer:

```sh
python3 scripts/verify_order23_anchor_finish.py \
  sources/eleven-order23-refutations.bin.xz --workers 4 \
  --reports /tmp/order23-verification
```

Parallel mode checks the
current member bytes afresh through the existing independent parallel verifier;
it requires every member to pass before using any returned family index. Saved
reports are never accepted as substitutes for verification.
