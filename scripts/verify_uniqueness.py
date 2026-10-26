"""Check both witnesses and replay the finite reconstruction without a compiler.

This does not repeat the 29-edge or quartic enumerations. Their completeness
requires reproduce_uniqueness.py and the two external generators.
"""
import gzip
import hashlib
import itertools
import json
from collections import Counter
from pathlib import Path

from extend29 import reconstruct
from reference import decode, encode, masks, triangles, verify_order, verify_width_lower
from reproduce_uniqueness import EXPECTED, EXPECTED_EXCEPTIONS

ROOT = Path(__file__).resolve().parents[1]


def main():
    if not __debug__:
        raise RuntimeError("Run without -O: assertions are verification steps.")
    result = json.loads((ROOT / "sources/uniqueness.json").read_text())
    for path, expected in result["sha256"].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected, path
    witnesses = []
    for filename, n in (("witness34-16", 16), ("witness34", 17)):
        witness = json.loads((ROOT / f"sources/{filename}.json").read_text())
        a = decode(witness["graph6"])
        assert len(a) == witness["n"] == n
        assert sum(map(len, a)) == 68 and witness["edges"] == 34
        assert [sorted(ns) for ns in a] == witness["adjacency_lists"]
        assert not triangles(a)
        assert (ROOT / f"sources/{filename}.g6").read_text().strip() == witness["graph6"]
        assert verify_order(a, witness["width_eight_order"], 8) == 8
        assert verify_width_lower(masks(a), 7, set(witness["width_seven_closed_prefixes"]))
        reached = {0}
        while True:
            enlarged = reached | set().union(*(a[v] for v in reached))
            if enlarged == reached:
                break
            reached = enlarged
        assert len(reached) == n
        witnesses.append(witness["graph6"])

    a = decode("K?bFBO{}?}Ug")
    expected_ns = list(itertools.combinations(range(12), 6))
    records = result["degree_six_extensions"]
    assert len(records) == len(expected_ns) == 924
    for record, ns in zip(records, expected_ns):
        assert record["neighbors"] == list(ns)
        b = [set(s) for s in a] + [set(ns)]
        for v in ns:
            b[v].add(12)
        verify_order(b, record["order"], 7)

    rows = result["cores29"]
    assert [r["n"] for r in rows] == list(EXPECTED)
    for r in rows:
        n = r["n"]
        assert r["total"] == r["unmodified_generator_count"] == EXPECTED[n]
        assert r["width"] == 6
        assert r["counterexamples"] == len(r["exceptions"]) == EXPECTED_EXCEPTIONS[n]
        assert r["verified"] + r["counterexamples"] == r["total"]
        assert r["greedy"] + r["search"] == r["verified"]
        for s in r["exceptions"]:
            a = decode(s)
            assert len(a) == n and sum(map(len, a)) == 58
            assert all(4 <= len(ns) <= 8 for ns in a)
    seeds = [s for r in rows for s in r["exceptions"]]
    packed = ROOT / "sources/uniqueness-reconstruction.json.gz"
    saved = json.loads(gzip.decompress(packed.read_bytes()))
    assert saved["seeds"] == seeds
    assert len(seeds) == 124 and sum(r["total"] for r in rows) == 518071774
    assert len(saved["extensions"]) == 15091
    assert Counter(len(decode(r["graph6"])) for r in saved["extensions"]) == {
        14: 1045, 15: 12858, 16: 1188}
    known_six = {r["graph6"]: r["order"] for r in saved["discarded_width_six"]}
    known_seven = {r["graph6"]: r["order"] for r in saved["extensions"]}

    def saved_orders(_checker, graphs, width):
        orders = []
        for a in graphs:
            s = encode(a)
            # Treat missing width-six certificates conservatively as survivors.
            # Every omitted branch must have a verified elimination order.
            order = known_six.get(s) if width == 6 else known_seven[s]
            if order is not None:
                verify_order(a, order, width)
            elif width == 7:
                assert s == witnesses[0]
            orders.append(order)
        return orders

    replay = reconstruct(None, seeds, oracle=saved_orders, progress=False)
    assert replay == saved
    assert saved["levels"] == result["reconstruction_levels"]
    assert saved["exceptions"] == result["degree_five_exceptions"] == [witnesses[0]]
    for q in [result["quartic17"], *result.get("quartic_crosschecks", [])]:
        assert q["n"] == 17 and q["total"] == q["generator_count"] == 86221634
        assert q["verified"] == 86221633 and q["counterexamples"] == 1
        assert len(q["exceptions"]) == 1
        a, b = decode(q["exceptions"][0]), decode(witnesses[1])
        permutation = q["isomorphism_to_witness"]
        assert sorted(permutation) == list(range(17))
        assert all({permutation[w] for w in a[v]} == b[permutation[v]] for v in range(17))
    print("PASS: two nonisomorphic 34-edge witnesses have treewidth exactly eight; "
          "924 degree-six extensions and all 15,091 reconstructed candidates checked.")
    print("Certificate-only check: the 29-edge and quartic enumerations are not repeated.")


if __name__ == "__main__":
    main()
