"""Classify connected 34-edge graphs of treewidth eight (proof.md, Section 8).

Uses nauty's geng and genquarticg sources. GENREG is an optional independent
cross-check. See README.md for source locations. No downloads are performed.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
import gzip
import itertools
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import time
from tempfile import TemporaryDirectory

from extend29 import reconstruct
from reference import decode
from reproduce import CC, GENG, ROOT, SOURCE, check_orders, digest, run

EXPECTED = {9: 133, 10: 131639, 11: 18336090, 12: 230446743,
            13: 256853749, 14: 12303420}
EXPECTED_EXCEPTIONS = {9: 1, 10: 0, 11: 0, 12: 77, 13: 40, 14: 6}
TRACKED = ("scripts/reproduce_uniqueness.py", "scripts/extend29.py",
           "scripts/check_quartic.c", "scripts/quartic_plugin.c", "scripts/treewidth.c",
           "scripts/reference.py", "scripts/reproduce.py", "sources/witness34-16.json",
           "sources/witness34-17.json")
GENREG_FILES = ("gendef.h", "genreg.c", "main.c", "optmid.c")


def isomorphism(a, b):
    """Find an explicit isomorphism; callers verify the resulting permutation."""
    assert len(a) == len(b)
    n = len(a)
    mapping = {}
    used = set()

    def search():
        if len(mapping) == n:
            return [mapping[v] for v in range(n)]
        choices = []
        for v in range(n):
            if v in mapping:
                continue
            candidates = [w for w in range(n) if w not in used
                          and len(a[v]) == len(b[w])
                          and all((u in a[v]) == (mapping[u] in b[w]) for u in mapping)]
            if not candidates:
                return None
            choices.append((len(candidates), v, candidates))
        _, v, candidates = min(choices)
        for w in candidates:
            mapping[v] = w
            used.add(w)
            found = search()
            if found is not None:
                return found
            used.remove(w)
            del mapping[v]
        return None

    result = search()
    assert result is not None
    assert sorted(result) == list(range(n))
    assert all({result[w] for w in a[v]} == b[result[v]] for v in range(n))
    return result


def identify_quartic(row, found, count, generator):
    assert count == row["total"] == 86221634
    assert row["verified"] == count - 1 and row["counterexamples"] == 1
    assert len(found) == 1
    witness = decode((ROOT / "sources/witness34-17.g6").read_text().strip())
    permutation = isomorphism(decode(found[0]), witness)
    row.update(exceptions=found, generator_count=count, generator=generator,
               isomorphism_to_witness=permutation)
    return row


def classify_nauty_quartic(plugin, generator):
    args = ["-c", "17"] if generator == "genquarticg" else [
        "-c", "-d4", "-D4", "17", "34:34"]
    start = time.monotonic()
    result = run([plugin, *args])
    row = next(json.loads(s.removeprefix("TW_RESULT "))
               for s in result.stderr.splitlines() if s.startswith("TW_RESULT "))
    count = int(re.search(r">Z (\d+) graphs", result.stderr)[1])
    row["wall_seconds"] = time.monotonic() - start
    row["arguments"] = args
    return identify_quartic(row, result.stdout.splitlines(), count, generator)


def degree_six(checker):
    a = decode("K?bFBO{}?}Ug")
    graphs, records = [], []
    for ns in itertools.combinations(range(12), 6):
        b = [set(s) for s in a] + [set(ns)]
        for v in ns:
            b[v].add(12)
        graphs.append(b)
        records.append({"neighbors": list(ns)})
    orders = check_orders(checker, graphs, 7)
    assert len(orders) == 924 and all(o is not None for o in orders)
    for record, order in zip(records, orders):
        record["order"] = order
    return records


def classify29(n, geng, plugin):
    args = ["-c", "-d4", "-D8", n, "29:29"]
    result = run([plugin, *args])
    row = next(json.loads(s.removeprefix("TW_RESULT "))
               for s in result.stderr.splitlines() if s.startswith("TW_RESULT "))
    count = run([geng, "-u", *args])
    independent = int(re.search(r">Z (\d+) graphs", count.stderr)[1])
    found = result.stdout.splitlines()
    assert row["n"] == n and row["width"] == 6
    assert row["total"] == independent == EXPECTED[n]
    assert row["counterexamples"] == len(found) == EXPECTED_EXCEPTIONS[n]
    assert row["verified"] + len(found) == independent
    assert row["greedy"] + row["search"] == row["verified"]
    row.update(exceptions=found, unmodified_generator_count=independent,
               arguments=list(map(str, args)))
    return row


def classify_quartic(genreg, checker, tmp):
    # Both return codes are checked; a broken generator cannot silently pass.
    generator_log = tmp / "genreg.log"
    checker_log = tmp / "quartic.log"
    start = time.monotonic()
    with generator_log.open("w") as gerr, checker_log.open("w") as cerr:
        gen = subprocess.Popen([str(genreg), "17", "4", "-s", "stdout"],
                               stdout=subprocess.PIPE, stderr=gerr)
        try:
            result = subprocess.run([str(checker), "17"], stdin=gen.stdout,
                                    stdout=subprocess.PIPE, stderr=cerr,
                                    text=True, check=True)
            gen.stdout.close()
            assert gen.wait() == 0
        finally:
            if gen.poll() is None:
                gen.terminate()
                gen.wait()
    count = int(re.search(r"(\d+) Graphen erzeugt", generator_log.read_text())[1])
    row = next(json.loads(s.removeprefix("QUARTIC_RESULT "))
               for s in checker_log.read_text().splitlines()
               if s.startswith("QUARTIC_RESULT "))
    found = result.stdout.splitlines()
    row["wall_seconds"] = time.monotonic() - start
    row["arguments"] = ["17", "4", "-s", "stdout"]
    return identify_quartic(row, found, count, "genreg")


def save(out, reconstruction):
    packed = json.dumps(reconstruction, separators=(",", ":")).encode()
    target = ROOT / "sources/uniqueness-reconstruction.json.gz"
    target.write_bytes(gzip.compress(packed, mtime=0))
    out["sha256"] = {p: digest(ROOT / p) for p in TRACKED}
    out["sha256"][str(target.relative_to(ROOT))] = digest(target)
    (ROOT / "sources/uniqueness.json").write_text(json.dumps(out, indent=1) + "\n")


def main():
    if not __debug__:
        raise RuntimeError("Run without -O: assertions are verification steps.")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quartic-generator", choices=("genquarticg", "genreg", "geng"),
                        default="genquarticg")
    parser.add_argument("--genquartic-source", type=Path,
                        default=Path(os.environ.get("GENQUARTIC_SOURCE",
                                                    "/usr/share/nauty/genquarticg.c")))
    parser.add_argument("--genreg-source", type=Path)
    parser.add_argument("--cross-check-genreg", action="store_true")
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("--workers must be positive")
    use_genreg = args.quartic_generator == "genreg" or args.cross_check_genreg
    if use_genreg and args.genreg_source is None:
        parser.error("GENREG needs --genreg-source /path/to/genreg")
    if args.cross_check_genreg and args.quartic_generator == "genreg":
        parser.error("GENREG is already the selected generator")
    if args.quartic_generator == "genquarticg" and not args.genquartic_source.is_file():
        parser.error("provide --genquartic-source /path/to/nauty/genquarticg.c")
    gen_source = args.genreg_source.resolve() if args.genreg_source else None
    flags = shlex.split(run(["pkg-config", "--cflags", "--libs", "nauty"]).stdout)
    out = {"date": date.today().isoformat(),
           "nauty_version": run(["pkg-config", "--modversion", "nauty"]).stdout.strip(),
           "compiler": run(CC + ["--version"]).stdout.splitlines()[0],
           "geng_sha256": digest(GENG)}
    if use_genreg:
        out.update(genreg_source_url="https://svn.code.sf.net/p/genreg/code/trunk/",
                   genreg_revision=5,
                   genreg_sha256={p: digest(gen_source / p) for p in GENREG_FILES})
    if args.quartic_generator == "genquarticg":
        out["genquarticg_sha256"] = digest(args.genquartic_source)
        out["quarticirred28_sha256"] = digest(args.genquartic_source.parent / "quarticirred28.h")
    with TemporaryDirectory(prefix="treewidth-classify34-") as name:
        tmp = Path(name)
        geng, plugin, checker, genreg, quartic = (
            tmp / s for s in ("geng", "geng6", "checker", "genreg", "quartic"))
        run(CC + ["-O3", GENG, *flags, "-o", geng])
        run(CC + ["-O3", "-DTW_MAXN=17", "-DTW_TARGET=6", "-DOUTPROC=tw_out",
                  "-DSUMMARY=tw_summary", GENG, SOURCE, *flags, "-o", plugin])
        run(CC + ["-O3", "-DTW_MAXN=17", "-DSTANDALONE", SOURCE, "-o", checker])
        if use_genreg:
            run(CC + ["-O3", ROOT / "scripts/check_quartic.c", "-o", quartic])
            run(CC + ["-O3", "-D__UNIX__", *(gen_source / p for p in GENREG_FILES
                                             if p.endswith(".c")), "-o", genreg])
        quartic_plugin = tmp / "quartic-plugin"
        if args.quartic_generator == "genquarticg":
            run(CC + ["-O3", "-DOUTPROC=tw_out",
                      "-DPLUGIN_INIT=extern void tw_quartic_summary(void); atexit(tw_quartic_summary);",
                      args.genquartic_source, ROOT / "scripts/quartic_plugin.c",
                      *flags, "-o", quartic_plugin])
        elif args.quartic_generator == "geng":
            run(CC + ["-O3", "-DTW_MAXN=17", "-DTW_TARGET=7", "-DOUTPROC=tw_out",
                      "-DSUMMARY=tw_summary", GENG, SOURCE, *flags, "-o", quartic_plugin])
        out["degree_six_extensions"] = degree_six(checker)
        rows = []
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            futures = [pool.submit(classify29, n, geng, plugin) for n in EXPECTED]
            for future in as_completed(futures):
                row = future.result()
                rows.append(row)
                print(f"29 edges, n={row['n']}: {row['total']:,} cores, "
                      f"{row['counterexamples']} survivors", flush=True)
        out["cores29"] = sorted(rows, key=lambda row: row["n"])
        seeds = [s for row in out["cores29"] for s in row["exceptions"]]
        reconstruction = reconstruct(checker, seeds)
        assert reconstruction["exceptions"] == [
            (ROOT / "sources/witness34-16.g6").read_text().strip()]
        if args.quartic_generator == "genreg":
            out["quartic17"] = classify_quartic(genreg, quartic, tmp)
        else:
            out["quartic17"] = classify_nauty_quartic(quartic_plugin, args.quartic_generator)
        if args.cross_check_genreg:
            out["quartic_crosschecks"] = [classify_quartic(genreg, quartic, tmp)]
        out["reconstruction_levels"] = reconstruction["levels"]
        out["degree_five_exceptions"] = reconstruction["exceptions"]
    save(out, reconstruction)
    import verify_uniqueness
    verify_uniqueness.main()
    print("PASS: exactly two connected 34-edge graphs have treewidth eight.")


if __name__ == "__main__":
    main()
