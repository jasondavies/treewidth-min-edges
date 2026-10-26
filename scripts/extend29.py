"""Reconstruct all relevant 29-edge graphs, then add a degree-five vertex.

See Section 8 of proof.md for the completeness argument. Seeds are the exhaustive
29-edge cores emitted by the width-six geng plugin. Width-six intermediate
graphs can be discarded: triangle-to-star replacements preserve that bound,
and adding one vertex raises it by at most one.
"""
import argparse
import itertools
import json
from pathlib import Path

from reference import decode, encode, triangles
from reproduce import check_orders


def star(a, triangle, retained=None):
    b = [set(ns) for ns in a] + [set(triangle)]
    for u, v in itertools.combinations(triangle, 2):
        if (u, v) != retained:
            b[u].remove(v)
            b[v].remove(u)
    for v in triangle:
        b[v].add(len(a))
    return b


def reconstruct(checker, seeds, oracle=check_orders, progress=True):
    roots = [decode(s) for s in seeds]
    for s in ("G~~~~{", "K?bFBO{}?}Ug"):
        a = decode(s)
        for t in triangles(a):
            for retained in itertools.combinations(t, 2):
                roots.append(star(a, t, retained))
    states = [(a, triangles(a), 0) for a in roots]
    out = {"seeds": seeds, "levels": [], "discarded_width_six": [],
           "extensions": [], "exceptions": []}
    seen_extensions = set()
    while states:
        # Degrees never increase under these reverse operations. Once a vertex
        # has degree three it cannot occur in another replacement, because the
        # target H has minimum degree three. At most five such vertices can be
        # repaired by the new degree-five vertex.
        states = [(a, ts, start) for a, ts, start in states
                  if len(a) <= 16 and min(map(len, a)) >= 3
                  and sum(len(ns) == 3 for ns in a) <= 5]
        if not states:
            break
        orders = oracle(checker, [a for a, _, _ in states], 6)
        next_states, candidates = [], []
        row = {"tested": len(states), "width_six": 0, "extensions": 0}
        for (a, ts, start), order in zip(states, orders):
            if order is not None:
                out["discarded_width_six"].append(
                    {"graph6": encode(a), "order": order})
                row["width_six"] += 1
                continue
            if 13 <= len(a) <= 16 and max(map(len, a)) <= 5:
                required = [v for v, ns in enumerate(a) if len(ns) == 3]
                optional = [v for v, ns in enumerate(a) if len(ns) == 4]
                for chosen in itertools.combinations(optional, 5 - len(required)):
                    ns = required + list(chosen)
                    b = [set(s) for s in a] + [set(ns)]
                    for v in ns:
                        b[v].add(len(a))
                    s = encode(b)
                    if s not in seen_extensions:
                        seen_extensions.add(s)
                        candidates.append(b)
            if len(a) < 16:
                for i in range(start, len(ts)):
                    t = ts[i]
                    if all(len(a[v]) >= 4 for v in t) and all(
                            v in a[u] for u, v in itertools.combinations(t, 2)):
                        next_states.append((star(a, t), ts, i + 1))
        orders = oracle(checker, candidates, 7) if candidates else []
        for a, order in zip(candidates, orders):
            assert sum(map(len, a)) == 68
            assert all(4 <= len(ns) <= 5 for ns in a)
            record = {"graph6": encode(a), "order": order}
            out["extensions"].append(record)
            if order is None:
                out["exceptions"].append(record["graph6"])
        row["extensions"] = len(candidates)
        out["levels"].append(row)
        if progress:
            print(f"Reconstruction level {len(out['levels'])}: {row}", flush=True)
        states = next_states
    return out


def main():
    if not __debug__:
        raise RuntimeError("Run without -O: assertions are verification steps.")
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--checker", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("seeds", nargs="+", type=Path)
    args = p.parse_args()
    seeds = [s for path in args.seeds for s in path.read_text().splitlines()]
    result = reconstruct(args.checker, seeds)
    args.output.write_text(json.dumps(result, indent=1) + "\n")
    print(f"Extensions: {len(result['extensions'])}; "
          f"exceptions: {len(result['exceptions'])}")


if __name__ == "__main__":
    main()
