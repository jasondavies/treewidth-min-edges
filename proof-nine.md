# Treewidth nine needs exactly 42 edges

Let $f(k)$ be the minimum number of edges in a finite simple undirected
graph of treewidth $k$. The computer-assisted result is

\[
\boxed{f(9)=42.}
\]

The proof has two parts: a 42-edge graph with independently checkable
certificates, and an exhaustive exclusion of graphs with at most 41 edges.
The saved outputs and reproduction scripts are included; the result has
not yet been externally reviewed.

## Upper bound: 42 edges suffice

The [witness](sources/witness42.g6) is a 4-regular, 21-vertex graph of girth
five. Its graph6 encoding is

```text
T???C@?GC_B_S_AICS_b_PEAcACS_BQ??F@?
```

[Its certificate](sources/witness42.json) contains a width-nine elimination
order and a closed set of **115,440** eliminated-vertex sets feasible at
width eight. The set contains the empty prefix, is closed under every
width-eight elimination step, and excludes the full vertex set. Therefore
no width-eight order exists. The verifier checks closure by explicitly
filling eliminated vertices, independently of the path-based construction
of the states. This proves treewidth exactly nine.

```sh
python3 scripts/nine/check_treewidth_nine_witness.py
python3 scripts/draw_witness42.py
```

Both commands use only Python's standard library. The drawing retains the
certificate's vertex labels in SVG element IDs and checks its edge set.
It is a display of this witness, not a claim of uniqueness at 42 edges.

## Dependencies and reduction

The [base proof](proof.md) establishes $f(8)=34$ and classifies:

* connected graphs with at most 28 edges and treewidth at least seven:
  precisely $K_8$ and the 12-vertex graph $F$;
* connected 34-edge graphs of treewidth at least eight: precisely the two
  triangle-free graphs on 16 and 17 vertices shown in the README.

If a counterexample to an edge bound exists, take one with the fewest
vertices. It is connected. Eliminating a vertex of degree at most three
never increases the edge count and preserves treewidth at least nine,
so its minimum degree is four. Deleting any vertex preserves treewidth
at least eight, so at $m$ edges its maximum degree is at most $m-34$.
In particular $m\ge38$.

A residue of minimum degree three with 28–31 edges and treewidth at least
seven, or with 34–36 edges and treewidth at least eight, is connected:
a component of the required treewidth consumes at least 28 or 34 edges,
whereas another component of minimum degree three would need at least six.
Thus the connected classifications cover all these residues.

## At most 38 edges

The reduction forces a quartic graph on 19 vertices. Triangles contradict
$f(8)=34$ after one vertex deletion and one degree-three elimination.
Four-cycles contradict the $K_8/F$ classification after deleting opposite
vertices and smoothing common degree-two neighbors. The one remaining
quartic girth-five graph has a verified width-eight order.
[Full argument](proofs/nine-38.md).

## 39 edges

Now a minimum counterexample has exactly 39 edges and maximum degree five.
It cannot be quartic, since a quartic graph has an even number of edges.
Delete a degree-five vertex. The result has 34 edges, minimum degree three,
and treewidth at least eight, so is one of the two classified graphs.
Restore the vertex with every possible five-element neighborhood:

\[
\binom{16}{5}+\binom{17}{5}=10,556.
\]

All these extensions have verified width-eight orders. The
[high-degree checker](scripts/nine/check_high_degrees.py) reconstructs them
and verifies every order in Python. This short argument replaces the
larger search used during the original investigation.

## 40 and 41 edges

The [40-edge proof](proofs/nine-40.md) excludes a degree-six vertex using
20,384 extensions of the two 34-edge graphs. Deleting a degree-five vertex
reduces the remaining mixed-degree cases to 93 classified 35-edge residues
and 72,751 extensions. The quartic case reduces to small residue families
when a four-cycle exists, and a complete restricted GENREG enumeration
otherwise. All final graphs have width at most eight.

The [41-edge proof](proofs/nine-41.md) similarly excludes degrees seven
and six, then reduces every remaining graph to one of **53,898** classified
36-edge residues. All **22,489,604** degree-five extensions have verified
width-eight orders. Together these exclusions prove $f(9)\ge42$.

## Small residue classifications

The classifications use the following general method. Eliminate a
vertex of degree three. If its neighborhood contains $t$ edges, the edge
count decreases by $t$. Reverse this operation by replacing a triangle
with a new degree-three star and keeping $t$ of the triangle's edges.
When $t=0$, this preserves the edge count. Start from every possible
minimum-degree-four core or lower-edge residue and close under these
moves. Discard a graph only after verifying an elimination order below
the required treewidth. Isomorphic duplicates are removed with nauty.

For **21 edges and treewidth at least six**, the only minimum-degree-three
residue is $K_7$. The Joret–Wood bound in the base proof gives $f(6)=21$;
therefore degree-three eliminations cannot lose edges. A resulting core
has minimum degree four and maximum degree six: deleting a vertex of
degree at least seven leaves at most 14 edges and treewidth at most four,
again by that bound. Enumerating orders 7–10 gives 2,603 cores, of which
only $K_7$ survives. All its triangle-to-star moves are isomorphic and
have width at most five. The [small classifier](scripts/nine/check_treewidth21_classification.py)
checks both assertions.

For **29 edges and treewidth at least seven**, use the 124 cores retained
by the base classification. An edge-losing degree-three elimination can
only lose one edge, giving $K_8$ or $F$; invert that move and close under
edge-preserving moves. This gives 280 residues through order 15. The
only two further candidates at order 16 have width-six orders, so the
closure stops. The 30-, 31-, 35-, and 36-edge proofs explain which of
these families and inverse moves they need.

Intermediate degree bounds are necessary conditions only. With $r$ full
triangle-to-star moves left, the maximum degree can decrease by at most
$r$, total excess above a target degree cap can decrease by at most $3r$,
and each move creates a permanent degree-three vertex. These bounds
justify the filters in the classifiers; they are not heuristic omissions.

For the 31-edge core search, a further certified rule prunes a partial
induced graph on $n$ of the target $N$ vertices when it has width at most
$6-(N-n)$. Adding the missing vertices to every bag gives width at most
six for every completion. A bounded search that fails or times out never
prunes. See [implementation](scripts/nine/treewidth_core_prune.c) and
[comparison with unpruned generation](scripts/nine/audit_prefix.py).

GENREG's cover rule is also one-sided: construct a supergraph containing
every completion of a partial graph, and prune only after verifying a
sufficiently small-width order for that supergraph. Triangle and codegree
restrictions are used only in the subcases where the proof establishes
them. An exact-key cache checks all adjacency masks before reusing a cover.

## Reproduction

Use Python 3.10 or newer without `-O`, a C compiler, `pkg-config`, and
nauty's library and `geng.c` (the recorded runs used nauty 2.8.8).
On Debian/Ubuntu the nauty development package supplies the default
`/usr/share/nauty/geng.c`; override `GENG_SOURCE` if necessary. `CC` selects
the compiler. The scripts use no third-party Python packages.

The complete run also needs Markus Meringer's **GENREG revision 5**:
`gendef.h`, `genreg.c`, `main.c`, and `optmid.c`, obtained separately from
[the official source repository](https://svn.code.sf.net/p/genreg/code/trunk/).
The builder checks its patches and records upstream source hashes. It does
not download or redistribute the upstream code.

**Check the saved final families and witness:**

```sh
python3 scripts/reproduce_nine.py --output /tmp/treewidth-nine-check --workers 16
```

This rebuilds all the final extensions in Python and verifies every order,
including all 22,489,604 at 41 edges. It is a substantial check, not an
instant smoke test. It **does not** establish the completeness of the
saved residue families or rerun the graph enumerations.

**Regenerate everything, including the 28/34-edge prerequisites:**

```sh
python3 scripts/reproduce_nine.py --full \
  --genreg-source /path/to/genreg \
  --output /tmp/treewidth-nine-full --workers 16
```

This runs the existing base reproductions, rebuilds all subsequent residue
families from freshly generated cores, reruns the generator audits and
quartic enumerations, and performs the independent final extension checks.
It uses no files from the original research workspace. The 30-edge search
alone checks 2,664,344,484 cores; the 31-edge reconstruction retains over
4.5 million graphs. Allow substantial runtime and several gigabytes of
working space. The number of workers controls multicore generation and
parallel extension checks; some Python classification stages are serial.

The output directory must be outside this checkout. The driver copies the
scripts and reference data there, leaves this checkout unchanged, and
records fingerprints of its inputs. Completed stages and generator
partitions are reused on restart. A timed-out partition is restarted,
with a longer allowance on the next round. Source or option changes
require a fresh output directory. Only completed partitions count toward
a completed classification; a partial search cannot produce a full pass.

The [saved reports](sources/nine/README.md) distinguish original run
provenance from newly generated reports. Counts of covered branches in
pruned searches are not counts of nonisomorphic graphs. The proof trusts
the completeness of nauty/GENREG enumeration and the stated mathematical
reductions; positive width certificates are independently verified.
