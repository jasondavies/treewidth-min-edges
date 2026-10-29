# Treewidth eleven requires exactly 53 edges

Among finite simple undirected graphs, the minimum number of edges at
**treewidth eleven is 53**. The lower bound excludes treewidth at least
eleven with at most 52 edges; a certified 24-vertex graph attains the bound.
This is a computer-assisted result, dependent on the earlier classifications
for treewidth eight, nine, and ten. It has not been externally reviewed.

## 1. Reducing the lower bound to six vertex counts

The [treewidth-ten result](proof-ten.md) says that treewidth at least ten
requires 47 edges. Suppose a graph of treewidth at least eleven has at most
51 edges, and choose such a graph with the fewest vertices. Eliminating a
vertex of degree at most three cannot increase the edge count and preserves
treewidth above three. Thus the graph has minimum degree at least four.
Deleting any vertex leaves treewidth at least ten, so at least 47 edges.
Every degree is therefore at most four, and the graph must have exactly 51
edges. But a 4-regular graph has an even number of edges. This rules out
all graphs with at most 51 edges.

For a minimum-order counterexample with 52 edges, the same argument gives
minimum degree four and maximum degree five. If it has $n$ vertices, then
$4n\le104\le5n$, so $21\le n\le26$. Exactly $104-4n$ vertices have degree five.
The remaining exclusions are:

| Vertices | Degree-five vertices | Exclusion |
| ---: | ---: | --- |
| 21 | 20 | The lone degree-four vertex has a clique neighborhood; eliminate it. |
| 22 | 16 | A boundary-clique argument. |
| 23 | 12 | 231 checked family proofs, four refinements, and a counting argument. |
| 24 | 8 | All 364 profiles of edges incident to degree-five vertices. |
| 25 | 4 | All 40 profiles, including the private-cycle and claw cases. |
| 26 | 0 | Completed quartic exclusion, using triangle, girth, and square reductions. |

These are reductions for a **minimum-order counterexample**, not unconditional
classifications of every 52-edge graph. The arguments follow below.

## 2. A shorter proof using the completed reductions

The proof can be organized around structural statements, with certificates
checking the finite cases needed by those statements. The history of how
those certificates were found is not part of the argument.

### Orders 21–25

For order 21, all four neighbors of the unique degree-four vertex are
high vertices (of degree five). Any two must be adjacent: otherwise deleting
them leaves 42 edges and treewidth at least nine, but the low vertex now has
degree two. Suppressing it leaves at most 41 edges without lowering treewidth
below nine, contradicting $f(9)=42$. Its neighborhood is therefore a clique.
Eliminating this simplicial vertex preserves treewidth at least eleven and
reduces the graph, contradicting minimum order. Order 22 is excluded by the
[boundary-clique argument](proof-eleven-order22.md).

At order 23, the [checked family proofs and anchor argument](proof-eleven-order23-anchor-finish.md)
establish two facts about a hypothetical counterexample:

1. Every one of its twelve high vertices has a low neighbor.
2. Each of its eleven low vertices has at most one high neighbor.

Counting high–low edges gives both at least twelve and at most eleven,
a contradiction. The certificates are needed to establish these facts;
the counting argument alone is not an unconditional degree-sequence theorem.
This avoids separately excluding the 33 residual catalogue families.

At order 24, [short reductions to earlier small-edge classifications](proof-eleven-order24-compact.md)
exclude 42 of the 364 necessary profiles. Checked branch proofs exclude the
other 322. The coverage checker verifies that their union is exactly the
complete catalogue. This replaces the original search transcript, although
it remains a computational case analysis.

At order 25, [cubic-neighbor restrictions](proof-eleven-cubic-neighbor-cap.md)
and their extensions support 38 stored profile proofs. The private-cycle
count and [claw reduction](proof-eleven-order25-claw.md) exclude the last two
profiles. The [combined checker](scripts/verify_order25_complete.py) verifies
coverage of all forty. The old sequence of completion searches and separate
four-cycle/paw core constructions is not needed on this route.

### Order 26: two computational cases after the local reductions

The graph is quartic. The [triangle certificate](proof-eleven-triangle-certificates.md)
excludes a triangle by covering and refuting all nine necessary local families.
There are then two possibilities: girth at least five, or a square.

The girth-at-least-five case uses the [complete GENREG enumeration](proof-eleven-enumeration.md#girth-at-least-five).
No short replacement for that entire case is asserted here.

For the square case, associate to each vertex $v$ a graph $J_v$ on its four
neighbors: two neighbors are adjacent in $J_v$ when they have a common
neighbor other than $v$. Its edges correspond to squares through $v$.
The necessary restrictions follow from:

1. The [square-cap argument](proof-eleven-quartic-square-cap.md), which bounds
   common-neighbor counts by two and square incidence by four.
2. The [square-direction argument](proof-eleven-quartic-square-directions.md),
   which excludes triangular incidence and supplies the marked-residue
   restrictions. Its finite premise includes all 983 exceptional quartic
   reconstructions.
3. The 156-byte four-square certificate, which excludes the remaining
   four-edge type, a four-cycle. Thus $J_v$ has at most three edges.

Choose a vertex on the maximum number of squares. There are five possible
nonempty incidence types: an edge, two adjacent edges, two disjoint edges,
a three-edge star, and a four-vertex path. The root-coverage checker matches
all five to the archived completion roots. The
[completion enumeration](proof-eleven-enumeration.md#square-families) excludes
them all. Its later stages also use the independently checked
[path exclusion](proof-eleven-quartic-path-certificate.md) globally.
The maximum square incidence at the chosen root is an explicit hypothesis
of these searches.

### Shared premises and verification

All these arguments use the minimum-counterexample reduction and earlier
edge minima. Several also require the complete earlier 28-, 29-, 34-,
35-, and specified 36-edge classifications. The full runner regenerates
these through `reproduce_ten.py --full`; checking only the stored graph
families would not establish their completeness.

The [verification guide](verification-eleven.md) gives the command,
dependency order, and remaining trusted mathematical and software components.

## 3. A graph attaining the bound

The illustrated witness has 24 vertices, 53 edges, and
[graph6 encoding](sources/witness53.g6)

```text
W?dkC@?G?`AAO_GOOE?_FOP?aGG?c?@ACAC@?Q?gG@``?@w
```

The [SVG drawing](sources/witness53.svg) is generated by
`scripts/draw_witness53.py` using only the Python standard library. Its twelve
vertex pairs and two curved edges respect reflection in the vertical axis.
Blue vertices have degree five and white vertices have degree four.

Its [certificate](sources/witness53.twcert.xz) contains a width-eleven
elimination order and 675,532 closed states excluding every width-ten order.
The closed set is stored as a compressed bitset; the entire certificate is
26,256 bytes. Its [standalone verifier](scripts/verify_treewidth_certificate.py)
uses neither the search program nor the archived reports.
Verify this graph alone with:

```sh
python3 scripts/verify_witness53.py
```

The lower-bound proof establishes the global edge minimum; no uniqueness
claim is made.

## 4. Verification and reproduction

For the pictured witness alone, run `python3 scripts/verify_witness53.py`.
For the complete selected computational route, including the earlier
classifications, see [verification-eleven.md](verification-eleven.md).
It provides one resumable command and a log for every stage.

A quick integrity and witness check is also available:

```sh
python3 scripts/reproduce_eleven.py
```

**It does not verify the complete 52-edge exclusion.** Use Python without
`-O`: some verification steps use assertions. Hashes establish integrity,
not mathematical correctness. The written reductions and enumeration
software remain proof dependencies; this is not a proof-assistant proof.
