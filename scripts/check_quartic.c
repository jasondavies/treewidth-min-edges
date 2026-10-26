/* Read GENREG shortcode for connected quartic graphs, and certify width <= 7.
 * Build: cc -O3 scripts/check_quartic.c -o check-quartic
 * Usage: genreg 17 4 -s stdout | check-quartic 17
 * The search and independent path-based order verifier are in treewidth.c.
 */
#define STANDALONE
#define TW_MAXN 17
#define main graph6_main
#include "treewidth.c"
#undef main

static void output_graph6(const mask *a, int n)
{
    putchar(63 + n);
    int value = 0, bits = 0;
    for (int j = 1; j < n; ++j) for (int i = 0; i < j; ++i) {
        value = (value << 1) | !!(a[i] & (1u << j));
        if (++bits == 6) {
            putchar(63 + value); value = bits = 0;
        }
    }
    if (bits) putchar(63 + (value << (6 - bits)));
    putchar('\n');
    fflush(stdout);
}

int main(int argc, char **argv)
{
    int n;
    if (argc != 2 || !parse_width(argv[1], &n) || n < 5) {
        fputs("usage: check-quartic N (5 <= N <= 17)\n", stderr);
        return 2;
    }
    unsigned char code[2 * TW_MAXN] = {0};
    int prefix, m = 2 * n;
    while ((prefix = getchar()) != EOF) {
        if (prefix > m || (!total && prefix != 0) ||
            fread(code + prefix, 1, m - prefix, stdin) != (size_t)(m - prefix)) {
            fputs("invalid/truncated shortcode\n", stderr); return 2;
        }
        mask a[TW_MAXN] = {0};
        int v = 0;
        for (int i = 0; i < m; ++i) {
            while (v < n && pc(a[v]) == 4) ++v;
            int w = (int)code[i] - 1;
            if (v >= n || w <= v || w >= n || pc(a[w]) >= 4 ||
                (a[v] & (1u << w))) {
                fputs("invalid shortcode edge\n", stderr); return 2;
            }
            a[v] |= 1u << w; a[w] |= 1u << v;
        }
        for (int i = 0; i < n; ++i) assert(pc(a[i]) == 4);
        mask reached = 1, last = 0;
        while (reached != last) {
            last = reached;
            for (int i = 0; i < n; ++i)
                if (reached & (1u << i)) reached |= a[i];
        }
        if (pc(reached) != n) {
            fputs("disconnected graph\n", stderr); return 2;
        }
        if (!check(a, n, 7)) output_graph6(a, n);
        if (total % 1000000 == 0)
            fprintf(stderr, "PROGRESS %llu\n", (unsigned long long)total);
    }
    if (ferror(stdin)) { perror("shortcode input"); return 2; }
    fprintf(stderr, "QUARTIC_RESULT {\"n\":%d,\"total\":%llu,"
            "\"verified\":%llu,\"counterexamples\":%llu}\n", n,
            (unsigned long long)total, (unsigned long long)verified,
            (unsigned long long)counterexamples);
    return 0;
}
