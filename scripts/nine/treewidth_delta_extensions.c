/* Invert a degree-three elimination on every triangle. Retain KEEP of its
 * edges, add a star, and check the resulting graph. Full inverse moves
 * (KEEP=0) preserve edges; partial moves add KEEP edges.
 * Usage: delta_extensions KEEP WIDTH FIRST LAST DEGREE_CAP THREES_CAP
 * Viability bounds concern subsequent full moves to the requested class.
 */
#define STANDALONE
#define TW_MAXN 20
#define main unused_checker_main
#include "treewidth_edge_geng.c"
#undef main
static int first_order,last_order,cap,threes_cap;

static int viable(const mask *a,int n)
{
    if(n>last_order)return 0;
    int threes=0,excess=0,remaining=last_order-n;
    for(int v=0;v<n;++v) {
        int d=pc(a[v]);if(d<3 || d>cap+remaining)return 0;
        threes+=d==3;if(d>cap)excess+=d-cap;
    }
    return threes+(n<first_order?first_order-n:0)<=threes_cap && excess<=3*remaining;
}

static void emit(const mask *a,int n)
{
    int value=0,used=0;putchar(63+n);
    for(int v=1;v<n;++v)for(int u=0;u<v;++u) {
        value=(value<<1)|!!(a[u]&(1u<<v));
        if(++used==6){putchar(63+value);used=value=0;}
    }
    if(used)putchar(63+(value<<(6-used)));
    putchar('\n');
}

int main(int argc,char **argv)
{
    if(argc!=7)return 2;
    int args[6];char *end;
    for(int i=0;i<6;++i){args[i]=(int)strtol(argv[i+1],&end,10);if(*end)return 2;}
    int keep=args[0],width=args[1];first_order=args[2];last_order=args[3];cap=args[4];threes_cap=args[5];
    if(keep<0 || keep>3 || width<1 || width>19 || first_order<1 || last_order>20
       || first_order>last_order || cap<3 || threes_cap<0)return 2;
    char line[256];uint64_t inputs=0;
    while(fgets(line,sizeof line,stdin)) {
        int n=(unsigned char)line[0]-63;assert(n>=1 && n<=20);++inputs;
        if(n>=last_order)continue;
        assert(strlen(line)>=(size_t)(1+(n*(n-1)/2+5)/6));
        mask original[20]={0};int bit=0;
        for(int v=1;v<n;++v)for(int u=0;u<v;++u,++bit)
            if(((line[1+bit/6]-63)>>(5-bit%6))&1){original[u]|=1u<<v;original[v]|=1u<<u;}
        for(int u=0;u<n;++u)for(int v=u+1;v<n;++v)if(original[u]&(1u<<v))
            for(int w=v+1;w<n;++w)if((original[u]&original[v])&(1u<<w)) {
                int ends[3][2]={{u,v},{u,w},{v,w}};
                for(unsigned kept=0;kept<8;++kept)if(pc(kept)==keep) {
                    mask a[20];memcpy(a,original,sizeof a);
                    for(int e=0;e<3;++e)if(!(kept&(1u<<e))) {
                        int x=ends[e][0],y=ends[e][1];a[x]^=1u<<y;a[y]^=1u<<x;
                    }
                    a[n]=(1u<<u)|(1u<<v)|(1u<<w);a[u]|=1u<<n;a[v]|=1u<<n;a[w]|=1u<<n;
                    if(viable(a,n+1) && !check(a,n+1,width))emit(a,n+1);
                }
            }
    }
    fprintf(stderr,"DELTA_EXTENSIONS {\"inputs\":%llu,\"graphs\":%llu,\"verified\":%llu,\"retained\":%llu}\n",
            (unsigned long long)inputs,(unsigned long long)total,(unsigned long long)verified,(unsigned long long)counterexamples);
    return 0;
}
