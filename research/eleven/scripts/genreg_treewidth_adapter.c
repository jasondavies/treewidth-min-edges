/* GENREG callback adapter. The external generator is downloaded separately.
 * Every positive leaf and supergraph order is checked independently using
 * paths in the original graph, via the shared checker.
 */
#define STANDALONE
#define TW_MAXN 20
#define main unused_checker_main
#include "treewidth_edge_geng.c"
#undef main
#ifndef GENREG_WIDTH
#define GENREG_WIDTH 8
#endif
#ifndef GENREG_CAP
#define GENREG_CAP -1
#endif
#ifndef GENREG_COVER
#define GENREG_COVER 0
#endif
#ifndef GENREG_STOP
#define GENREG_STOP 0
#endif
static uint64_t genreg_covers,genreg_attempts,genreg_triangle_prunes,genreg_leaves;

static void genreg_masks(int n,int **g,mask *a)
{
    assert(n>=1 && n<=TW_MAXN);
    for(int v=0;v<n;++v) {
        a[v]=0;
        for(int w=0;w<n;++w) if(g[v+1][w+1])a[v]|=1u<<w;
    }
}

static void genreg_emit(const mask *a,int n)
{
    int value=0,used=0;putchar(63+n);
    for(int j=1;j<n;++j)for(int i=0;i<j;++i) {
        value=(value<<1)|!!(a[i]&(1u<<j));
        if(++used==6){putchar(63+value);value=used=0;}
    }
    if(used)putchar(63+(value<<(6-used)));
    putchar('\n');fflush(stdout);
}

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
    size=n;target=GENREG_WIDTH;++genreg_attempts;
    if(!greedy(upper))return 0;
    if(!verify(upper)){fputs("GENREG COVER VERIFICATION FAILED\n",stderr);abort();}
    ++genreg_covers;return 1;
}

void genreg_tw_leaf(int n,int d,int **g)
{
    mask a[TW_MAXN];genreg_masks(n,g,a);++genreg_leaves;
    for(int v=0;v<n;++v)assert(pc(a[v])==d);
    if(!check(a,n,GENREG_WIDTH)) {
        genreg_emit(a,n);
        if(GENREG_STOP)exit(10);
    }
}

void genreg_tw_summary(unsigned long count)
{
    assert(count==genreg_leaves && total==genreg_leaves);
    fprintf(stderr,"GENREG_TW {\"leaves\":%llu,\"verified\":%llu,\"negative\":%llu,"
            "\"covers\":%llu,\"attempts\":%llu,\"triangle_prunes\":%llu}\n",
            (unsigned long long)genreg_leaves,(unsigned long long)verified,
            (unsigned long long)counterexamples,(unsigned long long)genreg_covers,
            (unsigned long long)genreg_attempts,(unsigned long long)genreg_triangle_prunes);
}
