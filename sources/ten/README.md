# Treewidth-ten reference data

These are the completed reference outputs for [f(10)=47](../../proof-ten.md).
The previous classifications are reused from `sources/nine`.

| File | Result |
|---|---|
| `treewidth46-four-cycles.json` | All 969,011 four-cycle reconstructions have width-nine orders |
| `treewidth46-four-cycle-audit.json` | Independent Python reconstruction and verification of every one |
| `treewidth46-girth5.g6` | All 3,917 connected quartic girth-five graphs on 23 vertices |
| `treewidth46-girth5.json` | Width-nine orders verified for every graph in that list |
| `treewidth-ten-results.json` | Aggregate result, construction of the witness, original artifact hashes |

The witness itself is [../witness47.g6](../witness47.g6), with a
[reproducible SVG drawing](../witness47.svg). Its compressed
[certificate](../witness47.json.gz) contains a width-ten order and 410,333
closed width-nine elimination states. The small
[summary](../witness47-summary.json) omits those states.

Original reports retain their research-workspace paths and source hashes
as provenance, not runtime dependencies. The aggregate report's artifact
names refer to the original layout: the three prerequisite residue lists
now live in `sources/nine`, the 46-edge reports here, and the witness
certificate at `sources/witness47.json.gz`. The packaged scripts have new
paths and share the repository's existing helpers. A new reproduction
records its own inputs and results in the selected output directory.

`package-manifest.json` records repository-relative hashes for the packaged
addition and its shared code dependencies. It is an integrity record,
not a substitute for checking the mathematical proof and certificates.
