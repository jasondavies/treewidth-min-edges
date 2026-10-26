/* A partial graph on n vertices of width <= k-(N-n) cannot extend to an
 * N-vertex graph of width >k: add the missing vertices to every bag.
 * Each successful prefix order is independently verified. Failed bounded
 * searches are inconclusive and never prune a branch.
 */
#include "treewidth_edge_geng.c"
static uint64_t prefix_attempts,prefix_covers,prefix_search_covers;
static int prefix_maxn;
#ifndef PREFIX_BUDGET
#define PREFIX_BUDGET 0
#endif
static int budget;

static int limited_search(const mask *a,mask remaining,int depth)
{
    if(!remaining)return 1;
    if(failed[remaining]==stamp)return 0;
    if(--budget<0)return -1;
    for(mask t=remaining;t;t&=t-1) {
        int v=first(t);
        if(pc(a[v]&remaining)>target)continue;
        mask b[TW_MAXN];memcpy(b,a,size*sizeof(mask));
        eliminate(b,remaining,v);order[depth]=v;
        int result=limited_search(b,remaining^(1u<<v),depth+1);
        if(result)return result;
    }
    failed[remaining]=stamp;return 0;
}

int prefix_prune(graph *g,int n,int maxn)
{
    prefix_maxn=maxn;
    int remaining=maxn-n;
    if(remaining<1 || remaining>2)return 0;
    mask a[TW_MAXN]={0};
    for(int v=0;v<n;++v)for(int w=0;w<n;++w)
        if(ISELEMENT(g+v,w))a[v]|=1u<<w;
    size=n;target=TW_TARGET-remaining;++prefix_attempts;
    int yes=greedy(a);
    if(!yes && PREFIX_BUDGET>0) {
        ++stamp;budget=PREFIX_BUDGET;
        yes=limited_search(a,(1u<<n)-1,0)==1;
        if(yes)++prefix_search_covers;
    }
    if(!yes)return 0;
    if(!verify(a)){fputs("PREFIX ORDER VERIFICATION FAILED\n",stderr);abort();}
    ++prefix_covers;return 1;
}

void prefix_summary(nauty_counter nout,double cpu)
{
    size=prefix_maxn;target=TW_TARGET;
    tw_summary(nout,cpu);
    fprintf(stderr,"PREFIX_RESULT {\"attempts\":%llu,\"covers\":%llu,\"search_covers\":%llu}\n",
            (unsigned long long)prefix_attempts,(unsigned long long)prefix_covers,
            (unsigned long long)prefix_search_covers);
}
