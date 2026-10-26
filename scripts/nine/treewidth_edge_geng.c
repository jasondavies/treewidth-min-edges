/* Complete small-graph treewidth check; see entry 021's solution.md.
 * Build as a geng OUTPROC/SUMMARY plugin, or with -DSTANDALONE to read graph6.
 * The search fills neighborhoods. Its order verifier independently computes
 * filled neighbors as original paths through the eliminated vertex set.
 */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifndef STANDALONE
#include <nauty.h>
#include <gtools.h>
#endif

#ifndef TW_MAXN
#define TW_MAXN 14
#endif
#ifndef TW_TARGET
#define TW_TARGET 6
#endif
typedef uint32_t mask;
static uint64_t failed[1 << TW_MAXN], stamp;
static int order[TW_MAXN], target, size;
static uint64_t total, greedy_ok, searched_ok, counterexamples, verified;
static uint64_t edge_counts[100];
static int pc(mask x) { return __builtin_popcount(x); }
static int first(mask x) { assert(x); return __builtin_ctz(x); }

static void eliminate(mask *a, mask remaining, int v)
{
    mask ns = a[v] & remaining & ~(1u << v);
    for (mask t = ns; t; t &= t - 1) {
        int w = first(t);
        a[w] |= ns & ~(1u << w);
    }
}

static int fill_score(const mask *a, mask ns)
{
    int missing = 0;
    for (mask t = ns; t; t &= t - 1) {
        int w = first(t);
        missing += pc(ns & ~a[w] & ~(1u << w));
    }
    return missing / 2;
}

static int greedy(const mask *original)
{
    mask a[TW_MAXN], remaining = (1u << size) - 1;
    memcpy(a, original, size * sizeof(mask));
    for (int depth = 0; depth < size; ++depth) {
        int best = -1, best_score = 10000;
        for (mask t = remaining; t; t &= t - 1) {
            int v = first(t), d = pc(a[v] & remaining);
            if (d > target) continue;
            int score = 16 * fill_score(a, a[v] & remaining) + d;
            if (score < best_score) { best = v; best_score = score; }
        }
        if (best < 0) return 0;
        order[depth] = best;
        eliminate(a, remaining, best);
        remaining ^= 1u << best;
    }
    return 1;
}

static int search(const mask *a, mask remaining, int depth)
{
    if (!remaining) return 1;
    if (failed[remaining] == stamp) return 0;
    for (mask t = remaining; t; t &= t - 1) {
        int v = first(t);
        if (pc(a[v] & remaining) > target) continue;
        mask b[TW_MAXN];
        memcpy(b, a, size * sizeof(mask));
        eliminate(b, remaining, v);
        order[depth] = v;
        if (search(b, remaining ^ (1u << v), depth + 1)) return 1;
    }
    failed[remaining] = stamp;
    return 0;
}

/* No fill operations: use the original-path characterization of a torso. */
static int verify(const mask *a)
{
    mask used = 0, full = (1u << size) - 1;
    for (int i = 0; i < size; ++i) {
        int v = order[i];
        if (v < 0 || v >= size || (used & (1u << v))) return 0;
        mask reached = 0, todo = a[v] & used, neighbors = a[v];
        while (todo) {
            int w = first(todo);
            todo ^= 1u << w;
            reached |= 1u << w;
            neighbors |= a[w];
            todo |= a[w] & used & ~reached;
        }
        if (pc(neighbors & (full ^ used) & ~(1u << v)) > target) return 0;
        used |= 1u << v;
    }
    return used == full;
}

static int check(const mask *a, int n, int width)
{
    assert(n >= 1 && n <= TW_MAXN);
    size = n; target = width; ++stamp; ++total;
    int edges = 0;
    for (int v = 0; v < n; ++v) edges += pc(a[v]);
    ++edge_counts[edges / 2];
    int yes = greedy(a);
    if (yes) ++greedy_ok;
    else if ((yes = search(a, (1u << n) - 1, 0))) ++searched_ok;
    if (yes) {
        if (!verify(a)) { fputs("ORDER VERIFICATION FAILED\n", stderr); abort(); }
        ++verified;
    } else ++counterexamples;
    return yes;
}

#ifndef STANDALONE
void tw_out(FILE *f, graph *g, int n)
{
    static FILE *hard = NULL;
    static int initialized = 0;
    if (!initialized) {
        const char *path = getenv("TW_HARD_CASES");
        if (path && !(hard = fopen(path, "w"))) { perror(path); abort(); }
        initialized = 1;
    }
    mask a[TW_MAXN] = {0};
    assert(n <= TW_MAXN);
    for (int v = 0; v < n; ++v)
        for (int w = 0; w < n; ++w)
            if (ISELEMENT(g + v, w)) a[v] |= 1u << w;
    uint64_t before = greedy_ok;
    int yes = check(a, n, TW_TARGET);
    if (!yes) { writeg6(f, g, 1, n); fflush(f); }
    if (hard && greedy_ok == before) {
        char *encoding = ntog6(g, 1, n);
        encoding[strcspn(encoding, "\n")] = '\0';
        fprintf(hard, "%s", encoding);
        if (yes) for (int i = 0; i < n; ++i) fprintf(hard, " %d", order[i]);
        else fprintf(hard, " NO");
        fputc('\n', hard);
    }
}

void tw_summary(nauty_counter nout, double cpu)
{
    if ((uint64_t)nout != total) { fputs("COUNT MISMATCH\n", stderr); abort(); }
    fprintf(stderr, "TW_RESULT {\"n\":%d,\"width\":%d,\"total\":%llu,"
        "\"greedy\":%llu,\"search\":%llu,\"verified\":%llu,"
        "\"counterexamples\":%llu,\"cpu_seconds\":%.3f,\"edges\":{",
        size, TW_TARGET, (unsigned long long)total, (unsigned long long)greedy_ok,
        (unsigned long long)searched_ok, (unsigned long long)verified,
        (unsigned long long)counterexamples, cpu);
    int comma = 0;
    for (int m = 0; m < 100; ++m) if (edge_counts[m]) {
        fprintf(stderr, "%s\"%d\":%llu", comma ? "," : "", m,
                (unsigned long long)edge_counts[m]);
        comma = 1;
    }
    fputs("}}\n", stderr);
}
#else
int main(int argc, char **argv)
{
    if (argc != 2) { fputs("usage: treewidth-check WIDTH < graphs.g6\n", stderr); return 2; }
    int width = atoi(argv[1]);
    char line[256];
    while (fgets(line, sizeof(line), stdin)) {
        int n = (unsigned char)line[0] - 63;
        if (n < 1 || n > TW_MAXN || strlen(line) < (size_t)(1 + (n * (n - 1) / 2 + 5) / 6)) return 2;
        mask a[TW_MAXN] = {0};
        int bit = 0;
        for (int j = 1; j < n; ++j) for (int i = 0; i < j; ++i, ++bit) {
            if (((line[1 + bit / 6] - 63) >> (5 - bit % 6)) & 1) {
                a[i] |= 1u << j; a[j] |= 1u << i;
            }
        }
        if (!check(a, n, width)) puts("NO");
        else {
            printf("YES");
            for (int i = 0; i < n; ++i) printf(" %d", order[i]);
            putchar('\n');
        }
    }
    return 0;
}
#endif
