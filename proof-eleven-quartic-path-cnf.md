# Independently reconstructing the square-path SAT encoding

This describes the logical encoding used by the stored square-path proof.
It does not by itself exclude the graph family: every additional graph-theory
clause and the propositional contradiction must also be checked.

[quartic_path_cnf.py](scripts/quartic_path_cnf.py) reconstructs the logical
clauses using only Python's standard library. It reproduces all 187,599
logical clauses and the 38,961 variable numbers of the archived formula.
The historical program then appended 128 graph-theory units. These are
excluded from the reconstruction. Thirteen of them occur in the sliced
propositional proof and remain separate graph-theory obligations.

## Why every counterexample gives a satisfying assignment

The first 325 variables are the edges of a simple graph on 26 labelled
vertices, ordered lexicographically by their endpoint pairs. The root fixes
the complete neighborhoods of vertices zero through four. All other
variables are auxiliary Boolean variables. It suffices to show that every
graph satisfying the stated necessary conditions has an extension to these
variables satisfying all clauses. No completeness property of the SAT
solver or of a graph generator is needed for this implication.

For a cardinality constraint on literals x[0],...,x[n-1] with upper bound t,
the sequential counter uses variables s[k,j]. Set s[k,j] to true exactly
when at least k+1 of x[0],...,x[j+k] are true. The clauses propagate this
threshold when the prefix grows, or when another true literal is added.
The final clauses forbid a true next literal after threshold t. Thus this
explicit assignment satisfies the counter whenever at most t inputs are
true. The variable order matches the staggered counter used by
[PySAT](https://github.com/pysathq/pysat/blob/master/cardenc/seqcounter.hh),
but the verifier has no PySAT dependency.

At each vertex, the encoding requires at most four incident edges and at
most 21 absent incident edges. These two inequalities give degree exactly
four. The tests check the constructive auxiliary assignment for all 12,650
degree-four patterns and all 2,626 patterns with at most three true inputs
used by the square-count constraint. They also check the counter for small
sizes and signed inputs. These tests supplement the threshold argument.

For each vertex pair u,v, AND gates encode each possible common neighbor.
A chain of AND and OR gates records whether the processed vertices contain
at least one or at least two common neighbors. Clauses forbid a third.
Consequently the final two-neighbor flag is true exactly when the pair has
two common neighbors. Triangle clauses separately exclude all triangles.

Under the bound of two common neighbors, each true two-neighbor flag for
v corresponds to exactly one square through v, with the other vertex as
its opposite corner. Bounding the sum of these flags by three therefore
bounds the number of squares through v. Further clauses forbid three
neighbors of v whose pairwise two-neighbor flags are all true. They express
the proved exclusion of a triangle in the square-incidence graph at v.
The relevant graph-theory premises must precede this SAT component in the
overall proof.

## Symmetry constraints

The encoding compares the list of unspecified edge variables with the same
list after swapping two vertices whose fixed-root neighborhoods are equal.
Each such transposition preserves the entire fixed root. Choose a graph
labeling whose edge list is lexicographically least under the group generated
by these transpositions. Its list is no larger than its image under any of
the chosen transpositions, so it satisfies every comparison simultaneously.

In the comparison gadget, `previous` means that all earlier compared bits
were equal. For the next two bits a,b, the clauses impose
`previous => a <= b` and
`following <=> previous and (a == b)`.
Assigning these meanings to the comparison auxiliaries satisfies their
clauses. Equal variables are skipped, which does not change the comparison.
Thus the symmetry constraints retain at least one labeling of every graph
in the rooted family.

## Additional clauses and propositional verification

A clause's occurrence in an archived CNF file is not its justification.
The enclosing checker must match each supplied initial clause to the
reconstructed logical clauses, or independently prove its graph-theory
content. This includes retained units appended during root propagation.
For a graph-theory clause, its falsification fixes present and absent
edges; a checked reduction must rule out that entire partial graph family.
No additional assumptions from the historical search log may be used.

The sliced proof then supplies reverse-unit-propagation steps. To verify
a proposed clause, negate all its literals and follow its supplied hints
to previously checked clauses. Every effective hint must force one literal
or exhibit a contradiction. Deriving a contradiction establishes the new
clause. Reaching the empty clause proves inconsistency of the justified
initial clauses. The proof-generating SAT solver is not part of this
acceptance check.
