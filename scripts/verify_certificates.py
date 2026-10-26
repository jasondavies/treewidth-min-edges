"""Check the saved certificates using only Python's standard library.

This checks source hashes, the exact treewidth of K8, F, and the 34-edge
graphs, and the width-six orders for every reduction of K8 and F. It does NOT
repeat geng's enumeration of the 96,841,893 cores; run reproduce.py for that.
"""
import hashlib
import json
from pathlib import Path

from reference import (decode, encode, masks, reductions, triangles,
                       verify_order, verify_width_lower)

ROOT = Path(__file__).resolve().parents[1]


def exact_width(a, order, closed_prefixes, width):
    assert verify_order(a, order, width) == width
    assert verify_width_lower(masks(a), width - 1, set(closed_prefixes))


def main():
    if not __debug__:
        raise RuntimeError("Run without -O: assertions are verification steps.")
    result = json.loads((ROOT / "sources/results.json").read_text())
    for path, expected in result["sha256"].items():
        actual = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        assert actual == expected, f"Source hash mismatch: {path}"
    assert result["total_cores"] == 96841893

    cores = result["exceptional_cores"]
    assert [c["graph6"] for c in cores] == ["G~~~~{", "K?bFBO{}?}Ug"]
    checked = 0
    for core in cores:
        a = decode(core["graph6"])
        assert [sorted(ns) for ns in a] == core["adjacency_lists"]
        assert [list(t) for t in triangles(a)] == core["triangles"]
        exact_width(a, core["width_seven_order"], core["width_six_closed_prefixes"], 7)
        saved = core["reductions"]
        expected = list(reductions(a))
        assert len(saved) == len(expected)
        for record, (label, b) in zip(saved, expected):
            assert all(record[k] == v for k, v in label.items())
            assert record["graph6"] == encode(b)
            verify_order(b, record["width_six_order"], 6)
            checked += 1

    witness = json.loads((ROOT / "sources/witness34.json").read_text())
    a = decode(witness["graph6"])
    assert len(a) == witness["n"] == 17
    assert sum(map(len, a)) // 2 == witness["edges"] == 34
    assert [sorted(ns) for ns in a] == witness["adjacency_lists"]
    assert (ROOT / "sources/witness34.g6").read_text().strip() == witness["graph6"]
    assert result["witness34_graph6"] == witness["graph6"]
    exact_width(a, witness["width_eight_order"], witness["width_seven_closed_prefixes"], 8)

    second = json.loads((ROOT / "sources/witness34-16.json").read_text())
    b = decode(second["graph6"])
    assert len(b) == second["n"] == 16
    assert sum(map(len, b)) // 2 == second["edges"] == 34
    assert [sorted(ns) for ns in b] == second["adjacency_lists"]
    assert (ROOT / "sources/witness34-16.g6").read_text().strip() == second["graph6"]
    assert not triangles(b)
    exact_width(b, second["width_eight_order"], second["width_seven_closed_prefixes"], 8)

    print(f"PASS: K8 and F have treewidth 7, all {checked} of their reductions have "
          "treewidth at most 6, and both 34-edge graphs have treewidth 8.")
    print("Certificate-only check: the core enumeration is not repeated here.")


if __name__ == "__main__":
    main()
