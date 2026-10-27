"""Draw the 47-edge treewidth-ten witness using only the standard library.

The fixed layout respects a reflection automorphism. The blue edge {1,10}
is the edge added to the quartic girth-five graph; its endpoints have degree
five. SVG vertex and edge identifiers retain the certificate's labels.
"""
import gzip
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ADDED_EDGE = (1, 10)
REFLECTION = (19, 10, 7, 12, 14, 16, 13, 2, 18, 17, 1, 20,
              3, 6, 4, 21, 5, 9, 8, 0, 11, 15, 22)
# Coordinates are indexed by the zero-based graph6 vertex labels.
POSITIONS = (
    (454.0, 202.7),  # 0
    (481.8, 40.0),  # 1
    (397.9, 81.1),  # 2
    (435.3, 452.8),  # 3
    (309.2, 285.1),  # 4
    (314.9, 207.1),  # 5
    (497.7, 500.0),  # 6
    (142.1, 81.1),  # 7
    (202.2, 131.7),  # 8
    (417.0, 283.7),  # 9
    (58.2, 40.0),  # 10
    (361.3, 343.1),  # 11
    (104.7, 452.8),  # 12
    (42.3, 500.0),  # 13
    (230.8, 285.1),  # 14
    (177.2, 422.1),  # 15
    (225.1, 207.1),  # 16
    (123.0, 283.7),  # 17
    (337.8, 131.7),  # 18
    (86.0, 202.7),  # 19
    (178.7, 343.1),  # 20
    (362.8, 422.1),  # 21
    (270.0, 396.2),  # 22
)


def decode(s):
    n = ord(s[0]) - 63
    assert n == 23 and len(s) == 1 + (n * (n - 1) // 2 + 5) // 6
    assert all(63 <= ord(c) <= 126 for c in s)
    a = [set() for _ in range(n)]
    bit = 0
    for v in range(1, n):
        for u in range(v):
            if (ord(s[1 + bit // 6]) - 63) >> (5 - bit % 6) & 1:
                a[u].add(v)
                a[v].add(u)
            bit += 1
    return a


def main():
    if not __debug__:
        raise RuntimeError("Run without -O: assertions check the drawing against the certificate.")
    with gzip.open(ROOT / "sources/witness47.json.gz", "rt") as stream:
        certificate = json.load(stream)
    encoding = (ROOT / "sources/witness47.g6").read_text().strip()
    assert encoding == certificate["graph6"]
    a = decode(encoding)
    assert certificate["vertices"] == len(a) == len(POSITIONS) == 23
    edges = [(u, v) for u in range(23) for v in sorted(a[u]) if u < v]
    assert len(edges) == certificate["edges"] == 47
    assert ADDED_EDGE in edges
    assert all(len(a[v]) == (5 if v in ADDED_EDGE else 4) for v in range(23))

    # Verify both the graph symmetry and the fixed geometric layout.
    assert sorted(REFLECTION) == list(range(23))
    for v, (x, y) in enumerate(POSITIONS):
        w = REFLECTION[v]
        assert REFLECTION[w] == v
        assert {REFLECTION[u] for u in a[v]} == a[w]
        xx, yy = POSITIONS[w]
        assert abs(x + xx - 540) < 1e-6 and y == yy

    # Removing the highlighted edge recovers a quartic graph of girth >=5.
    base = [set(ns) for ns in a]
    u, v = ADDED_EDGE
    base[u].remove(v)
    base[v].remove(u)
    assert all(len(ns) == 4 for ns in base)
    assert all(not base[u] & base[v] for u in range(23) for v in base[u])
    assert all(len(base[u] & base[v]) <= 1 for u in range(23) for v in range(u))

    paths = []
    # Draw the highlighted edge last, with all vertex circles above the edges.
    for u, v in sorted(edges, key=lambda e: e == ADDED_EDGE):
        x, y = POSITIONS[u]
        xx, yy = POSITIONS[v]
        css = "e added" if (u, v) == ADDED_EDGE else "e"
        paths.append(f'<path class="{css}" data-edge="{u} {v}" '
                     f'd="M{x:.1f},{y:.1f} L{xx:.1f},{yy:.1f}">'
                     f'<title>Edge {u}–{v}</title></path>')
    circles = []
    for v, (x, y) in enumerate(POSITIONS):
        css = "v in" if v in ADDED_EDGE else "v"
        circles.append(f'<circle id="v{v}" class="{css}" cx="{x:.1f}" cy="{y:.1f}" '
                       f'r="7.5"><title>Vertex {v}, degree {len(a[v])}</title></circle>')
    assert len(paths) == 47 and len(circles) == 23
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 540 540" width="540" height="540" role="img" aria-labelledby="title description">
<title id="title">A 23-vertex, 47-edge graph of treewidth ten</title>
<desc id="description">The blue edge joins the two blue degree-five vertices at the top. Deleting this edge leaves a quartic graph of girth five. The other twenty-one vertices are white and have degree four. The drawing is symmetric about its vertical axis. Edge crossings are not vertices.</desc>
<style>
  .e { fill: none; stroke: #7d8590; stroke-width: 1.5; stroke-linecap: round; }
  .e.added { stroke: #0969da; stroke-width: 2.5; }
  .v { fill: #ffffff; stroke: #57606a; stroke-width: 1.8; }
  .v.in { fill: #54aeff; stroke: #0550ae; }
</style>
'''
    svg += "\n".join(paths + circles) + "\n</svg>\n"
    destination = ROOT / "sources/witness47.svg"
    destination.write_text(svg)
    print(destination)


if __name__ == "__main__":
    main()
