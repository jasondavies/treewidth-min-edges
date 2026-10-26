/* Reconstruct a quartic 20-vertex graph from a 30-edge order-16 residue.
 * Input: graph6, degrees 3,3,3,3,4,...,4. Choose two edges to subdivide;
 * add opposite cycle vertices and partition the four deficient vertices.
 */
#define STANDALONE
#define TW_MAXN 20
#define main unused_checker_main
#include "treewidth_edge_geng.c"
#undef main
int main(void)
{
    char line[256];uint64_t inputs=0;
    while(fgets(line,sizeof line,stdin)) {
        assert(line[0]=='O');mask original[20]={0};int bit=0,edges[30][2],ne=0,low[4],nl=0;
        for(int v=1;v<16;++v)for(int u=0;u<v;++u,++bit)
            if(((line[1+bit/6]-63)>>(5-bit%6))&1) {
                original[u]|=1u<<v;original[v]|=1u<<u;
                assert(ne<30);edges[ne][0]=u;edges[ne++][1]=v;
            }
        assert(ne==30);
        for(int v=0;v<16;++v)if(pc(original[v])==3){assert(nl<4);low[nl++]=v;}else assert(pc(original[v])==4);
        assert(nl==4);++inputs;
        for(int i=0;i<29;++i)for(int j=i+1;j<30;++j)for(int partner=1;partner<4;++partner) {
            mask a[20];memcpy(a,original,sizeof a);int chosen[2]={i,j};
            for(int q=0;q<2;++q) {
                int u=edges[chosen[q]][0],v=edges[chosen[q]][1],z=16+q;
                a[u]^=1u<<v;a[v]^=1u<<u;int ns[4]={u,v,18,19};
                for(int r=0;r<4;++r){a[z]|=1u<<ns[r];a[ns[r]]|=1u<<z;}
            }
            for(int q=0;q<4;++q){int z=(q==0 || q==partner)?18:19;a[z]|=1u<<low[q];a[low[q]]|=1u<<z;}
            for(int v=0;v<20;++v)assert(pc(a[v])==4);
            if(!check(a,20,8)) {
                int value=0,used=0;putchar(83);
                for(int v=1;v<20;++v)for(int u=0;u<v;++u) {
                    value=(value<<1)|!!(a[u]&(1u<<v));
                    if(++used==6){putchar(63+value);used=value=0;}
                }
                if(used)putchar(63+(value<<(6-used)));
                putchar('\n');fflush(stdout);return 10;
            }
        }
    }
    fprintf(stderr,"FOUR_CYCLE {\"inputs\":%llu,\"graphs\":%llu,\"verified\":%llu}\n",
            (unsigned long long)inputs,(unsigned long long)total,(unsigned long long)verified);
    return 0;
}
