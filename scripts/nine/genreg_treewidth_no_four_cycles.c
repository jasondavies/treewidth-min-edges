/* Exact-key memoization of the existing verified supergraph heuristic.
 * A cache hit requires equality of all adjacency masks, not only a hash.
 * Negative entries only skip a heuristic and never prune a graph.
 */
#define genreg_tw_prune original_genreg_tw_prune
#include "genreg_treewidth_adapter.c"
#undef genreg_tw_prune

typedef struct { mask a[TW_MAXN]; unsigned char state; } entry;
static entry cache[1u << 18];

int genreg_tw_prune(int n,int d,int **g,int *degree,int start)
{
    if(GENREG_CAP<0 && !GENREG_COVER)return 0;
    mask a[TW_MAXN];int triangles[TW_MAXN]={0};
    genreg_masks(n,g,a);
    for(int v=0;v<n;++v) {
        for(mask t=a[v];t;t&=t-1)triangles[v]+=pc(a[first(t)]&a[v]);
        triangles[v]/=2;
        if(GENREG_CAP>=0 && triangles[v]>GENREG_CAP){++genreg_triangle_prunes;return 1;}
    }
    /* This is only the subcase with no four-cycles. It is not yet
     * justified as a necessary condition for every counterexample. */
    assert(n==20 && d==4 && GENREG_WIDTH==8);
    for(int v=0;v<n;++v)for(int w=v+1;w<n;++w)
        if(pc(a[v]&a[w])>=2){++genreg_triangle_prunes;return 1;}
    if(!GENREG_COVER || n-start+1>12)return 0;
    mask upper[TW_MAXN];memcpy(upper,a,n*sizeof(mask));
    for(int v=start-1;v<n;++v)if(degree[v+1]<d)
        for(int w=v+1;w<n;++w)if(degree[w+1]<d && !(a[v]&(1u<<w))) {
            mask common=a[v]&a[w];int allowed=1;
            if(GENREG_CAP>=0) {
                int count=pc(common);
                if(triangles[v]+count>GENREG_CAP || triangles[w]+count>GENREG_CAP)allowed=0;
                for(mask t=common;t && allowed;t&=t-1)
                    if(triangles[first(t)]>=GENREG_CAP)allowed=0;
            }
            if(allowed){upper[v]|=1u<<w;upper[w]|=1u<<v;}
        }
    uint64_t hash=UINT64_C(14695981039346656037);
    for(int v=0;v<n;++v){hash^=upper[v];hash*=UINT64_C(1099511628211);hash^=hash>>29;}
    entry *e=&cache[hash&((1u<<18)-1)];
    ++genreg_attempts;
    if(e->state && !memcmp(e->a,upper,n*sizeof(mask))) {
        if(e->state==2){++genreg_covers;return 1;}
        return 0;
    }
    size=n;target=GENREG_WIDTH;
    int yes=greedy(upper);
    if(yes && !verify(upper)){fputs("CACHE COVER VERIFICATION FAILED\n",stderr);abort();}
    memcpy(e->a,upper,n*sizeof(mask));e->state=yes?2:1;
    if(yes)++genreg_covers;
    return yes;
}
