/* Append a maximum-degree vertex, requiring minimum degree four.
 * Retain only graphs whose treewidth exceeds the supplied bound.
 * Every discarded graph has an independently verified positive order.
 * Usage: core_extensions DEGREE OUTPUT_EDGES WIDTH < bases.g6
 */
#define STANDALONE
#define TW_MAXN 20
#define main unused_checker_main
#include "treewidth_edge_geng.c"
#undef main
static int n,added,width;static mask current[20];

static void emit(void)
{
    int value=0,used=0;putchar(64+n);
    for(int v=1;v<=n;++v)for(int u=0;u<v;++u) {
        value=(value<<1)|!!(current[u]&(1u<<v));
        if(++used==6){putchar(63+value);used=value=0;}
    }
    if(used)putchar(63+(value<<(6-used)));
    putchar('\n');
}

static void choose(mask eligible,int need,mask selected)
{
    if(!need) {
        current[n]=selected;
        for(mask t=selected;t;t&=t-1)current[first(t)]|=1u<<n;
        if(!check(current,n+1,width))emit();
        for(mask t=selected;t;t&=t-1)current[first(t)]^=1u<<n;
        current[n]=0;return;
    }
    while(pc(eligible)>=need) {
        int v=first(eligible);eligible&=eligible-1;
        choose(eligible,need-1,selected|(1u<<v));
    }
}

int main(int argc,char **argv)
{
    if(argc!=4)return 2;
    char *end;added=(int)strtol(argv[1],&end,10);if(*end || added<4 || added>19)return 2;
    int expected=(int)strtol(argv[2],&end,10);if(*end || expected<1 || expected>=100)return 2;
    width=(int)strtol(argv[3],&end,10);if(*end || width<1 || width>19)return 2;
    char line[256];uint64_t inputs=0,eligible_inputs=0;
    while(fgets(line,sizeof line,stdin)) {
        n=(unsigned char)line[0]-63;assert(n>=1 && n<20);
        assert(strlen(line)>=(size_t)(1+(n*(n-1)/2+5)/6));
        memset(current,0,sizeof current);int bit=0,edges=0;
        for(int v=1;v<n;++v)for(int u=0;u<v;++u,++bit)
            if(((line[1+bit/6]-63)>>(5-bit%6))&1) {
                current[u]|=1u<<v;current[v]|=1u<<u;++edges;
            }
        assert(edges+added==expected);++inputs;
        mask required=0,optional=0;int valid=1;
        for(int v=0;v<n;++v) {
            int d=pc(current[v]);assert(d>=3);
            if(d>added)valid=0;
            if(d==3)required|=1u<<v;
            else if(d<added)optional|=1u<<v;
        }
        if(!valid || pc(required)>added || pc(required|optional)<added)continue;
        ++eligible_inputs;choose(optional,added-pc(required),required);
    }
    fprintf(stderr,"CORE_EXTENSIONS {\"inputs\":%llu,\"eligible_inputs\":%llu,\"graphs\":%llu,\"verified\":%llu,\"retained\":%llu}\n",
            (unsigned long long)inputs,(unsigned long long)eligible_inputs,
            (unsigned long long)total,(unsigned long long)verified,(unsigned long long)counterexamples);
    return 0;
}
