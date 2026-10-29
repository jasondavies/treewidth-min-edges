# Explicit cubic-cap projections for private order-25 profiles

The two supplied certificates exclude the private P4 and paw high-incidence
profiles `001101` and `001111`. Together they occupy 4,608 compressed bytes.
They use the [H23 cubic-neighbor theorem](proof-eleven-cubic-neighbor-cap.md)
in addition to the older numerical and minimum-order premises of the branch
checker. They do not constitute a complete order-25 or 52-edge exclusion.

## When the rule applies

Consider a hypothetical minimum-order, 52-edge graph of treewidth at least
eleven, with four degree-five vertices and twenty-one degree-four vertices.
Call these the high and low vertices. All four high neighborhoods must be
completely specified, and each low vertex must be adjacent to at most one
high vertex. This last condition is the private-incidence hypothesis.

Choose two nonadjacent high vertices x and y. Their deletion removes ten
edges, so the remaining graph H has twenty-three vertices, forty-two edges,
and treewidth at least nine. Because every high incidence is known, every
remaining vertex's degree is known exactly. The checker applies the rule
only if these degrees are eight threes and fifteen fours, and at least one
remaining high vertex is cubic. It also checks that every remaining cubic
high vertex has no cubic neighbor.

Write C for the eight cubics of H. A low member of C originally belonged
to the private group of x or y. Within its own group it has at most one
neighbor: two such neighbors would give it two triangles with its high
parent, contradicting the existing low triangle bound. In the other deleted
high's group it has at most one neighbor, by the existing upper bound of
one common low neighbor for a low-high pair. It cannot be adjacent to a
remaining high vertex, by privacy. These facts give degree at most two in
H[C]. The explicitly checked cubic high vertices are isolated in H[C],
so H[C] also has an isolated vertex.

The H23 theorem now says that every quartic of H has at most one cubic
neighbor. If two of these incidences are already required, the family is
empty. If exactly one is required, all other possible incidences between
that quartic and C can be forbidden. This argument applies independently
to each eligible nonadjacent high pair. Every deduction concerns an original
edge: the rule uses vertex deletion only, with no filling.

The theorem is an explicit additional premise with its own source-only
finite checks and earlier-classification dependencies. It is not inferred
from numerical edge minima alone.

## Certificate semantics

The format is `52-edge-branch-refutation-v6`, in the existing TW11B binary
transport. Versions one through four keep their previous semantics; version
five remains reserved for a separate experimental format.

The new JSON node is either `['c']`, a terminal cap contradiction, or
`['c', child]`, a projection followed by one child. Binary opcode 15 is the
terminal form; opcode 14 has one child and no payload. The checker recomputes
all eligible high pairs and every deduction. A nonterminal node must make
at least one change. A terminal node must derive an actual contradiction.

As for other projection nodes, the incoming family is first normalized by
the unchanged original procedure. Cap deductions are made on copies; the
parent's normalized family remains the state registered for postorder proof
references. The child is checked on the narrowed family. The original
`normalise`, `Bounds`, numerical trace checker, and deterministic program
semantics are unchanged. The rule is never applied implicitly to old
certificates or to old trace programs.

Version-six certificates may also contain the existing neighborhood and
edge-split nodes. The binary codec checks node arity, root identity, complete
branch coverage, and final end-of-file. JSON packing accepts version six;
older program-conversion tools do not support the new projection node and
reject it rather than silently rewriting it.

## Checked certificates and reproduction

| Profile | Nodes | Cap projections | Cap contradictions | Compressed bytes |
|---|---:|---:|---:|---:|
| P4, `001101` | 865 | 284 | 4 | 1,372 |
| Paw, `001111` | 2,456 | 826 | 16 | 3,236 |

Both supplied certificates were independently replayed under `python3 -O`,
which leaves all checks active. Recorded generation times were 0.03 and
0.12 seconds; replay took 0.24 and 0.70 seconds. Counts and timings are
diagnostics, not premises.

To check the supplied certificates:

```sh
python3 -O scripts/verify_branch_refutation.py sources/eleven-order25-private-cap/001101.bin.xz
python3 -O scripts/verify_branch_refutation.py sources/eleven-order25-private-cap/001111.bin.xz
```

