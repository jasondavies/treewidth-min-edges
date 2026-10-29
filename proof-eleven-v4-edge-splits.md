# Explicit optional-edge splits

This optional v4 extension adds one exhaustive case split to the existing
branch-certificate checker. It changes no numerical bounds, local propagation,
neighborhood-pattern rule, or deterministic program expansion. It is useful
for recording failed assumptions: an inexpensive refutation of one edge value
lets the proposer continue searching with the other value.

A state describes graphs with the fixed root degree profile, containing every
known edge and using only possible edges. After the usual normalization, let
`uv` be possible but not known. Every represented graph belongs to exactly one
of these two families:

1. `uv` is absent: remove it from the possible-edge relation.
2. `uv` is present: add it to the known-edge relation.

Both children retain the original exact degree profile. Their independent
refutations therefore refute the parent family. The checker requires distinct,
in-range integer endpoints in increasing order and requires the edge to be
optional. It visits separate copies of the parent state; neither child's
propagation changes the other child or the parent.

## Encoding and references

The JSON node is

```text
["e", u, v, absent_child, present_child]
```

Only `52-edge-branch-refutation-v4` accepts it. Its binary encoding is opcode
`12`, one byte for `u`, one byte for `v`, then the absent and present subtrees,
in that order. Existing v1/v2/v3 nodes retain their meanings. A v4 proof may use
ordinary traces, neighborhood projections and program leaves without changing
how those nodes are checked.

Both children are mandatory. The binary reader accounts for both subtrees and
rejects truncated trees and trailing bytes. Postorder reference IDs count all
closed nodes as before. The parent becomes available as a reference target
only after both children close, and its saved state is the original normalized
parent. References may point to earlier closed nodes in either already visited
subtree; self and forward references remain invalid.

The length-prefixed bundle format requires no new outer format: its existing
member parser delegates to the certificate header parser, which now explicitly
accepts version 4. The streaming program converter preserves v4 and traverses both children in
the same order. It may replace an explicit trace by a bounded program, preserving
node counts and postorder references. Its output must be checked independently.
The older JSON program converter explicitly rejects v4.

## Verification

The version-four inference rules are checked by the ordinary branch verifier.
The selected order-specific checkers supply the required root-coverage checks;
see [the verification guide](verification-eleven.md).
