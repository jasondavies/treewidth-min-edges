# An explicit marked-residue projection for order 24

This rule uses two completed premises in addition to the ordinary
minimum-counterexample reduction and earlier edge minima:

- [The marked H22 characterization](proof-eleven-marked-residue.md), including
  its earlier-classification premises.
- [The complete exclusion of its nonadjacent-high reconstructions](proof-eleven-exceptional-nonadjacent-pair.md).

It is an additional rule in branch-certificate format v7. Ordinary
normalization, interval bounds, explicit traces, and program leaves retain
their previous meanings.

## The mathematical implication

Consider a hypothetical minimum-order graph G of treewidth at least eleven,
with 24 vertices, 52 edges, eight highs of degree five and sixteen lows of
degree four. Suppose all high neighborhoods are known exactly.

Delete two nonadjacent highs x,y. This removes ten edges and leaves
H=G-{x,y} with treewidth at least nine. Use the rule only when its exact
residual degrees are four cubics L and eighteen quartics Q. The residual
degrees can be computed exactly because the deleted neighborhoods are known.

Let S be a subset of L with at least two vertices. Require that S is
independent and that every vertex of L-S has exactly one neighbor in S.
These statements must hold for every represented completion: every possible
edge within S is forbidden, and each vertex in L-S has exactly one known
neighbor in S with no other possible neighbor in S.

The graph H[L] is a proper subgraph of K(2,2). Indeed, at the edge minimum
f(9)=42 every cubic neighborhood is independent and two cubics have at most
one common neighbor, as proved in the marked-residue theorem. Thus H[L]
has neither a triangle nor a four-cycle and is a forest on four vertices.
The only such forest not embeddable as a proper K(2,2) subgraph is K(1,3).
That star has no eligible S: including its center prevents including any
other vertex, whereas selecting two or more leaves gives the center more
than one neighbor in S. The hypotheses on S therefore exclude the star.

No quartic w in Q can have two neighbors in S. Otherwise H satisfies every
hypothesis of the marked-residue theorem and is isomorphic to its fixed
exception. But adding back the two nonadjacent degree-five vertices makes
G one of the completely checked 24-vertex reconstructions of that exception.
Every such graph has treewidth at most ten, a contradiction.

Consequently, for each eligible S and each w in Q:

- Two known neighbors of w in S refute the current family.
- If one neighbor is known, every other possible edge from w to S is forbidden.

All these consequences concern the original graph G; no graph vertex is
removed from the branch-certificate state.

## Exact syntax and checking

The JSON forms are

```text
["m"]
["m", child]
```

The checker independently enumerates every nonadjacent high pair having the
required residual degree profile, then every eligible subset S of its four
cubics. The first form requires an actual contradiction. The second requires
at least one newly forbidden edge, followed by a complete proof for the
projected family. The projection runs on a copy; the normalized parent state
is preserved for the existing postorder reference rule.

Binary opcode 16 denotes a projection with one child; opcode 17 denotes a
terminal contradiction. Only format v7 admits these opcodes. Previous
formats reject the new node, and previous node semantics are unchanged.
The public premise notice names both added theorems for all checking CLIs.

The untrusted generator may first branch on optional edges among the four
cubics. These are ordinary `e` nodes, whose two children cover edge absence
and presence. They make more eligible S sets exact; they introduce no
additional mathematical assumption and no implicit pruning.

## Completed profile proofs

The new rule gives complete independently replayed proofs for catalogue
indices 35, 37 and 155:

| Index | Proof nodes | Marked projections | Marked terminal leaves |
|---:|---:|---:|---:|
| 35 | 41,360 | 51 | 0 |
| 37 | 27,723 | 5 | 630 |
| 155 | 72,617 | 608 | 793 |

The C proposer took approximately 4.8, 3.0 and 9.0 seconds respectively on
the validation machine. Each complete binary stream was independently
replayed by Python against the exact catalogue prefix before acceptance.
No incomplete search output is a proof artifact.

