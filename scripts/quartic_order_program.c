/* Untrusted order-program interpreter; Python checks the returned permutation. */
#include <stdint.h>
#include <string.h>

int minfill26_prefix(const uint32_t input[26], int first, int second, unsigned char order[26]) {
    uint32_t adjacency[26], live = (UINT32_C(1) << 26) - 1;
    if (first < 0 || first >= 26 || second < -1 || second >= 26 || first == second) return 0;
    memcpy(adjacency, input, sizeof adjacency);
    for (int step = 0; step < 26; ++step) {
        int chosen = step == 1 && second >= 0 ? second : first;
        if (step && !(step == 1 && second >= 0)) {
            int best_fill = 1000, best_degree = 1000;
            uint32_t candidates = live;
            while (candidates) {
                int v = __builtin_ctz(candidates);
                candidates &= candidates - 1;
                uint32_t neighbors = adjacency[v] & live, remaining = neighbors;
                int degree = __builtin_popcount(neighbors), twice_fill = 0;
                while (remaining) {
                    int u = __builtin_ctz(remaining);
                    remaining &= remaining - 1;
                    twice_fill += __builtin_popcount(neighbors & ~adjacency[u] & ~(UINT32_C(1) << u));
                }
                int fill = twice_fill / 2;
                if (fill < best_fill || (fill == best_fill && degree < best_degree)) {
                    chosen = v;
                    best_fill = fill;
                    best_degree = degree;
                }
            }
        }
        uint32_t neighbors = adjacency[chosen] & live;
        if (__builtin_popcount(neighbors) > 10) return 0;
        order[step] = (unsigned char)chosen;
        live &= ~(UINT32_C(1) << chosen);
        while (neighbors) {
            int u = __builtin_ctz(neighbors);
            neighbors &= neighbors - 1;
            adjacency[u] |= (adjacency[chosen] & live) & ~(UINT32_C(1) << u);
        }
    }
    return 1;
}

int minfill26(const uint32_t input[26], int first, unsigned char order[26]) {
    return minfill26_prefix(input, first, -1, order);
}
