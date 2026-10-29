"""Draw the illustrated 53-edge treewidth-eleven witness (standard library).

The graph and its two curved edges respect reflection in the vertical axis.
All twelve vertex pairs are mirrored. Blue vertices have degree five; white
vertices have degree four. Labels match the accompanying graph6/certificate.
"""
import argparse
from pathlib import Path
from verify_treewidth_certificate import read_certificate

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "sources"
REFLECTION = (1, 0, 3, 2, 5, 4, 12, 8, 7, 11, 13, 9, 6, 10, 16, 17, 14, 15, 20, 21, 18, 19, 23, 22)
# Coordinates use the zero-based graph6 vertex labels.
POSITIONS = (
    (391.4, 352.1),  # 0
    (148.6, 352.1),  # 1
    (240.0, 283.7),  # 2
    (300.0, 283.7),  # 3
    (300.0, 383.2),  # 4
    (240.0, 383.2),  # 5
    (399.5, 69.1),  # 6
    (390.5, 467.8),  # 7
    (149.5, 467.8),  # 8
    (230.3, 97.8),  # 9
    (208.0, 352.0),  # 10
    (309.7, 97.8),  # 11
    (140.5, 69.1),  # 12
    (332.0, 352.0),  # 13
    (470.5, 349.8),  # 14
    (417.3, 243.7),  # 15
    (69.5, 349.8),  # 16
    (122.7, 243.7),  # 17
    (167.7, 169.8),  # 18
    (190.1, 288.4),  # 19
    (372.3, 169.8),  # 20
    (349.9, 288.4),  # 21
    (442.3, 153.0),  # 22
    (97.7, 153.0),  # 23
)
# Mirrored quadratic curves keep two long edges away from the central bundle.
CURVE_CONTROLS = {
    (12, 15): (374.9, 20.0),
    (6, 17): (165.1, 20.0),
}


def decode(s):
    n = ord(s[0]) - 63
    assert n == 24 and len(s) == 1 + (n * (n - 1) // 2 + 5) // 6
    assert all(63 <= ord(c) <= 126 for c in s)
    adjacency = [set() for _ in range(n)]
    bit = 0
    for v in range(n):
        for u in range(v):
            if (ord(s[1 + bit // 6]) - 63) >> (5 - bit % 6) & 1:
                adjacency[u].add(v)
                adjacency[v].add(u)
            bit += 1
    return adjacency


def main():
    if not __debug__:
        raise RuntimeError("Run without -O: assertions check the drawing against the certificate.")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "sources/witness53.svg")
    args = parser.parse_args()
    certificate, _ = read_certificate(SOURCE / "witness53.twcert.xz")
    encoding = (SOURCE / "witness53.g6").read_text().strip()
    assert encoding == certificate["graph6"]
    adjacency = decode(encoding)
    assert len(adjacency) == len(POSITIONS) == certificate["vertices"] == 24
    edges = [(u, v) for u in range(24) for v in sorted(adjacency[u]) if u < v]
    assert len(edges) == certificate["edges"] == 53
    assert certificate["treewidth"] == 11
    assert sorted(map(len, adjacency)) == [4] * 14 + [5] * 10
    # Check the graph automorphism separately from its geometric realization.
    assert sorted(REFLECTION) == list(range(24))
    for v, (x, y) in enumerate(POSITIONS):
        w = REFLECTION[v]
        assert REFLECTION[w] == v
        assert {REFLECTION[u] for u in adjacency[v]} == adjacency[w]
        xx, yy = POSITIONS[w]
        assert abs(x + xx - 540) < 1e-6 and y == yy
    assert CURVE_CONTROLS.keys() <= set(edges)
    for u, v in edges:
        mirror = tuple(sorted((REFLECTION[u], REFLECTION[v])))
        assert ((u, v) in CURVE_CONTROLS) == (mirror in CURVE_CONTROLS)
        if (u, v) in CURVE_CONTROLS:
            x, y = CURVE_CONTROLS[u, v]
            xx, yy = CURVE_CONTROLS[mirror]
            assert abs(x + xx - 540) < 1e-6 and y == yy
    paths = []
    for u, v in edges:
        x, y = POSITIONS[u]
        xx, yy = POSITIONS[v]
        if (u, v) in CURVE_CONTROLS:
            cx, cy = CURVE_CONTROLS[u, v]
            shape = f"M{x:.1f},{y:.1f} Q{cx:.1f},{cy:.1f} {xx:.1f},{yy:.1f}"
        else:
            shape = f"M{x:.1f},{y:.1f} L{xx:.1f},{yy:.1f}"
        paths.append(f'<path class="e" data-edge="{u} {v}" '
                     f'd="{shape}">'
                     f'<title>Edge {u}–{v}</title></path>')
    circles = []
    for v, (x, y) in enumerate(POSITIONS):
        degree = len(adjacency[v])
        css = "v high" if degree == 5 else "v"
        circles.append(f'<circle id="v{v}" class="{css}" cx="{x:.1f}" cy="{y:.1f}" '
                       f'r="7.5"><title>Vertex {v}, degree {degree}</title></circle>')
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 540 540" width="540" height="540" role="img" aria-labelledby="title description">
<title id="title">A 24-vertex, 53-edge graph of treewidth eleven</title>
<desc id="description">The ten blue vertices have degree five. The fourteen white vertices have degree four. All twenty-four vertices form twelve mirrored pairs. Two curved edges are mirrored too; the drawing has exact vertical reflection symmetry. Edge crossings are not vertices. Vertex and edge labels correspond to the saved graph6 encoding and treewidth certificate.</desc>
<style>
  .e { fill: none; stroke: #7d8590; stroke-width: 1.5; stroke-linecap: round; }
  .v { fill: #ffffff; stroke: #57606a; stroke-width: 1.8; }
  .v.high { fill: #54aeff; stroke: #0550ae; }
</style>
'''
    svg += "\n".join(paths + circles) + "\n</svg>\n"
    args.output.write_text(svg)
    print(args.output)


if __name__ == "__main__":
    main()
