# Independently checked branch certificates for order 25

This bundle covers **twenty of the forty necessary order-25 profiles**.
It is **463,288 bytes**, compressed from 1,961,161 bytes of binary proof data.
Nineteen members use ordinary rules; profile `000012` uses the explicit
broad and one-high cap rules, reducing its replay from 809 to 2.8 seconds.
It needs no C generator, nauty, checkpoint archive, or stored success report
to verify.

The [complete order-25 checker](proof-eleven-order25-claw.md#reproduction)
adds eighteen separate branch proofs and two structural reductions to cover
all forty profiles. Order 24 also has a complete independent certificate.
This component alone is **not the complete 52-edge exclusion**: the remaining quartic
cases use the retained enumerations.

## What the checker establishes

Run `python3 scripts/verify_order25_complete.py` for all forty profiles.
The full runner also checks its finite premises.

Each claim concerns a **minimum-order 52-edge counterexample** of treewidth
at least eleven. Some rules use minimum order, so the checker does not claim
to bound the treewidth of every arbitrary completion of these profiles.
The [four-step example](proof-eleven-profile20.md) explains the base interval rules.

The version-ten member additionally uses the
[broad cubic cap](proof-eleven-cubic-neighbor-cap-extension.md) and
[one-high cap](proof-eleven-one-high-cubic-cap.md), with their explicitly
stated earlier classification and finite-check dependencies.

The basic mathematical premises are the earlier edge lower bounds

| Treewidth at least | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Required edges | 1 | 3 | 6 | 10 | 15 | 21 | 28 | 34 | 42 | 47 |

The [preliminary parity argument](proof-eleven.md#1-reducing-the-lower-bound-to-six-vertex-counts)
then gives the lower bound 52 for treewidth eleven, independently of the
52-edge exclusion being proved. These are fixed in the checker, not supplied
as numerical claims in the certificate. The earlier results remain explicit
dependencies; the new checker replaces neither their proofs nor their data.

## Complete catalogue, without a graph-isomorphism library

At order 25 there are four degree-five vertices and twenty-one degree-four
vertices. Call them high and low vertices respectively. The elementary
restrictions below imply that a low vertex has zero, one, or two high
neighbors. If it has two, they are adjacent. No high pair has more than
one shared low neighbor.

Thus each of the six high pairs has one of three states:

- `0`: no high--high edge;
- `1`: an edge without a shared low neighbor;
- `2`: an edge with one shared low neighbor.

For a fixed assignment, add one low vertex for each `2`, then enough private
low neighbors to give every high vertex degree five. All remaining low
vertices have no high neighbor. This determines every edge incident to a
high vertex. The edges between low vertices remain unspecified.

[order25_profiles.py](scripts/order25_profiles.py) tries all $3^6=729$
assignments. It rejects impossible degrees and violations of the triangle
and nonadjacent-high-neighbor restrictions. It identifies equivalent
assignments by explicitly trying all $4!=24$ permutations of the high
vertices. Exactly forty classes remain. The ordering of private low
vertices, shared low vertices of the same type, and free low vertices is
immaterial: these vertices all have the same target degree and incidence.
Consequently every minimum counterexample of order 25 belongs to a listed
family after relabeling. No successful-search count is used to establish
this coverage.

```sh
python3 scripts/order25_profiles.py --output /tmp/order25-roots.txt
```

The six-digit codes printed by the bundle checker refer to pairs
`01, 02, 03, 12, 13, 23`, using the lexicographically smallest coloring under
the 24 permutations. They are independent of the historical profile indices.

## Why the local propagation rules are valid

Let $G$ be a minimum-order 52-edge counterexample, and let $L,H$ be its low
and high vertex sets.

1. **Triangle counts.** Eliminating a degree-$d$ vertex in $t$ triangles
   changes the edge count by $\binom d2-d-t$. For degree four this is
   $2-t$, and for degree five it is $5-t$. A nonpositive change contradicts
   minimum order or the exclusion below 52 edges. Thus a low vertex is in
   at most one triangle and a high vertex in at most four.
2. **High neighbors of a low vertex form a clique.** Deleting two
   nonadjacent high vertices leaves 42 edges and treewidth at least nine.
   A common low neighbor then has degree two; eliminating it loses an edge,
   contradicting the 42-edge lower bound. The triangle count further limits
   each low vertex to at most two high neighbors.
3. **Common low neighbors.** For distinct $u,v$, the set
   $S=N(u)\cap N(v)\cap L$ is independent: an edge inside $S$ would put
   either low endpoint in two triangles. Delete $u,v$ and eliminate the
   now-degree-two vertices of $S$. Their independence ensures each loses
   at least one edge. The 42-edge lower bound gives
   $|S|\le10-\deg(u)-\deg(v)+[uv\in E]$.
   Together with the low triangle bound, this gives at most two common
   low neighbors for a low--low pair and at most one for every other pair.
4. **A low vertex's triangle includes every high neighbor.** Deleting a
   high neighbor leaves 47 edges and treewidth at least ten. The low vertex
   becomes cubic; a surviving edge in its neighborhood would let elimination
   lose an edge, contradicting the 47-edge lower bound.
5. **Deleting nonadjacent high neighbors of a high vertex.** The deletion
   leaves 42 edges and treewidth at least nine. The vertex becomes cubic,
   so its remaining neighborhood must be independent for the same reason.
6. **Connectedness.** A proper saturated component can never acquire an
   edge to the rest of the graph. A disconnected counterexample would have
   a component of treewidth at least eleven with fewer vertices, contrary
   to minimum order.

The checker maintains certain and possible edges. It forces edges required
by exact degrees or rule 2, and forbids an optional edge when adding it
already violates a monotone local restriction. It repeats these deductions
until stable. Each deduction retains every hypothetical counterexample.

## Checking branches, symmetry, and terminal reductions

The proof is a finite tree with three node types:

- `['x']`: the local propagation above derives a contradiction;
- `['r', steps]`: a supplied sequence of deletions and eliminations derives
  an edge, vertex-count, or degree contradiction;
- `['b', vertex, children]`: exhaust every possible missing-neighbor choice
  for that vertex, then check every corresponding child.

At a branch, the checker computes the required number of additional
neighbors and all possible choices itself. The number and order of children
must match exactly. Completing a row adds its chosen edges and rules out
every unchosen edge incident with that vertex.

Symmetry removes choices only among vertices of equal target degree whose
certain and possible neighborhoods agree outside the pair itself. The
transposition of any such pair is therefore an explicitly checked
automorphism of the partial family. Within each interchangeable class,
choosing any given number of vertices is equivalent to choosing its first
vertices. The checker enumerates every possible vector of these counts.
It does not use nauty or trust a generator's isomorphism decision.

The checker additionally uses [order-sensitive edge bounds](proof-eleven-order-bounds.md)
and [cubic-neighbor incidence bounds](proof-eleven-cubic-bounds.md). Both are
proved from the earlier numerical minima and elementary graph arguments;
neither assumes any of the 52-edge exclusions being certified.

The `r` nodes use the degree/edge interval operations from the
[four-step checker](proof-eleven-profile20.md#checking-incomplete-neighborhoods).
They also tighten each degree to at most $E-f(k-1)$, because deleting that
vertex must leave treewidth at least $k-1$. The degree sum bounds the number
of edges. If $E=f(k)$ and $k\ge4$, nonisolated vertices must have degree at
least three, and cubic neighborhoods must be independent; otherwise a
low-degree elimination would lose an edge while preserving treewidth $k$.
These implications can force or forbid further edges. Fewer than $f(k)$
edges, or at most $k$ remaining vertices, is an immediate contradiction.

Version 1 stores a tree. Version 2 additionally permits a reference to an
already closed node, accompanied by an explicit permutation preserving the
degree classes and certain edges. The current possible edges, after that
permutation, must be contained in the previously certified possible edges.
This makes the referenced exclusion apply to the current family. IDs follow
postorder: a node is registered only after all its obligations are proved.
Self-references, forward references, and cycles are therefore rejected.
Only snapshots that will actually be referenced are retained, and each is
released after its last use. Every branch still finishes a previously
unfinished vertex, and every operation in a terminal trace removes a vertex.

Before normalizing a refutation leaf, the checker may execute its supplied
trace on the larger incoming family. If that already derives a contradiction,
normalization adds no necessary premise. A failed attempt changes no state;
the checker then normalizes and checks the trace as usual. This shortcut is
used only when no later reference needs that leaf's normalized snapshot, so
postorder reference identities and the retained states remain unchanged.

Version 3 adds [bounded program leaves and neighborhood projections](proof-eleven-v3-certificates.md). Program leaves encode a supplied deterministic sequence of checked operations in two or three bytes. Neighborhood nodes exhaust at most 1,024 local edge patterns. Neither extension changes the earlier mathematical premises or accepts a search program's success report.

## Streaming encoding

[branch_certificate_binary.py](scripts/branch_certificate_binary.py) encodes
one v1, v2, or v3 proof. The header is `TW11B`, byte 1, the proof-version byte,
the vertex count and completed-prefix length, then one unsigned base-128
adjacency-mask integer per vertex. Its scope is fixed to minimum-order
52-edge counterexamples. Preorder node opcodes are:

| Opcode | Contents |
| --- | --- |
| 0 | Local contradiction |
| 1 | Trace length, then one byte per operation: vertex plus 32 for elimination |
| 2 | Branch vertex, child count, then every child in order |
| 3 | Earlier postorder node ID, then a complete vertex permutation; v2 or v3 |

Lengths, counts, masks, and reference IDs use canonical unsigned base-128
encoding below $2^{63}$. Vertex labels use single bytes. Version 3 additionally
uses opcodes 4–7 for [neighborhood nodes and program leaves](proof-eleven-v3-certificates.md#binary-representation).
The decoder rejects malformed fields, missing children, truncation and trailing
bytes. JSON and binary adapters feed the same proof traversal and inference
functions. The v2/v3 prepass derives reference counts by parsing the proof; no
stored counts or success receipts are trusted. The actual checks still require
an earlier closed target, preventing circular justification.

The [bundle format](scripts/branch_certificate_bundle.py) begins with
`TWBBC1` and a newline, one order byte (23, 24, or 25), and a member count.
Each member has a byte length followed by its complete `TW11B` encoding.
Lengths are bounded by 1 GiB and the outer stream must end exactly after the
last member. Each proof gets fresh reference state. The order-specific
verifier separately validates catalogue membership, rejects duplicate roots,
and recomputes the missing list. XZ compression surrounds the complete file.

