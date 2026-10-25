# Smallest treewidth achieved by a graph with fewer edges than the complete graph

> A natural family of graphs to consider are the
> [cliques](https://en.wikipedia.org/wiki/Clique_(graph_theory)): a clique on
> $k+1$ vertices has treewidth $k$, and has $k (k+1) / 2$ edges. However,
> asymptotically, there are graphs of treewidth $k$ whose number of edges is
> linear rather than quadratic, e.g., cubic expanders as mentioned in
> [this question](https://cstheory.stackexchange.com/questions/39071/maximum-treewidth-of-a-graphs-with-m-edges).
> So cliques are not optimal. My question is: **what is the smallest example
> of a graph of treewidth $k$ having less edges than the $(k+1)$-clique?**
>
> — Antoine Amarilli, [TCS Stack Exchange](https://cstheory.stackexchange.com/questions/53806/what-is-the-smallest-graph-of-treewidth-k-having-less-edges-than-the-k1-c)

**The smallest treewidth $k$ at which a graph can have fewer edges than
$K_{k+1}$ is $k = 8$. The minimum number of edges at treewidth eight is 34.**

| Treewidth $k$ | Edges of $K_{k+1}$ | Minimum number of edges |
| ---: | ---: | ---: |
| 6 | 21 | 21 |
| 7 | 28 | 28 |
| 8 | 36 | **34** |

<p align="center">
  <img src="sources/witness34.svg" width="360"
       alt="A 17-vertex, 4-regular graph with 34 edges and treewidth 8">
</p>

*A 34-edge graph of treewidth eight. The 12 outer vertices form a Möbius
ladder: a 12-cycle plus its six diameters (dashed). Each of the four inner
vertices is joined to every fourth outer vertex, and the centre vertex is
joined to all four inner vertices.*

For every $k \le 7$, the clique is optimal. This repository contains the
[proof](proof.md), the code for its computer-assisted step, and the saved
certificates. The results have not yet been externally reviewed. The 34-edge
graph comes from House of Graphs' quartic archive and is not claimed as a new
construction.

## Proof outline

The key step is a classification: **every connected graph with at most 28
edges and treewidth at least seven is $K_8$ or one 12-vertex graph $F$.**

1. **The classification.** Eliminating vertices of degree at most three and
   adding a few edges turns any such graph into a connected graph with 28
   edges, 8–14 vertices, and degrees 4–7. All **96,841,893** of these have
   verified width-six elimination orders, except $K_8$ and $F$. Deleting an
   edge of either, or replacing a triangle by a star, lowers the treewidth to
   six, so the original graph was $K_8$ or $F$ all along.
2. **Treewidth seven needs 28 edges,** because $K_8$ and $F$ both have 28.
   The Joret–Wood bound handles treewidths up to six.
3. **Treewidth eight needs 34 edges.** Deleting a maximum-degree vertex from
   a smallest counterexample with at most 33 edges leaves a connected
   28-edge graph of treewidth at least seven on 13–15 vertices, which the
   classification rules out.
4. **34 edges suffice:** a 17-vertex, 4-regular graph has treewidth exactly
   eight.

### How the results are certified

An *elimination order* of width $w$ proves treewidth at most $w$, and a
*closed-prefix certificate* proves treewidth greater than $w$. Every order is
checked by a separate routine that uses paths in the original graph instead
of filling, and every saved certificate is checked in Python; see
[Section 7 of the proof](proof.md#7-how-the-computation-is-certified) for
details. The proof relies on the published Joret–Wood theorem, the
completeness of nauty's isomorphism-class generation, and the verifiers in
this repository. None of these has been formally verified in a proof
assistant.

## Reproduce everything

Requirements: Python 3.10 or later, a C compiler supporting GCC-style builtins
(GCC or Clang), `pkg-config`, and nauty development files including `geng.c`.
The checked run used nauty 2.8.8. Other versions may label the two
exceptional graphs ($K_8$ and $F$) differently from the saved encodings and
have not been tested. On Debian/Ubuntu:

```sh
sudo apt-get install python3 build-essential pkg-config libnauty2-dev nauty
```

From the repository root:

```sh
python3 scripts/reproduce.py
```

This runs the enumeration, certifies the facts about $K_8$, $F$, and the
34-edge graph, and rechecks the saved certificates. A successful run ends
with:

```text
PASS: every computational step of proof.md verified.
```

Allow a few minutes, depending on hardware. No network access, graph archive
download, or Python packages are needed. Executables and intermediate order
logs are built in a temporary directory and removed on completion. The result
file `sources/results.json` is regenerated with local timings, compiler
information, and source hashes, which may differ from the saved run.

**Do not use Python's `-O` flag:** assertions are verification steps, and the
scripts refuse to run under it. The scripts can be run from any working
directory.

The default generator source is `/usr/share/nauty/geng.c`. To use another
installation or compiler:

```sh
GENG_SOURCE=/path/to/geng.c CC=clang python3 scripts/reproduce.py
```

Nauty's headers and libraries must be discoverable through `pkg-config nauty`;
set `PKG_CONFIG_PATH` if necessary. Nauty is installed separately, not bundled.

## Faster certificate check

With only Python's standard library, run:

```sh
python3 scripts/verify_certificates.py
```

This checks source hashes, the exact treewidths of $K_8$, $F$, and the
34-edge graph, and the width-six orders for every reduction of $K_8$ and $F$.
It does **not** repeat the exhaustive enumeration; use the full run for that.

## Files

- [proof.md](proof.md): the complete proof.
- [scripts/reproduce.py](scripts/reproduce.py): full reproduction.
- [scripts/verify_certificates.py](scripts/verify_certificates.py): Python-only
  check of the saved certificates.
- [scripts/treewidth.c](scripts/treewidth.c): C search and independent order
  verifier, used as a `geng` plugin or standalone graph6 checker.
- [scripts/reference.py](scripts/reference.py): independent Python reference
  algorithms.
- [sources/results.json](sources/results.json): enumeration counts, source
  hashes, and certificates for $K_8$ and $F$ and all their reductions.
- [sources/witness34.json](sources/witness34.json),
  [graph6 file](sources/witness34.g6), and [drawing](sources/witness34.svg):
  the 34-edge graph and its certificates.

## References and attribution

- Antoine Amarilli's [original question](https://cstheory.stackexchange.com/questions/53806/what-is-the-smallest-graph-of-treewidth-k-having-less-edges-than-the-k1-c).
- Gwenaël Joret and David R. Wood, *K4-Minor-Free Induced Subgraphs of Sparse
  Connected Graphs*, SIAM Journal on Discrete Mathematics 32(1), 123–147 (2018),
  [Theorem 1.2, arXiv:1605.04730](https://arxiv.org/abs/1605.04730),
  [DOI:10.1137/16M107712X](https://doi.org/10.1137/16M107712X).
- [House of Graphs' quartic archives](https://houseofgraphs.org/meta-directory/quartic),
  specifically [17 vertices, girth at least four](https://houseofgraphs.org/data/quartics/17_4_4.g6.gz),
  supply the 34-edge graph. The archive is not needed to verify it.
- Devon's November 2025 comment on the original question supplies the earlier
  35-edge circulant example.
- [Nauty and Traces](https://pallini.di.uniroma1.it/) supply the `geng`
  generator used for exhaustive enumeration.

Original code and text are under the [MIT license](LICENSE); external
software and source material retain their own licenses.
