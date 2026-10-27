/* Reverse deletion of opposite vertices of a four-cycle in a quartic
 * 23-vertex graph. Their r=2,3,4 common neighbors are smoothed, leaving
 * 38-r edges on 21-r vertices. All successful orders are verified. */
#define STANDALONE
#define TW_MAXN 23
#define main unused_checker_main
#include "../nine/treewidth_edge_geng.c"
#undef main
static mask original[TW_MAXN];
static int r,n,ne,nlow,edges[36][2],low[4],selected[4];
static uint64_t inputs;

static void emit(const mask *a)
{
    int value=0,bits=0;putchar(63+23);
    for(int v=1;v<23;++v)for(int u=0;u<v;++u) {
        value=(value<<1)|!!(a[u]&(1u<<v));
        if(++bits==6){putchar(63+value);bits=value=0;}
    }
    if(bits)putchar(63+(value<<(6-bits)));
    putchar('\n');fflush(stdout);
}

static void construct(void)
{
    int partitions=r==2?3:1;
    for(int partner=1;partner<=partitions;++partner) {
        mask a[TW_MAXN];memcpy(a,original,sizeof a);
        for(int j=0;j<r;++j) {
            int u=edges[selected[j]][0],v=edges[selected[j]][1],z=n+j;
            a[u]^=1u<<v;a[v]^=1u<<u;
            int ns[4]={u,v,21,22};
            for(int k=0;k<4;++k){a[z]|=1u<<ns[k];a[ns[k]]|=1u<<z;}
        }
        for(int j=0;j<nlow;++j) {
            int hub=(r==2?(j==0||j==partner):j==0)?21:22;
            a[hub]|=1u<<low[j];a[low[j]]|=1u<<hub;
        }
        for(int v=0;v<23;++v)assert(pc(a[v])==4);
        if(!check(a,23,9))emit(a);
    }
}

static void choose(int depth,int next)
{
    if(depth==r){construct();return;}
    for(int i=next;i<=ne-(r-depth);++i){selected[depth]=i;choose(depth+1,i+1);}
}

int main(int argc,char **argv)
{
    if(argc!=2 || (r=atoi(argv[1]))<2 || r>4)return 2;
    char line[256];n=21-r;
    while(fgets(line,sizeof line,stdin)) {
        assert(line[0]==63+n);memset(original,0,sizeof original);ne=nlow=0;int bit=0;
        for(int v=1;v<n;++v)for(int u=0;u<v;++u,++bit)
            if(((line[1+bit/6]-63)>>(5-bit%6))&1) {
                original[u]|=1u<<v;original[v]|=1u<<u;
                assert(ne<36);edges[ne][0]=u;edges[ne++][1]=v;
            }
        assert(ne==38-r);
        for(int v=0;v<n;++v)if(pc(original[v])==3){assert(nlow<4);low[nlow++]=v;}
            else assert(pc(original[v])==4);
        assert(nlow==2*(4-r));++inputs;choose(0,0);
    }
    if(ferror(stdin))return 2;
    fprintf(stderr,"RESULT {\"inputs\":%llu,\"graphs\":%llu,\"verified\":%llu,\"candidates\":%llu}\n",
            (unsigned long long)inputs,(unsigned long long)total,
            (unsigned long long)verified,(unsigned long long)counterexamples);
    return 0;
}
