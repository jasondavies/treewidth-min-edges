"""Reproduce the computer-assisted steps of proof.md.

Classifies every connected graph with 28 edges, 8-14 vertices, and degrees
4-7 by treewidth at most six; certifies the small facts about the two
exceptions, K8 and F; and checks the 34-edge graph of treewidth eight.

Needs a C compiler, pkg-config, and nauty development files, including geng.c.
Debian paths are the defaults; override GENG_SOURCE or CC if needed.
No network access. Run from any working directory.
"""
from datetime import date
import hashlib
import json
import os
from pathlib import Path
import random
import re
import shlex
import subprocess
from tempfile import TemporaryDirectory

from reference import (decode, encode, masks, reductions, treewidth, triangles,
                       verify_order, verify_width_lower, width_reachable)
import verify_certificates

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts/treewidth.c"
GENG = Path(os.environ.get("GENG_SOURCE", "/usr/share/nauty/geng.c"))
CC = shlex.split(os.environ.get("CC", "cc"))
EXPECTED = {8: 1, 9: 106, 10: 101336, 11: 9555744,
            12: 62893242, 13: 24203296, 14: 88168}
EXCEPTIONS = {8: ["G~~~~{"], 12: ["K?bFBO{}?}Ug"]}


def run(args, **kwargs):
    return subprocess.run([str(x) for x in args], check=True, text=True,
                          capture_output=True, **kwargs)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_orders(checker, graphs, width):
    """Ask the C checker for width-`width` orders and verify them in Python."""
    output = run([checker, width], input="".join(encode(a) + "\n" for a in graphs))
    lines = output.stdout.splitlines()
    assert len(lines) == len(graphs)
    orders = []
    for a, line in zip(graphs, lines):
        fields = line.split()
        if fields == ["NO"]:
            orders.append(None)
        else:
            assert fields[0] == "YES"
            orders.append(list(map(int, fields[1:])))
            verify_order(a, orders[-1], width)
    return orders


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
        orders = check_orders(checker, [a for a, _ in group], bound)
        for (_, expected), order in zip(group, orders):
            assert (order is not None) == expected
            comparisons += 1
    return {"all_unlabeled_graphs_n1_through7": exhaustive,
            "seeded_random_graphs_n8_through11": len(cases) - exhaustive,
            "decision_comparisons": comparisons}


def classify(geng, plugin, tmp):
    """Every core has a verified width-six order, except K8 and F."""
    rows = []
    for n, expected in EXPECTED.items():
        args = ["-c", "-d4", "-D7", n, "28:28"]
        hard = tmp / f"hard-{n}.txt"
        result = run([plugin, *args], env={**os.environ, "TW_HARD_CASES": str(hard)})
        line = next(s for s in result.stderr.splitlines() if s.startswith("TW_RESULT "))
        row = json.loads(line.removeprefix("TW_RESULT "))
        found = result.stdout.splitlines()
        assert found == EXCEPTIONS.get(n, [])
        assert row["n"] == n and row["total"] == expected
        assert row["verified"] == expected - len(found)
        assert row["counterexamples"] == len(found)
        assert row["greedy"] + row["search"] == row["verified"]
        nongreedy = 0
        for record in hard.read_text().splitlines():
            encoding, *order = record.split()
            a = decode(encoding)
            assert len(a) == n and sum(map(len, a)) == 56
            assert all(4 <= len(ns) <= 7 for ns in a)
            if order == ["NO"]:
                assert encoding in found
            else:
                verify_order(a, list(map(int, order)), 6)
                nongreedy += 1
        assert nongreedy == row["search"]
        count = run([geng, "-u", *args])
        assert int(re.search(r">Z (\d+) graphs", count.stderr)[1]) == expected
        row.update(arguments=list(map(str, args)), exceptions=found,
                   unmodified_generator_count=expected,
                   nongreedy_orders_verified_in_python=nongreedy)
        rows.append(row)
        print(f"n={n}: {expected:,} cores; exceptions {found}", flush=True)
    assert sum(r["total"] for r in rows) == 96841893
    return rows


def certify_exception(checker, encoding):
    """Exact treewidth seven, and treewidth six after any reduction."""
    core = decode(encoding)
    adj = masks(core)
    lower, none = width_reachable(adj, 6)
    assert none is None and verify_width_lower(adj, 6, lower)
    upper = check_orders(checker, [core], 7)[0]
    assert verify_order(core, upper, 7) == 7
    cases = list(reductions(core))
    orders = check_orders(checker, [a for _, a in cases], 6)
    assert all(orders)
    return {"graph6": encoding, "adjacency_lists": [sorted(ns) for ns in core],
            "triangles": triangles(core),
            "width_six_closed_prefixes": sorted(lower), "width_seven_order": upper,
            "reductions": [{**label, "graph6": encode(a), "width_six_order": order}
                           for (label, a), order in zip(cases, orders)]}


def check_witness(checker):
    """The 34-edge graph has treewidth exactly eight."""
    witness = json.loads((ROOT / "sources/witness34-17.json").read_text())
    a = decode(witness["graph6"])
    assert len(a) == 17 and sum(map(len, a)) == 68
    assert verify_width_lower(masks(a), 7, set(witness["width_seven_closed_prefixes"]))
    assert verify_order(a, witness["width_eight_order"], 8) == 8
    assert check_orders(checker, [a], 7) == [None]
    assert check_orders(checker, [a], 8)[0] is not None
    return witness["graph6"]


def main():
    if not __debug__:
        raise RuntimeError("Run without -O: assertions are verification steps.")
    flags = shlex.split(run(["pkg-config", "--cflags", "--libs", "nauty"]).stdout)
    out = {"date": date.today().isoformat(),
           "nauty_version": run(["pkg-config", "--modversion", "nauty"]).stdout.strip(),
           "compiler": run(CC + ["--version"]).stdout.splitlines()[0],
           "sha256": {path: digest(ROOT / path) for path in (
               "scripts/reproduce.py", "scripts/reference.py",
               "scripts/treewidth.c", "sources/witness34-17.json")},
           "geng_sha256": digest(GENG)}
    with TemporaryDirectory(prefix="treewidth-min-edges-") as name:
        tmp = Path(name)
        geng, plugin, checker = (tmp / x for x in ("geng", "geng-tw6", "checker"))
        run(CC + ["-O3", GENG, *flags, "-o", geng])
        run(CC + ["-O3", "-DOUTPROC=tw_out", "-DSUMMARY=tw_summary",
                  GENG, SOURCE, *flags, "-o", plugin])
        run(CC + ["-O3", "-Wall", "-Wextra", "-DTW_MAXN=17", "-DSTANDALONE",
                  SOURCE, "-o", checker])
        out["checker_audit"] = audit(checker, geng)
        print("Checker audit passed:", out["checker_audit"], flush=True)
        out["cores"] = classify(geng, plugin, tmp)
        out["total_cores"] = sum(r["total"] for r in out["cores"])
        out["exceptional_cores"] = [certify_exception(checker, s)
                                    for n in sorted(EXCEPTIONS) for s in EXCEPTIONS[n]]
        print("K8 and F: treewidth 7; every edge deletion and triangle-to-star "
              "replacement has treewidth at most 6.", flush=True)
        out["witness34_17_graph6"] = check_witness(checker)
        print("34-edge graph: treewidth exactly 8.", flush=True)
    destination = ROOT / "sources/results.json"
    destination.write_text(json.dumps(out, indent=1) + "\n")
    print(f"Results saved to {destination}", flush=True)
    verify_certificates.main()
    print("PASS: every computational step of Sections 1–7 of proof.md verified.")


if __name__ == "__main__":
    main()
