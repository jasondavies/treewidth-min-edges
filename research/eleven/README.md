# Retained enumeration inputs

This directory contains only the historical inputs needed by the selected
[treewidth-eleven verification route](../../verification-eleven.md), plus the
small original result records. It is not the complete research workspace.

- `scripts/`: original source files needed to generate or audit the two
  remaining quartic enumeration cases, including files bound into archived
  manifests. Keep these bytes unchanged: replay checks their original hashes.
- `sources/treewidth-eleven-quartic-complete-checkpoints.tar.gz`: the required
  45.4 MB archive of five square-search stages, frontiers, sources and binaries.
- `sources/*results.json` and `*audit.json`: original computational records.
  References in historical records can name material kept in the separate
  research backup; they are provenance, not the current dependency inventory.
- `SHA256.json`: the selected files and their original SHA-256 hashes.

The current proof is in [proof-eleven.md](../../proof-eleven.md) and
[proof-eleven-enumeration.md](../../proof-eleven-enumeration.md).
The original sources can contain historical comments and unused entry points;
only the route documented in the verification guide is packaged here.

The superseded order-25 archive and other experiments are preserved separately,
not required for checking this publication. A hash check establishes integrity;
it does not replace mathematical review or rerunning the enumerations.
