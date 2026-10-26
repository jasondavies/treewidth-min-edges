"""Draw the 16-vertex witness in the visual style of witness34.svg.

Uses only the standard library. Edge/vertex IDs retain the certificate labels.
The twelve degree-four vertices form a Hamiltonian cycle plus a matching;
the four blue degree-five vertices form an inner four-cycle.
"""
import json
import math
from pathlib import Path

from reference import decode, edges

ROOT = Path(__file__).resolve().parents[1]
RING = [0, 5, 11, 14, 2, 6, 10, 13, 1, 4, 8, 12]
INNER = [7, 3, 9, 15]


def main():
    a = decode(json.loads((ROOT / "sources/witness34-16.json").read_text())["graph6"])
    positions = {}
    for vertices, radius in ((RING, 190), (INNER, 135)):
        for i, v in enumerate(vertices):
            theta = -math.pi / 2 + 2 * math.pi * i / len(vertices)
            if vertices is INNER:
                theta += math.pi / 2
            positions[v] = (300 + radius * math.cos(theta),
                            300 + radius * math.sin(theta))
    ring_edges = {tuple(sorted((v, RING[(i + 1) % 12])))
                  for i, v in enumerate(RING)}
    assert all(v in a[u] for u, v in ring_edges)
    assert all(len(a[v]) == 4 for v in RING)
    assert all(len(a[v]) == 5 for v in INNER)
    assert sorted(positions) == list(range(16))
    paths = []
    for u, v in edges(a):
        x, y = positions[u]
        xx, yy = positions[v]
        path = f"M{x:.1f},{y:.1f} L{xx:.1f},{yy:.1f}"
        if u in RING and v in RING and (u, v) not in ring_edges:
            # Route the matching outside the ring. The normal points towards
            # the midpoint of the shorter circular arc between the endpoints.
            nx, ny = (x + xx) / 2 - 300, (y + yy) / 2 - 300
            norm = math.hypot(nx, ny)
            nx, ny = nx / norm, ny / norm
            bulge = (235 - norm) / 0.75
            path = (f"M{x:.1f},{y:.1f} "
                    f"C{x + bulge * nx:.1f},{y + bulge * ny:.1f} "
                    f"{xx + bulge * nx:.1f},{yy + bulge * ny:.1f} {xx:.1f},{yy:.1f}")
        paths.append(f'<path class="e" data-edge="{u} {v}" d="{path}"/>')
    assert len(paths) == 34
    circles = []
    for v in RING + INNER:
        x, y = positions[v]
        css = "v in" if v in INNER else "v"
        circles.append(f'<circle id="v{v}" class="{css}" cx="{x:.1f}" cy="{y:.1f}" '
                       f'r="7.5"><title>Vertex {v}, degree {len(a[v])}</title></circle>')
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="36 36 528 528" width="528" height="528" role="img" aria-labelledby="title description">
<title id="title">A 16-vertex, 34-edge graph of treewidth eight</title>
<desc id="description">Twelve white vertices of degree four form the outer ring; its six additional matching edges curve outside. Four blue vertices of degree five form an inner four-cycle. Each blue vertex is joined to three ring vertices. Edge crossings are not vertices.</desc>
<style>
  .e { fill: none; stroke: #7d8590; stroke-width: 1.5; stroke-linecap: round; }
  .v { fill: #ffffff; stroke: #57606a; stroke-width: 1.8; }
  .v.in { fill: #54aeff; stroke: #0550ae; }
</style>
'''
    svg += "\n".join(paths + circles) + "\n</svg>\n"
    destination = ROOT / "sources/witness34-16.svg"
    destination.write_text(svg)
    print(destination)


if __name__ == "__main__":
    main()
