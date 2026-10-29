# Nonadjacent-high reconstructions of the exceptional marked residue

**Complete:** all 3,732,129 reconstructions have independently checked
width-ten orders. The full source-only replay took 260 seconds on one CPU
on the validation machine. Every graph was resolved using a single-vertex
prefix; the bounded two-prefix fallback remains available.

Let H be the fixed 22-vertex, 42-edge exception from
[the marked-residue theorem](proof-eleven-marked-residue.md). It has four
cubic vertices C and eighteen quartic vertices Q. Its graph6 identity is
shared by the checkers through `scripts/marked_residue_common.py`:

```text
UqGOOICQ@GB?Oo_oCG?c@?E??c?@?o?`G?IC?@Q?
```

Consider any simple graph G obtained by adding two **nonadjacent** vertices
x,y to H, such that x,y have degree five and G has eight degree-five and
sixteen degree-four vertices. The finite check below establishes that every
such G has treewidth at most ten. It does not assume that the cubic
attachments split evenly, or that x,y have no common neighbor.

This is a reconstruction lemma for the fixed exception. Applying it to an
arbitrary graph first requires the separate marked-residue theorem and its
marking hypotheses. No claim that every 22-vertex, 42-edge residue is this
exception is used here.

## Every attachment pattern

Each cubic of H must be adjacent to at least one of x,y, so that its final
degree is four or five. A quartic of H is adjacent to at most one of them.
Let t be the number of cubics adjacent to both x,y; thus 0 <= t <= 4.
Choose these t shared cubics. Among the other 4-t cubics, choose a to
attach to x; the remaining 4-t-a attach to y. The numbers of quartics
attached to x and y are then forced by their degree-five requirements:

    q_x = 5-t-a,       q_y = 1+a.

Choose disjoint subsets of Q of those sizes. This exhausts every possible
G: all edges within H are fixed, the edge xy is absent, and the listed
attachments determine all remaining edges. It also gives the required
number of highs automatically: x,y, the t shared cubics, and the 6-t
attached quartics make eight degree-five vertices.

Swapping x and y preserves the graph up to relabeling. If t<4, the checker
requires the first nonshared cubic to attach to x. Every orbit under the
swap has exactly one such orientation. If t=4, x and y each attach to one
quartic, and these quartics are distinct; the smaller quartic label is
assigned to x. This again chooses exactly one orientation. No further
symmetry pruning is used.

For fixed t the resulting count is

    (1/2) * binom(4,t) * sum_{a=0}^{4-t}
        binom(4-t,a) * binom(18,5-t-a) * binom(13+t+a,1+a).

The division by two has no fixed points: both added vertices have at least
one quartic neighbor, and those quartic neighbor sets are disjoint. The
counts are:

| Shared cubics t | Reconstructions |
|---:|---:|
| 0 | 2,339,064 |
| 1 | 1,199,520 |
| 2 | 183,600 |
| 3 | 9,792 |
| 4 | 153 |
| Total | 3,732,129 |

The previously considered balanced, private case (t=0,a=2) accounts for
only 1,113,840 of these graphs. The broader check includes the other splits
and all shared-cubic cases.

## Independent verification

The Python checker constructs every graph and independently verifies that
it is simple and undirected, has 52 edges and degree sequence 4^16,5^8,
that x,y are nonadjacent degree-five vertices, and that deleting x,y
restores exactly H.

It then asks a bounded order finder for a width-ten elimination order.
The existing order finder uses 26 vertices, so the input is padded with
two isolated vertices. The checker first requires a complete permutation
of all 26 vertices, then removes both dummy vertices and independently
recomputes every fill edge on the original 24-vertex graph using sets.
A malformed permutation, a fill step of degree greater than ten, or failure
to find an order stops the verification with an error.

The finder tries each single-vertex prefix and then each ordered pair of
distinct vertices, followed by deterministic greedy min-fill elimination.
This bounded search is used only to propose an upper-bound order. It never
certifies a lower bound or treats an exhausted search as success. The
optional C implementation is untrusted; the same Python checker validates
its output.

## Reproduction

No saved enumeration, order data, or archive checkpoint is required:

```sh
python3 scripts/verify_exceptional_nonadjacent_pair.py --native
```

Without `--native`, the same bounded proposal policy runs in Python. The
native option uses portable `-O3` compilation through the existing helper;
`--cc 'cc -march=native'` optionally enables machine-specific optimization.
The standard-library tests independently compare the attachment
normalization against unrestricted subset pairs in a smaller domain and
exercise invalid padded orders, a valid permutation of excessive width,
and complete exhaustion of the bounded proposal policy.

The complete ordered adjacency stream, encoded as 24 little-endian
32-bit masks per graph, has SHA256

    8754fee454677219d4ff109218543475b1d6cfe1c5871b8688631ba214ffa94c

This digest records the checked stream; it is not a substitute for exhaustive
enumeration or independent order verification.

## Consequence for marked residues in order 24

Suppose a 24-vertex, 52-edge hypothetical graph of treewidth at least eleven
has eight highs of degree five and sixteen lows of degree four. Delete two
nonadjacent highs. If the residual graph satisfies the marked-residue
hypotheses, deletion leaves exactly 42 edges and treewidth at least nine,
so that theorem identifies the residue with H. Transporting labels through
the resulting isomorphism gives one of the constructions enumerated above.
Its checked width-ten order contradicts the original treewidth bound.
Thus no such marked residue can arise from that high-pair deletion.
