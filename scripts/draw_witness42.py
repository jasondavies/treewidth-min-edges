"""Draw the 42-edge treewidth-nine witness using only the standard library.

Sevenfold symmetric layout in the style of the two 34-edge drawings.
Vertex and edge identifiers use exactly the certificate's labeling.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Three orbits of an order-seven automorphism, traversed in steps of three.
OUTER = [0, 10, 13, 8, 14, 2, 17]
LEFT = [7, 3, 4, 1, 6, 9, 5]
RIGHT = [18, 16, 20, 15, 11, 19, 12]


def decode(s):
    n = ord(s[0])-63
    assert n == 21 and len(s) == 36
    a = [set() for _ in range(n)]
    bit = 0
    for v in range(1,n):
        for u in range(v):
            if (ord(s[1+bit//6])-63) >> (5-bit%6) & 1:
                a[u].add(v); a[v].add(u)
            bit += 1
    return a


def main():
    certificate = json.loads((ROOT/'sources/witness42.json').read_text())
    assert (ROOT/'sources/witness42.g6').read_text().strip() == certificate['graph6']
    a = decode(certificate['graph6'])
    assert sorted(OUTER+LEFT+RIGHT) == list(range(21))
    assert all(len(ns)==4 for ns in a)
    assert all(a[v] == {OUTER[(i-1)%7],OUTER[(i+1)%7],LEFT[i],RIGHT[i]}
               for i,v in enumerate(OUTER))
    positions = {}
    for ring,radius,offset in [(OUTER,235,0),(LEFT,145,-math.pi/14),(RIGHT,145,math.pi/14)]:
        for i,v in enumerate(ring):
            angle = -math.pi/2+2*math.pi*i/7+offset
            positions[v] = (270+radius*math.cos(angle),270+radius*math.sin(angle))
    paths=[]
    curved=0
    for u in range(21):
        for v in sorted(a[u]):
            if u>=v: continue
            x,y=positions[u]; xx,yy=positions[v]
            path=f'M{x:.2f},{y:.2f} L{xx:.2f},{yy:.2f}'
            if u not in OUTER and v not in OUTER and abs(x+xx-540)<1e-6 and abs(y+yy-540)<1e-6:
                # Bend the seven diameters consistently to avoid a false central hub.
                sign=1 if u in LEFT else -1
                cx=270+sign*(yy-y)*0.24; cy=270-sign*(xx-x)*0.24
                path=f'M{x:.2f},{y:.2f} Q{cx:.2f},{cy:.2f} {xx:.2f},{yy:.2f}'
                curved+=1
            paths.append(f'<path class="e" data-edge="{u} {v}" d="{path}"/>')
    assert len(paths)==42 and curved==7
    circles=[]
    for v in OUTER+LEFT+RIGHT:
        x,y=positions[v]
        css='v' if v in OUTER else 'v in'
        circles.append(f'<circle id="v{v}" class="{css}" cx="{x:.2f}" cy="{y:.2f}" r="7.5">'
                       f'<title>Vertex {v}, degree 4</title></circle>')
    svg='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -11.6 540 540" width="540" height="540" role="img" aria-labelledby="title description">
<title id="title">A 21-vertex, 42-edge graph of treewidth nine</title>
<desc id="description">Seven white vertices form an outer cycle. Each is joined to a pair of blue inner vertices. The fourteen inner vertices each have three further neighbors on the inner ring. The drawing has sevenfold rotational symmetry. All vertices have degree four. Edge crossings are not vertices.</desc>
<style>
  .e { fill: none; stroke: #7d8590; stroke-width: 1.5; stroke-linecap: round; }
  .v { fill: #ffffff; stroke: #57606a; stroke-width: 1.8; }
  .v.in { fill: #54aeff; stroke: #0550ae; }
</style>
'''
    svg+='\n'.join(paths+circles)+'\n</svg>\n'
    destination=ROOT/'sources/witness42.svg'
    destination.write_text(svg)
    print(destination)


if __name__=='__main__':
    main()
