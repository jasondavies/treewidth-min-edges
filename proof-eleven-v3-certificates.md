# Version-three branch certificates

Version three adds explicit neighborhood projection nodes and compact
deterministic program leaves. It uses the same independent Python event
verifier and the same earlier edge minima and minimum-counterexample premises
as versions one and two. Existing normalization and v1/v2 encodings remain
unchanged. A certificate still excludes only its stated root family; separate
catalogue coverage is required for an entire vertex count.

## Neighborhood projection

`['n', v, child]` requires a vertex of prescribed degree five with all five
neighbors certain. The checker enumerates every present/absent assignment to
the optional pairs inside this neighborhood. There are at most ten pairs, so
at most 1,024 cases. Outside pairs are unchanged.

A case is discarded only when a vertex has too many certain neighbors or too
few possible neighbors for its exact degree, or when the existing
`local_contradiction` function rejects it. Every actual counterexample
completion induces one of these cases and satisfies all these necessary
conditions. Consequently, a pair present in every surviving case can be
forced, and a pair present in none can be forbidden. The child must prove the
narrowed family empty. At least one deduction is required.

`['n', v]` is a terminal refutation, accepted only when all cases are discarded.
It cannot be substituted for a nonterminal projection or consume child events.

## Deterministic program leaves

`['g', normalized, policy, first, switch]` supplies one bounded program. The
mode is integer zero for the incoming family or integer one for the family
after ordinary local normalization. All parameters are checked before use.

The program repeatedly calls the existing checked `Bounds.tighten` and
`Bounds.step` operations. Each operation removes a vertex. It executes at most
the original number of vertices and succeeds only by deriving `Contradiction`.
Failure to choose a valid operation, or finishing without a contradiction,
rejects the leaf. The verifier never tries an alternative policy.

The policies are specified as follows:

| Policy | First choice | Subsequent choices |
| --- | --- | --- |
| 0 | Delete vertex `first` | Eliminate the smallest eligible vertex with upper degree at most three; otherwise delete a vertex with maximum certain degree, breaking ties by smallest label. |
| 1 | Delete vertex `first` | Eliminate the eligible vertex minimizing `(possible degree, upper degree, label)`; otherwise use the same deletion rule. |
| 2 | Pure-elimination trial `first`, from 0 through 8 | Sort eligible vertices by `(possible degree, upper degree, label)`. Trials 0–4 skip that many choices at the first operation. Trials 5–8 skip 1–4 choices at the second operation. All other operations choose the first eligible vertex. |

Eligibility for elimination means upper degree strictly less than the
maintained width lower bound. Subsequent greedy deletions require a positive
certain degree. Every deletion must preserve a positive width lower bound.
The existing operation checker also checks all ordinary preconditions.

`switch = -1` keeps the selected policy. For policies zero or one, an integer
`1 <= switch < n` starts pure-elimination trial zero after exactly `switch`
operations. Policy two cannot switch. These are supplied instructions, not a
search over programs during verification.

## References and traversal

Both new node types occupy one ordinary postorder node ID. A nonterminal
neighborhood node registers after its child. It retains its original
normalized family; deductions are applied to copied rows for the child. Thus
a later reference to the parent uses the broader family that was proved empty.

A raw program must execute before normalization even when a later reference
needs its snapshot: normalization could change a deterministic choice. Once
the raw program closes, the checker normalizes the original rows for that
snapshot. `Bounds.from_family` copies the rows, so program execution does not
change them. If snapshot normalization itself detects a contradiction, its
necessary deductions still describe a subfamily of the already-refuted family.

The existing exact-certain-edge and possible-edge-containment reference tests
are unchanged. Self references, ancestor references, and references to later
nodes fail because their targets have not closed. Replacing an explicit trace
leaf by a program leaf leaves every postorder reference ID unchanged.

## Binary representation

The existing `TW11B` transport header is retained, with proof-version byte 3.
Opcodes zero through three keep their previous meanings. The additional bytes
are:

| Opcode | Payload | Meaning |
| --- | --- | --- |
| 4 | One vertex byte, then one child subtree | Nonterminal neighborhood projection |
| 5 | One vertex byte | Terminal neighborhood refutation |
| 6 | Packed program byte, optionally a switch byte | Raw program leaf |
| 7 | Packed program byte, optionally a switch byte | Normalized program leaf |

The program byte stores `first` in bits 0–4, `policy` in bits 5–6, and a
switch-present flag in bit 7. A set flag requires one further byte containing
`switch`. Ordinary program leaves therefore use two bytes; switched leaves use
three. Every decoded parameter is range-checked. New opcodes are rejected in
v1/v2 certificates. Complete root consumption and end-of-file checks apply to
both JSON events and binary events.

## Verification

The version-three decoder is part of `branch_certificate_binary.py`.
The order-specific checkers validate roots and complete coverage in addition
to every mathematical proof step. See [the full route](verification-eleven.md).
