"""Reproduce the complete computer-assisted resolution of a3nm-021.

Needs a C compiler, pkg-config, and nauty development files, including geng.c.
Debian paths are the defaults; override GENG_SOURCE or CC if needed.
No network access. Run from any working directory. Typical runtime: under a minute.
"""
import hashlib
import json
import os
from pathlib import Path
import random
import re
import shlex
import subprocess
from tempfile import TemporaryDirectory

from factor_matching import verify_width_lower, width_reachable
from graph_research import graph, treewidth

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts/treewidth_edge_geng.c"
GENG = Path(os.environ.get("GENG_SOURCE", "/usr/share/nauty/geng.c"))
CC = shlex.split(os.environ.get("CC", "cc"))
EXPECTED = {9: 29, 10: 50038, 11: 3837691, 12: 12543045, 13: 1094992}


def run(args, **kwargs):
    return subprocess.run([str(x) for x in args], check=True, text=True,
                          capture_output=True, **kwargs)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decode(s):
    n = ord(s[0]) - 63
    assert 1 <= n <= 14
    a = [set() for _ in range(n)]
    bit = 0
    for j in range(1, n):
        for i in range(j):
            if (ord(s[1 + bit // 6]) - 63) >> (5 - bit % 6) & 1:
                a[i].add(j)
                a[j].add(i)
            bit += 1
    return a


def encode(a):
    bits = [int(j in a[i]) for j in range(1, len(a)) for i in range(j)]
    bits += [0] * ((-len(bits)) % 6)
    return chr(len(a) + 63) + "".join(
        chr(63 + sum(bits[i + j] << (5 - j) for j in range(6)))
        for i in range(0, len(bits), 6))


def masks(a):
    return tuple(sum(1 << w for w in ns) for ns in a)


def verify_order(a, order, bound):
    """Set-based fill verifier, independent of the C path-based verifier."""
    assert sorted(order) == list(range(len(a)))
    current = [set(ns) for ns in a]
    remaining = set(range(len(a)))
    width = 0
    for v in order:
        ns = current[v] & remaining
        width = max(width, len(ns))
        assert len(ns) <= bound
        for w in ns:
            current[w].update(ns - {w})
        remaining.remove(v)
    return width


def audit(checker, geng):
    """Compare the C decision routine with an independent Python subset DP."""
    cases = []
    for n in range(1, 8):
        cases.extend(decode(s) for s in run([geng, "-q", n]).stdout.splitlines())
    exhaustive = len(cases)
    rng = random.Random(210025)
    for n in range(8, 12):
        for _ in range(12):
            probability = rng.random()
            cases.append([set() for _ in range(n)])
            a = cases[-1]
            for j in range(1, n):
                for i in range(j):
                    if rng.random() < probability:
                        a[i].add(j)
                        a[j].add(i)
    grouped = {}
    for a in cases:
        w = treewidth(masks(a))
        for bound in (w - 1, w):
            grouped.setdefault(bound, []).append((a, w <= bound))
    comparisons = 0
    for bound, group in sorted(grouped.items()):
        output = run([checker, bound], input="".join(encode(a) + "\n" for a, _ in group))
        lines = output.stdout.splitlines()
        assert len(lines) == len(group)
        for (a, expected), line in zip(group, lines):
            fields = line.split()
            assert (fields[0] == "YES") == expected
            if expected:
                verify_order(a, list(map(int, fields[1:])), bound)
            else:
                assert fields == ["NO"]
            comparisons += 1
    return {"all_unlabeled_graphs_n1_through7": exhaustive,
            "seeded_random_graphs_n8_through11": len(cases) - exhaustive,
            "decision_comparisons": comparisons}


def main():
    flags = shlex.split(run(["pkg-config", "--cflags", "--libs", "nauty"]).stdout)
    out = {"date": "2026-10-25", "answer": 8,
           "geng_source_sha256": digest(GENG), "checker_source_sha256": digest(SOURCE),
           "nauty_version": run(["pkg-config", "--modversion", "nauty"]).stdout.strip(),
           "compiler": run(CC + ["--version"]).stdout.splitlines()[0],
           "enumeration_arguments": "-c -d4 -D6 n 26:27, for every n=9,...,13",
           "enumeration": []}
    hard_cases = []
    with TemporaryDirectory(prefix="treewidth-edge-") as tmp:
        tmp = Path(tmp)
        geng, plugin, checker = (tmp / name for name in ("geng", "geng-tw", "checker"))
        run(CC + ["-O3", GENG, *flags, "-o", geng])
        run(CC + ["-O3", "-DOUTPROC=tw_out", "-DSUMMARY=tw_summary",
                  GENG, SOURCE, *flags, "-o", plugin])
        run(CC + ["-O2", "-Wall", "-Wextra", "-DSTANDALONE", SOURCE, "-o", checker])
        out["checker_audit"] = audit(checker, geng)
        print("Independent checker audit passed:", out["checker_audit"], flush=True)
        for n, expected in EXPECTED.items():
            args = ["-c", "-d4", "-D6", n, "26:27"]
            count = run([geng, "-u", *args])
            assert int(re.search(r">Z (\d+) graphs", count.stderr)[1]) == expected
            hard = tmp / f"hard-{n}.txt"
            result = run([plugin, *args], env={**os.environ, "TW_HARD_CASES": str(hard)})
            assert not result.stdout, "Counterexample found: " + result.stdout
            line = next(s for s in result.stderr.splitlines() if s.startswith("TW_RESULT "))
            row = json.loads(line.removeprefix("TW_RESULT "))
            assert row["n"] == n
            assert row["total"] == row["verified"] == expected
            assert row["greedy"] + row["search"] == expected
            assert row["counterexamples"] == 0
            assert sum(row["edges"].values()) == expected
            out["enumeration"].append(row)
            local = 0
            for s in hard.read_text().splitlines():
                encoding, *order = s.split()
                a = decode(encoding)
                order = list(map(int, order))
                assert len(a) == n
                assert 26 <= sum(map(len, a)) // 2 <= 27
                assert all(4 <= len(ns) <= 6 for ns in a)
                verify_order(a, order, 6)
                hard_cases.append({"graph6": encoding, "width_six_order": order})
                local += 1
            assert local == row["search"]
            print(f"n={n}: {expected:,} graphs, every order verified", flush=True)

        a = graph(14, [(i, (i + d) % 14) for i in range(14) for d in (1, 4, 7)])
        lower, no_order = width_reachable(a, 7)
        assert no_order is None and verify_width_lower(a, 7, lower)
        upper = [0, 1, 3, 4, 6, 2, 5, 7, 8, 9, 10, 11, 12, 13]
        sets = [{w for w in range(14) if ns >> w & 1} for ns in a]
        assert verify_order(sets, upper, 8) == 8
        encoding = encode(sets)
        assert run([checker, 7], input=encoding + "\n").stdout.strip() == "NO"
        width_eight = run([checker, 8], input=encoding + "\n").stdout.split()
        assert width_eight[0] == "YES"
        verify_order(sets, list(map(int, width_eight[1:])), 8)
        out["upper_witness"] = {
            "graph6": encoding, "n": 14, "edges": sum(x.bit_count() for x in a) // 2,
            "steps": [1, 4, 7], "width_eight_order": upper,
            "width_seven_closed_prefixes": sorted(lower),
            "closed_prefix_count": len(lower), "closure_independently_verified": True}
        assert out["upper_witness"]["edges"] == 35

    out["total_graphs"] = sum(r["total"] for r in out["enumeration"])
    out["total_orders_verified"] = sum(r["verified"] for r in out["enumeration"])
    out["hard_cases_independently_verified_in_python"] = len(hard_cases)
    out["hard_cases"] = hard_cases
    assert out["total_graphs"] == out["total_orders_verified"] == 17525795
    dest = ROOT / "sources/treewidth-edge-results.json"
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(f"PASS: minimum k=8; results saved to {dest}", flush=True)


if __name__ == "__main__":
    main()
