/* Append degree five to a 35-edge residue, requiring degrees four/five. */
#define STANDALONE
#define TW_MAXN 20
#define main unused_checker_main
#include "treewidth_edge_geng.c"
#undef main
int main(void)
{
    char line[256];uint64_t inputs=0;
    while(fgets(line,sizeof line,stdin)) {
        int n=(unsigned char)line[0]-63;assert(n>=15 && n<=18);
        mask original[20]={0},required=0,optional=0;int bit=0,edges=0;
        for(int v=1;v<n;++v)for(int u=0;u<v;++u,++bit)
            if(((line[1+bit/6]-63)>>(5-bit%6))&1){original[u]|=1u<<v;original[v]|=1u<<u;++edges;}
        assert(edges==35);++inputs;
        for(int v=0;v<n;++v) {
            int d=pc(original[v]);assert(d>=3 && d<=5);
            if(d==3)required|=1u<<v;
            if(d==4)optional|=1u<<v;
        }
        for(mask chosen=optional;;chosen=(chosen-1)&optional) {
            mask neighbors=chosen|required;
            if(pc(neighbors)==5) {
                mask a[20];memcpy(a,original,sizeof a);a[n]=neighbors;
                for(mask t=neighbors;t;t&=t-1)a[first(t)]|=1u<<n;
                if(!check(a,n+1,8)) {
                    int value=0,used=0;putchar(64+n);
                    for(int v=1;v<=n;++v)for(int u=0;u<v;++u) {
                        value=(value<<1)|!!(a[u]&(1u<<v));
                        if(++used==6){putchar(63+value);used=value=0;}
                    }
                    if(used)putchar(63+(value<<(6-used)));
                    putchar('\n');fflush(stdout);return 10;
                }
            }
            if(!chosen)break;
        }
    }
    fprintf(stderr,"FIVE_EXTENSION {\"inputs\":%llu,\"graphs\":%llu,\"verified\":%llu}\n",
            (unsigned long long)inputs,(unsigned long long)total,(unsigned long long)verified);
    return 0;
}
