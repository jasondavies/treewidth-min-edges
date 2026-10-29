# The last order-24 profile reduces directly to 34 edges

This short reduction excludes catalogue profile 88, relative to the complete
34-edge classification in [proof.md, Section 8](proof.md#8-classification-at-34-edges-exactly-two-connected-graphs).
That classification says that a graph with 34 edges and treewidth at least
eight has exactly 16 or 17 nonisolated vertices. The only disconnected
freedom is to add isolated vertices. The earlier minimum is f(8)=34.
Neither the 37-edge nor the 36-edge classification is needed here.

In this profile, high vertices 5, 6, 7 are independent. Each of high
vertices 2, 3, 4 is adjacent to all three of them, and its other two neighbors
are respectively the private low pairs

    {14,15}, {16,17}, {18,19}.

Suppose a completion G of the profile had treewidth at least 11. Deleting
5,6,7 removes exactly 15 edges and leaves 21 vertices, 37 edges, and
treewidth at least 8. Vertices2,3,4 now have degree 2. Suppress all three,
adding the edge between a vertex's two neighbors if it is absent.
Eliminating degree-two vertices preserves treewidth when it exceeds 2.
Each suppression removes two edges and adds at most one, so the result J
has 18 vertices, at most 34 edges, and treewidth at least 8.

J has no isolated vertices. Every low vertex initially has exactly one
high neighbor. The low vertices attached to5,6,7 lose that neighbor and
retain their three low neighbors. Each low endpoint of a suppressed high
loses at most one incidence, even if its replacement edge was already
present, and therefore still has degree at least 3. The six endpoints are
distinct. All other low degrees remain 4. The two surviving highs 0, 1 each
lose one deleted high neighbor, so retain degree 4. Thus J has minimum
degree at least 3.

If J had fewer than 34 edges, it would contradict f(8)=34. If it had 34,
its 18 nonisolated vertices would contradict the complete34-edge
classification. Therefore no completion of profile 88 has treewidth 11.

The small checker verifies this recipe against the independently checked
order-24 catalogue. It bounds the fill-edge count conservatively and
credits no fill edge when bounding surviving degrees, so it does not
assume any unknown low-low edge is absent:

```sh
python3 scripts/verify_order24_smoothing34.py
```

The JSON contains only the catalogue index and the six high-vertex
operations. This is a one-profile reduction; complete order-24 coverage
also uses the other verified components. Its 34-edge classification
premise can be regenerated with `scripts/reproduce_uniqueness.py`.
