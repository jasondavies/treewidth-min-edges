# A stored certificate excluding path-shaped square incidence

The certificate excludes a four-vertex path in the square-incidence graph
at any vertex of a quartic minimum-order 52-edge counterexample. This is
one quartic subcase, not the full 52-edge exclusion.

**Complete.** The final assembled serial replay passed: all 10,400 graph
clauses and 21,145 propositional steps were checked in 534.94 seconds,
using 527.66 user CPU seconds. Reported peak resident memory was 304,628 KiB.
The default uses one worker; `--workers 4` checks independent graph
clauses in parallel, with fresh proofs and exact result coverage. A full
four-worker replay also passed in 74.62 seconds (294.95 aggregate user CPU
seconds; reported peak resident memory 349,100 KiB). The runs occurred
under different machine loads; these are measured reproduction times,
not an isolated parallel-scaling benchmark.

For a vertex v, its square-incidence graph has vertex set N(v), with an
edge between two neighbors when they have another common neighbor. The
[proved square-direction restrictions](proof-eleven-quartic-square-directions.md)
and the independently checked original-v1 C4 certificate leave maximum
square incidence three and prohibit triangles in this incidence graph.
Thus a copy of P4 must be the entire incidence graph at v.

The root is the canonical mask 13 profile from `quartic_square_profiles.py`,
with suffix-to-suffix edges omitted. In particular the already proved
opposite-corner edge 6–7 is not initially assumed. This larger root family
contains every relevant P4 completion. The certificate separately proves
that edge as a graph-theoretic unit clause.

## What is checked

The stored files are:

- `sources/eleven-quartic-p4-rup.json.xz`: 916,776 bytes of propositional proof;
- `sources/eleven-quartic-p4-theory.json.xz`: 334,916 bytes of graph-clause proofs.

Their total compressed size is 1,251,692 bytes. Their individual uncompressed
sizes are 7,640,980 and 14,406,769 bytes. The theorem checker requires Python
and the repository's earlier proof modules and small classification files.
It requires no SAT solver, C compiler, archived search log, or external
isomorphism library:

```sh
python3 -O scripts/verify_quartic_path_refutation.py --workers 4
```

The [Boolean encoding proof](proof-eleven-quartic-path-cnf.md) explains
the standard-library reconstruction of degree equations, triangle exclusion,
common-neighbor counts, square-incidence restrictions, and lexicographic
symmetry constraints. It supplies 187,599 logical clauses over 38,961
variables. Every permitted graph has an auxiliary-variable extension;
a lexicographically least labeling in its permitted symmetry orbit meets
the symmetry constraints.

The saved positive-hint reverse-unit-propagation proof uses 20,590 initial
clauses and 21,145 derived steps. Exactly 10,190 initial clauses occur in
the reconstructed logical formula. Every other initial clause is checked
as a graph-theoretic consequence. The checker compares actual clause
contents; historical clause IDs, solver results and logged reason codes
are not premises.

For each of these 10,400 graph clauses, the checker starts from the fixed
root and negates every literal: a negated edge literal forces that edge,
and a positive edge literal forbids it. It then checks the supplied local
projections and a terminal proof. This establishes the clause for all
hypothetical counterexamples, not merely one sampled completion.

Finally, the propositional checker validates every reverse-unit-propagation
step and requires the final empty clause. A solver's unsuccessful search,
time limit, or negative treewidth answer never enters this argument.

## Explicit quartic projection

`quartic_path_projection.py` imports the original interval rules without
changing their meaning. Its additional premises are stated explicitly:
the triangle exclusion, common-neighbor cap two, square-direction lemmas,
original-v1 C4 exclusion, and marked-H22 theorem with its complete exceptional
quartic-square reconstruction. The triangle and C4 premise checkers reject
newer branch formats, so those premises cannot be proved by a rule which
already assumes their conclusions.

The projection rejects a known triangle, excessive common-neighbor count,
more than three known squares at a vertex, or triangular square incidence.
It forces the already proved edge between opposite corners of disjoint
square directions. It may also forbid an optional edge whose addition
would violate one of these restrictions.

For a square x-a-y-b-x with all four corner neighborhoods exact, delete
x,y and suppress a,b. Triangle-freeness and the common-neighbor cap make
the eight private neighbors distinct in the required ways. The resulting
H has 22 vertices, 42 edges, four cubics L and eighteen quartics. The two
new suppression edges lie entirely outside L.

The four cubics split into two private-neighbor pairs. Their induced graph
is one of the 15 proper labeled subgraphs of K2,2. The checker considers
every pattern consistent with the current edge information. In each
pattern it applies:

1. independent neighborhoods at cubic vertices and the cubic-pair
   common-neighbor cap one, consequences of f(9)=42;
2. the marked theorem: if S is independent in L and every vertex of L−S
   has exactly one neighbor in S, distinct members of S have disjoint
   neighborhoods outside L, since the complete exceptional quartic lift
   was independently excluded.

The second condition also forbids a common neighbor inside L: independence
and exact domination already rule one out. This justifies the implementation's
cap-zero test over all of H for those selected pairs.

Each case retains a separate copy of the original G edge interval. The
suppression fills exist only in a temporary H adjacency view. They may
cause a contradiction or forbid an original cubic incidence, but are
never added to G or transferred back as original edge information. The
unchanged G rules may propagate further deductions within each case.
The intersection of all surviving known-edge sets and union of their
possible-edge sets safely covers every original completion. No surviving
case, or every case refuted, is determined by a search timeout.

## The explicit 35-edge terminal

Some ordinary deletion/elimination traces reach treewidth lower bound eight
and an edge upper bound of 35. Their terminal uses the complete earlier
34-edge classification and full 35-edge minimum-degree-three classification.
These are stronger premises than edge minima alone and are named as such.

After removing isolates, a compatible graph with minimum degree at least
three occurs in the earlier families. A degree-one vertex can be deleted;
a degree-two vertex can be suppressed. These operations preserve a
width-eight lower bound and lose at least one edge. Two edge losses would
contradict f(8)=34, and a degree-two vertex with adjacent neighbors loses
two immediately. Thus the only additional 35-edge possibilities arise from
a 34-edge graph by one pendant-edge addition, one separate isolated-edge
addition, or one edge subdivision. Arbitrarily many isolated vertices
are handled by padding.

`full35_compatibility.py` regenerates the resulting 235 templates directly
from the two earlier 34-edge graphs and 130 retained full 35-edge graphs.
It checks their pinned source identities and basic graph parameters;
no archived C table or 52-edge classification is used.

For each template, an exhaustive injection into the residual vertices
must respect every known edge, every forbidden edge, and all degree bounds.
Vertices forced to be nonisolated must be used; unused vertices can then
be isolates. Degree, triangle-count and four-cycle-count intervals only
remove impossible candidate images. The search rejects a terminal only
when every template is incompatible. Reaching its node limit raises an
error and cannot prove exclusion. All 151 required terminals completed;
the largest search visited 15,863 nodes.

## Ordinary branch terminals

Twenty-one deductions use small ordinary branch certificates. After the
checked quartic projections, each certificate starts from exactly the
proved known edges, deliberately allowing any forgotten forbidden edges.
The enclosing checker verifies this interval containment and the exact
root before replaying the certificate. Only original formats v1–v4 are
accepted here. Their known rules, exhaustive neighborhood branches and
numerical traces retain their previous meanings.

The largest two of these certificates have 19,169 and 18,525 nodes. All
are embedded as ordinary JSON certificate objects in the theory file;
no executable producer or stored verification report is required.

## Scope and dependencies

The result is relative to the minimum-order counterexample reduction,
earlier edge minima, the explicitly cited full 34/35 classifications,
and the separately proved quartic and marked-residue ingredients above.
Their source-only and stored checks remain separately reproducible.

The conclusion removes P4 from every square-incidence graph. It leaves
four nonempty square-incidence types—one edge, two adjacent edges, two
disjoint edges, and a three-edge star—for the subsequent square work.
The girth-at-least-five case remains a separate proof component.
