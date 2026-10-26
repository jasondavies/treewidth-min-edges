/* Prune regular-graph generation with verified upper supergraphs.
 * PRUNE returns true only for a forbidden triangle pattern or a partial
 * graph all of whose regular completions have width <=TW_TARGET.
 */
#include "treewidth_edge_geng.c"
#ifndef REGULAR_DEGREE
#define REGULAR_DEGREE 4
#endif
#ifndef COVER_LAST
#define COVER_LAST 4
#endif
static uint64_t regular_triangle_prunes,regular_covers,regular_attempts;

int regular_tw_prune(graph *g,int n,int maxn)
{
    mask a[TW_MAXN]={0};int degree[TW_MAXN]={0};
    assert(maxn<=TW_MAXN);
    for(int v=0;v<n;++v)for(int w=0;w<n;++w)
        if(ISELEMENT(g+v,w)){a[v]|=1u<<w;++degree[v];}
    const int cap=REGULAR_DEGREE==4?1:4;
    for(int v=0;v<n;++v) {
        int twice=0;
        for(mask t=a[v];t;t&=t-1)twice+=pc(a[first(t)]&a[v]);
        if(twice>2*cap){++regular_triangle_prunes;return 1;}
    }
    if(n<maxn-COVER_LAST)return 0;
    mask future=((1u<<maxn)-1)^((1u<<n)-1);
    for(int v=0;v<n;++v)if(degree[v]<REGULAR_DEGREE) {
        a[v]|=future;
        for(int w=n;w<maxn;++w)a[w]|=1u<<v;
    }
    for(int v=n;v<maxn;++v)a[v]|=future^(1u<<v);
    size=maxn;target=TW_TARGET;++regular_attempts;
    if(!greedy(a))return 0;
    if(!verify(a)){fputs("GENERATION COVER VERIFICATION FAILED\n",stderr);abort();}
    ++regular_covers;return 1;
}

void regular_summary(nauty_counter nout,double cpu)
{
    tw_summary(nout,cpu);
    fprintf(stderr,"REGULAR_PRUNES {\"triangle\":%llu,\"covers\":%llu,\"attempts\":%llu}\n",
            (unsigned long long)regular_triangle_prunes,(unsigned long long)regular_covers,
            (unsigned long long)regular_attempts);
}
