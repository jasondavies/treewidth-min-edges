# Removing the isolated-cubic condition from the H23 cap

The [23-vertex cubic-neighbor theorem](proof-eleven-cubic-neighbor-cap.md)
holds without its isolated-vertex hypothesis:

**Theorem.** Let H have 23 vertices, 42 edges, eight cubic vertices L, and
fifteen quartics. If H[L] has maximum degree at most two and tw(H) is at
least nine, every quartic of H has at most one cubic neighbor.

The proof retains all the earlier theorem's stated classification
premises. It makes no use of an archived 52-edge classification.

## The additional finite check

The original reduction H to J20, the general packing reduction for J20,
and the inverse construction of 71 necessary J graphs never use the
existence of an isolated cubic in H. That condition appears only in the
final filter of the reconstructed H graphs.

As before, 66 intermediate graphs have freshly checked width-seven orders.
Their universal-apex extensions have checked width-eight orders, covering
every lift from those intermediate graphs, with or without an isolated
cubic. This follows by first eliminating the two inserted degree-three
subdivision vertices: the remaining graph is a subgraph of J plus a
universal apex.

For the five remaining intermediate graphs, the reconstruction tries
51,260 inverse choices. After retaining the maximum-degree-two condition
on H[L], cubic-neighborhood independence, and cubic-pair codegree at most
one, 41,920 targets remain. The earlier theorem retained 39,760 of these.
All 2,160 additional targets, and all the old targets, have independently
checked width-eight elimination orders. Each of the five intermediate
graphs contributes 432 additional targets. No failed order search is used
as an exclusion.

Run the strengthened finite check explicitly:

```sh
python3 -O scripts/verify_cubic_neighbor_cap.py --native --without-isolate
```

The recorded complete portable run took 8.21 seconds. Its graph-stream
SHA256 is

```text
47b657c14e77e3f0981f5052e572f62397688668c7eb920f1e6d182823f5d58b
```

The `--without-isolate` option is required for this stronger statement.
The command's default retains the original family and theorem. The proof
still requires the earlier complete classifications and the two-K4
incidence lemma explained in the original theorem.

## Applying the stronger cap to order 25

Consider a hypothetical 52-edge, minimum-order counterexample with four
high vertices of degree five and twenty-one low vertices of degree four.
All four high neighborhoods must be exact. Each low vertex has at most
two high neighbors, and any two high neighbors of a low are adjacent,
by the existing minimal-counterexample restrictions.

Delete a nonadjacent high pair x,y. The remaining H has 23 vertices,
42 edges, and treewidth at least nine. All its degrees are known exactly
from the high-incidence root. Apply the rule only when these degrees are
eight threes and fifteen fours. Let L be the eight cubics. Additionally
check that every remaining high in L has at most two neighbors in L;
these incidences are exact because all high neighborhoods are known.

Each low cubic of H belongs to exactly one deleted-parent group, say x.
If it has no other high parent, it has at most one cubic neighbor in its
own group, by the one-triangle allowance at a low vertex, and at most
one in y's group, by the low-high common-low-neighbor bound. It has no
remaining high neighbor.

If it also has a remaining high parent z, the edge xz already gives a
triangle through this low. A neighbor in its own group would create a
second triangle, so there can be none. It has at most one neighbor in
y's group and at most one remaining high neighbor, namely z. Its degree
in H[L] is again at most two.

Together with the explicit check on the cubic highs, this proves that
H[L] has maximum degree at most two. No isolated vertex or private-incidence
assumption is needed. The strengthened theorem bounds every quartic's
number of cubic neighbors by one. Two required incidences refute the
family; one required incidence forbids every other possible one.

## Explicit version-eight nodes

The new JSON node is `['d']` for a cap contradiction or `['d', child]`
for a nonempty projection followed by one child. Binary opcodes 19 and
18 respectively encode these nodes in `52-edge-branch-refutation-v8`.
The checker recomputes all eligible deleted pairs and deductions. It
normalizes with the original procedure, then projects on copies, keeping
the original normalized parent for postorder references.

Versions one through seven retain their semantics. In particular, the
version-six private cap still requires its original isolated-cubic-high
condition; version-seven marked-H22 nodes are unchanged. `Bounds`, local
normalization, numerical traces, and deterministic programs do not gain
implicit applications of the stronger theorem.

## Supplied profile exclusions

The fifteen supplied version-eight certificates exclude these order-25
profiles:

```text
000011 000111 000112 001100 001102 001200 001201 001211 002111 002200 002201 011111 011120 011220 012210
```

They occupy 273,980 compressed bytes in
`sources/eleven-order25-broad-cap`. Every completed proof was independently
replayed with its exact catalogue prefix. These are additional profile
exclusions, not a complete order-25 certificate. Combining the current
components leaves profiles `000001` and `001011` unresolved by these proofs.

The tests cover opt-in family expansion with unchanged default counts,
new nonprivate deductions, scope failures, false terminals, binary and JSON
roundtrips, rejection by older formats, truncation/trailing data, and packing.
Independent C/Python differential testing agrees on 600 partial families,
including 435 with shared low attachments. The older mathematical helper
functions, including the version-six and version-seven projections, retain
identical abstract syntax.
