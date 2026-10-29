# Verifying the treewidth-eleven result

The claim is that **53 is the minimum number of edges in a finite simple
undirected graph of treewidth eleven**. There are two separate obligations:
verify a 53-edge witness, and exclude every graph with at most 52 edges.
The [proof](proof-eleven.md) explains the reduction and links its hand arguments.

The selected computational route combines finished certificates with the
existing exhaustive enumeration. Stored certificates are used where they simplify verification; the two
remaining enumeration cases retain their original code and required evidence.

## One command

Requirements: Linux x86-64 with POPCNT; Python 3.11 or later; a C compiler;
`pkg-config`; nauty development files (including `geng.c`, default
`/usr/share/nauty/geng.c`); and `bubblewrap` with working mount namespaces.
The archived square-search executables were built with GCC 13.3 and nauty
2.8.8. This route uses those binaries and their runtime libraries; other
platforms require rebuilding from the archived sources.

Obtain the unmodified GENREG revision-5 sources separately, following the
[earlier reproduction instructions](README.md). The directory passed below
must contain `gendef.h`, `genreg.c`, `main.c`, and `optmid.c`.
Run from the repository root, without Python's `-O` option:

```sh
python3 scripts/reproduce_eleven_full.py \
  --genreg-source /path/to/genreg-r5 \
  --output /tmp/treewidth-eleven-full --workers 8
```

Use a **new output directory** for independent verification. Allow several
gigabytes of working space and substantial computation time: this includes
regenerating the earlier classifications, not just checking k=11 certificates.
Budget roughly **5–7 hours on eight cores** for the full rerun. This is an
estimate from the observed stages and archived workloads, not a completed
end-to-end measurement; other machines may take longer.

Add `--plan` to print every command without running or writing anything.
After interruption, repeat the command with `--resume`. The runner rejects
changed inputs, skips successful local stages with intact logs, and resumes
supported enumeration checkpoints. A partially completed certificate stage
restarts; individual square-search replay receipts survive interruption.

`logs/` contains a separate log for each stage. `summary.json` records
progress and becomes `complete` only after every selected check succeeds.
The terminal message is `PASS: all selected computational checks completed`.
A failed stage stops the runner; a partial result is not a proof of exclusion.
Receipts and logs are local records, not certificates to accept from another
machine. An independent party should start with a new output directory.

## Dependency map

Stages run sequentially, with at most the requested worker count in a stage.
Some finite checks are single-threaded.

| Stage | What it establishes or checks |
| --- | --- |
| Earlier classifications | `reproduce_ten.py --full` regenerates the earlier minima and small graph families, including their completeness. |
| Witness | The symmetric 24-vertex, 53-edge graph has treewidth exactly eleven. |
| Order 23 | Exact family coverage, 231 stored proofs, four refinements, and the counting finish. |
| Order 24 | Coverage of all 364 profiles; also regenerates the two-K4, marked-H22, and exceptional nonadjacent-pair premises. |
| Order 25 | All 40 profiles, including the two hand reductions; also regenerates its cubic-neighbor premises. |
| Quartic triangles | All nine families and the coverage proof. |
| Quartic exception | All 983 quartic reconstructions of the marked-H22 exception. |
| Four squares and square paths | Stored certificates for the exclusions used by the square search. |
| Square roots | The five archived roots cover the regenerated rooted catalogue after the four-square exclusion. |
| Girth at least five | Fresh GENREG enumeration of 256 partitions, followed by the independent accounting audit. |
| Square searches | All five stages of archived coverage, all adaptive splits and cooperative cuts, and every adaptive and cooperative terminal search. |

At orders 21 and 22 the exclusions are written arguments, not extra search
jobs. The minimum-order reduction, square cap, square-direction lemmas,
and graph-construction arguments likewise need mathematical review.

For the square search, **maximum square incidence at the chosen root** is
an explicit hypothesis. Later stages also use the path exclusion globally.
The marked-H22 restriction replaces the earlier high-core computation with
the same necessary neighborhood condition, checked by the selected finite
reconstructions. None of these premises assumes the final 52-edge exclusion.

## What “verification” means here

The stored witness and branch proofs are checked independently of their
search programs. Native helpers used in finite reconstruction checks propose
orders that the checkers verify. The girth-five and archived square searches
remain computer-assisted enumerations: their completeness depends on the
correctness of GENREG, canonicalization, the C completion code, and the
written pruning arguments. This is not a proof-assistant certificate.

In the square-search replay, cooperative records must reproduce their exact
deterministic outputs. Adaptive terminals are rerun with their stage's
kernel and must finish with no graphs, no exported unfinished patterns,
and zero residues. Imported historical terminals may have different node
counts, so those counts are not used as the acceptance condition.

The old `--replay-terminals` option replayed only cooperative terminals.
It now includes the earlier adaptive terminals too. The narrower command
without that option still checks coverage, splits, and cuts while checking
terminal outcomes from saved records. It must not be described as a fresh
complete replay.

## Validation status

The original exhaustive computations completed. The
[original result manifest](research/eleven/sources/treewidth-eleven-results.json),
[girth-five audit](research/eleven/sources/treewidth-eleven-girth26-audit.json), and
[quartic square audit](research/eleven/sources/treewidth-eleven-quartic-complete-audit.json)
record their scope and results. They remain evidence for the computational
proof, subject to its stated mathematical and software dependencies.

The newly assembled full command was **deliberately stopped during fresh
validation**, after the following stages passed with eight workers:

| Fresh stage | Minutes | Result |
| --- | ---: | --- |
| earlier-classifications | 62.55 | passed |
| four-squares | 0.00 | passed |
| order23 | 6.82 | passed |
| order24 | 10.17 | passed |
| order25 | 3.17 | passed |
| quartic-exception | 0.00 | passed |
| square-path | 0.97 | passed |
| square-roots | 0.00 | passed |
| triangles | 0.01 | passed |
| witness | 0.09 | passed |

The girth-five rerun completed **97 of 256 partitions** before it was stopped.
The final square-search stage was not started in this run. These partial
results do not establish complete coverage. The original completed runs
supply those cases; no complete fresh end-to-end rerun is claimed.

The raw validation logs and checkpoints are preserved in the author's research
backup. They are not inputs to the published verification route.

A separate bounded archive integration check regenerated coverage accounting
and freshly replayed 243 adaptive terminals, then correctly reported an
incomplete result at its time limit. The complete ledger has 43,376 adaptive
terminals and 125,888 cooperative tasks (including cuts).

The publication has since been trimmed to the selected route. Required
mathematical checkers and certificate bytes are unchanged; the quick integrity
wrapper and archive wrapper now cover only the retained route. All 120
retained tests passed (the missing-fixture test was rerun after
restoring its fixture). The trimmed checkout also passed its integrity and
witness checks, the triangle and four-square certificates, root coverage,
and the complete archive coverage accounting. A bounded integration replay
correctly returned an incomplete status after one terminal; the GENREG
adapter compiled successfully. No additional full enumeration was run merely
to remove unused files.

## What is stored

The [enumeration inputs](research/eleven/README.md) retain the original source
bytes needed by the girth-five and square searches, the original result
records, and the 45.4 MB square-search archive. `SHA256.json` lists exactly
the retained historical inputs with their original hashes. Missing or changed
listed files fail the integrity check.

The complete order-25 certificates replace the older 75 MB checkpoint archive.
Alternative certificate generators, unfinished experiments, old witnesses,
and redundant search transcripts are not part of this checkout. Their removal
does not change the selected verification obligations or reduce the runtime
of the remaining enumerations.
