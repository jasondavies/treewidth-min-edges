"""Draw the 17-vertex witness in the visual style of witness34-16.svg.

Uses only the standard library. Edge/vertex IDs retain the certificate labels.
The twelve ring vertices form a Mobius ladder whose six diameters are drawn
as loops outside the ring; the four blue inner vertices are each joined to
every fourth ring vertex, and the dark-blue centre to all four inner vertices.
"""
import json
import math
from pathlib import Path

from reference import decode, edges

ROOT = Path(__file__).resolve().parents[1]
RING = [0, 2, 9, 16, 13, 6, 1, 5, 12, 15, 11, 3]
INNER = [4, 8, 7, 10]
HUB = 14
# Side of each diameter's loop, indexed by the ring position of its first
# endpoint; this choice makes the drawing symmetric about the anti-diagonal.
SIDES = [1, 1, -1, 1, -1, -1]


def main():
    a = decode(json.loads((ROOT / "sources/witness34-17.json").read_text())["graph6"])
    positions = {HUB: (300.0, 300.0)}
    for i, v in enumerate(RING):
        theta = -math.pi / 2 + 2 * math.pi * i / 12
        positions[v] = (300 + 190 * math.cos(theta), 300 + 190 * math.sin(theta))
    # An order-4 automorphism maps ring position i to i+3 and inner j to j-1,
    # so the inner vertices run anticlockwise.
    for j, v in enumerate(INNER):
        theta = -math.pi / 2 - 2 * math.pi * j / 4
        positions[v] = (300 + 140 * math.cos(theta), 300 + 140 * math.sin(theta))
    ring_edges = {tuple(sorted((v, RING[(i + 1) % 12])))
                  for i, v in enumerate(RING)}
    diameters = {tuple(sorted((RING[i], RING[i + 6]))): i for i in range(6)}
    assert all(v in a[u] for u, v in ring_edges | set(diameters))
    assert all(set(a[v]) == {RING[j], RING[j + 4], RING[j + 8], HUB}
               for j, v in enumerate(INNER))
    assert all(len(a[v]) == 4 for v in range(17))
    assert sorted(positions) == list(range(17))
    paths = []
    for u, v in edges(a):
        x, y = positions[u]
        xx, yy = positions[v]
        path = f"M{x:.1f},{y:.1f} L{xx:.1f},{yy:.1f}"
        if (u, v) in diameters:
            # Route each diameter outside the ring as a cubic loop.
            sign = SIDES[diameters[u, v]]
            nx, ny = -sign * (yy - y) * 0.9, sign * (xx - x) * 0.9
            path = (f"M{x:.1f},{y:.1f} C{x + nx:.1f},{y + ny:.1f} "
                    f"{xx + nx:.1f},{yy + ny:.1f} {xx:.1f},{yy:.1f}")
        paths.append(f'<path class="e" data-edge="{u} {v}" d="{path}"/>')
    assert len(paths) == 34
    circles = []
    for v in RING + INNER + [HUB]:
        x, y = positions[v]
        css = "v hub" if v == HUB else "v in" if v in INNER else "v"
        circles.append(f'<circle id="v{v}" class="{css}" cx="{x:.1f}" cy="{y:.1f}" '
                       f'r="7.5"><title>Vertex {v}, degree {len(a[v])}</title></circle>')
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="29.5 29.5 528 528" width="528" height="528" role="img" aria-labelledby="title description">
<title id="title">A 17-vertex, 34-edge graph of treewidth eight</title>
<desc id="description">Twelve white ring vertices form a Mobius ladder: a 12-cycle whose six diameters curve outside the ring. Each of four blue inner vertices is joined to every fourth ring vertex, and a dark-blue centre vertex is joined to all four inner vertices. All vertices have degree four. Edge crossings are not vertices.</desc>
<style>
  .e { fill: none; stroke: #7d8590; stroke-width: 1.5; stroke-linecap: round; }
  .v { fill: #ffffff; stroke: #57606a; stroke-width: 1.8; }
  .v.in { fill: #54aeff; stroke: #0550ae; }
  .v.hub { fill: #0969da; stroke: #033d8b; }
</style>
'''
    svg += "\n".join(paths + circles) + "\n</svg>\n"
    destination = ROOT / "sources/witness34-17.svg"
    destination.write_text(svg)
    print(destination)


if __name__ == "__main__":
    main()
