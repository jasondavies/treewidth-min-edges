/* Exploratory: add every nonedge to each quartic 23-vertex input. */
#define STANDALONE
#define TW_MAXN 23
#define main unused_checker_main
#include "../nine/treewidth_edge_geng.c"
#undef main
static void emit(const mask *a) {
    int value=0,bits=0;putchar(86);
    for(int v=1;v<23;++v)for(int u=0;u<v;++u) {
        value=(value<<1)|!!(a[u]&(1u<<v));
        if(++bits==6){putchar(63+value);bits=value=0;}
    }
    if(bits)putchar(63+(value<<(6-bits)));
    putchar('\n');fflush(stdout);
}
int main(void) {
    char line[256];uint64_t inputs=0;
    while(fgets(line,sizeof line,stdin)) {
        assert(line[0]==86);mask original[23]={0};int bit=0;
        for(int v=1;v<23;++v)for(int u=0;u<v;++u,++bit)
            if(((line[1+bit/6]-63)>>(5-bit%6))&1){original[u]|=1u<<v;original[v]|=1u<<u;}
        for(int v=0;v<23;++v)assert(pc(original[v])==4);
        ++inputs;
        for(int v=1;v<23;++v)for(int u=0;u<v;++u)if(!(original[u]&(1u<<v))) {
            mask a[23];memcpy(a,original,sizeof a);a[u]|=1u<<v;a[v]|=1u<<u;
            if(!check(a,23,9))emit(a);
        }
    }
    fprintf(stderr,"RESULT {\"inputs\":%llu,\"graphs\":%llu,\"verified\":%llu,\"candidates\":%llu}\n",
      (unsigned long long)inputs,(unsigned long long)total,(unsigned long long)verified,(unsigned long long)counterexamples);
}
