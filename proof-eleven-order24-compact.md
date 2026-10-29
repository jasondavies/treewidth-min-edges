# Complete compact exclusion of order 24

Every one of the 364 necessary order-24 incidence profiles is excluded by
independently checkable proof components. The aggregate first checks the
short recipes, then replays branch proofs only for roots not already
excluded. It checks catalogue coverage once and requires the checked
components to cover the exact reconstructed catalogue:

```sh
python3 scripts/verify_order24_compact.py
```

A complete serial replay took 624.33 seconds (about 10.4 minutes) on the
development machine. All recorded source and input hashes were unchanged.
The earlier full-body replay took 1,609.38 seconds (about 26.8 minutes).
The improvement comes mainly from the short 35-edge reduction for profile
69, which replaces the largest branch proof.

The short components prove 42 roots. The command still reads every stored
branch-certificate header, checks its exact catalogue root, rejects
within-component duplicates, and checks the container's end. It omits a
body only after a short proof has independently excluded that same root.
Skipped bodies contribute no new coverage. To replay the redundant bodies
as well, use `--replay-redundant`.

The optional `--native` flag enables `-march=native` only in the untrusted
C order proposers. Every returned elimination order is checked separately.

| Component, in checking order | Profiles proved | Newly covered |
|---|---:|---:|
| 28-edge smoothing recipes | 13 | 13 |
| 29-edge smoothing recipes | 2 | 2 |
| 34-edge smoothing recipe | 1 | 1 |
| 35-edge smoothing recipes | 29 | 21 |
| 20-vertex residue recipes | 9 | 5 |
| Ordinary branch bodies replayed | 320 | 320 |
| Marked-residue branch bodies replayed | 2 | 2 |
| Union | | 364 |

The stored ordinary bundle contains 346 root proofs and the separate
marked files contain three. Of these 349 bodies, 322 are replayed and 27
are already covered by checked short proofs. Overlap between independently
checked components is harmless. The displayed counts are diagnostic;
success depends on exact catalogue coverage, not on this table.

The catalogue, stored branch certificates and short recipes occupy
2,290,964 bytes. The unchanged ordinary certificate bundle accounts for
1,869,320 bytes. No archived order-24 search transcript is a proof input.

## Mathematical premises

This is an exclusion of minimum-order, 52-edge counterexamples with 24
vertices. It uses the written [minimum-counterexample reduction](proof-eleven.md)
and earlier treewidth edge minima. The smoothing and residue arguments also
use the complete earlier 28-, 29-, 34-, 35-, and specified 36-edge
classifications, with their exact scopes recorded in the linked proofs.
Their completeness is an explicit premise, not something the short command
silently assumes from a saved count.

The new finite ingredients are the [two-K4 incidence lemma](proof-eleven-two-k4-incidence.md),
the [marked 42-edge residue theorem](proof-eleven-marked-residue.md), and the
[complete nonadjacent-pair reconstructions of its exception](proof-eleven-exceptional-nonadjacent-pair.md).
They can all be regenerated before checking the root proofs:

```sh
python3 scripts/verify_order24_compact.py --check-premises
```

Equivalently, run their individual checks:

```sh
python3 scripts/verify_two_k4_incidence.py
python3 scripts/verify_marked_residue_reconstructions.py
python3 scripts/verify_exceptional_nonadjacent_pair.py --native
```

The aggregate's premise mode uses portable C proposers by default and
independent Python order/isomorphism checks. It does not require the H23
lift computation. The [20-vertex residue check](proof-eleven-order24-twenty-residue.md)
regenerates all its intermediate candidates on every aggregate run.

The [marked projection](proof-eleven-marked-projection.md) supplies the
three additional branch proofs. Profile 88 has the short
[34-edge smoothing argument](proof-eleven-order24-smoothing34.md). The
[35-edge smoothing argument](proof-eleven-order24-smoothing35.md) supplies
29 recipes, including the replacement for profile 69.

This establishes the complete order-24 component. Other vertex counts and
the remaining quartic cases still require their own proofs; the command
does not claim to establish the full 52-edge exclusion.
