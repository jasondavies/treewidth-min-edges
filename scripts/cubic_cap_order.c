/* Bounded, untrusted order finder. Python independently checks every order. */
#include <stdint.h>
#include <string.h>

#define MAXN 23

static int prefix_order(const uint32_t *input, int n, int width,
                        int first, int second, unsigned char *out) {
    uint32_t adjacency[MAXN], live = (UINT32_C(1) << n) - 1;
    memcpy(adjacency, input, (size_t)n * sizeof *adjacency);
    for (int step = 0; step < n; ++step) {
        int chosen = step == 0 ? first : step == 1 ? second : -1;
        if (chosen < 0) {
            int score = 10000;
            uint32_t candidates = live;
            while (candidates) {
                int v = __builtin_ctz(candidates);
                candidates &= candidates - 1;
                uint32_t neighbors = adjacency[v] & live, todo = neighbors;
                int degree = __builtin_popcount(neighbors), missing = 0;
                if (degree > width)
                    continue;
                while (todo) {
                    int u = __builtin_ctz(todo);
                    todo &= todo - 1;
                    missing += __builtin_popcount(neighbors & ~adjacency[u]
                                                   & ~(UINT32_C(1) << u));
                }
                int value = 8 * missing + degree;
                if (value < score) {
                    score = value;
                    chosen = v;
                }
            }
        }
        if (chosen < 0 || !(live & (UINT32_C(1) << chosen)))
            return 0;
        uint32_t neighbors = adjacency[chosen] & live;
        if (__builtin_popcount(neighbors) > width)
            return 0;
        out[step] = (unsigned char)chosen;
        live &= ~(UINT32_C(1) << chosen);
        while (neighbors) {
            int u = __builtin_ctz(neighbors);
            neighbors &= neighbors - 1;
            adjacency[u] |= (adjacency[chosen] & live) & ~(UINT32_C(1) << u);
        }
    }
    return 1;
}

/* Positive: found order; zero: bounded attempts exhausted; negative: bad input. */
int propose(const uint32_t *input, int n, int width, unsigned char *out) {
    if (n < 1 || n > MAXN || width < 0 || width >= n)
        return -1;
    uint32_t limit = (UINT32_C(1) << n) - 1;
    for (int v = 0; v < n; ++v) {
        if ((input[v] & ~limit) || (input[v] & (UINT32_C(1) << v)))
            return -1;
        for (int u = 0; u < n; ++u)
            if (((input[v] >> u) & 1) != ((input[u] >> v) & 1))
                return -1;
    }
    int attempts = 1;
    if (prefix_order(input, n, width, -1, -1, out))
        return attempts;
    for (int u = 0; u < n; ++u) {
        ++attempts;
        if (prefix_order(input, n, width, u, -1, out))
            return attempts;
    }
    for (int u = 0; u < n; ++u)
        for (int v = 0; v < n; ++v) {
            if (u == v)
                continue;
            ++attempts;
            if (prefix_order(input, n, width, u, v, out))
                return attempts;
        }
    return 0;
}
