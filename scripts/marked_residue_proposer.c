/* Untrusted finite reconstruction proposer. Python independently regenerates
 * all choices and checks every emitted order or exact exception mapping. */
#define STANDALONE
#define TW_MAXN 22
#define main original_treewidth_main
#include "treewidth.c"
#undef main
#include <limits.h>
#include <inttypes.h>
#include <time.h>
typedef mask M;
#define N 22
#define PC(x) pc(x)
#define FIRST(x) first(x)
#include "exception.h"
#include "marked_residue_exception_map.inc"

static uint64_t inverse_choices, target_choices, order_proofs, exception_proofs;
static uint64_t target_limit;
static int count_only, stopped, unknown, base_index, base_n, subdivisions, edge_count;
static mask base_graph[22];
static int edge_list[36][2], matching[4];

static int target_family(const mask *a,mask new_cubics) {
    int lows[4],count=0;mask low_set=0;
    for(int v=0;v<22;++v) {
        int degree=pc(a[v]);
        if(degree==3) {
            if(count==4)abort();lows[count++]=v;low_set|=1u<<v;
        } else if(degree!=4)abort();
    }
    if(count!=4)abort();
    int twice_edges=0;
    for(int i=0;i<4;++i) {
        int v=lows[i];twice_edges+=pc(a[v]&low_set);
        for(mask q=a[v];q;q&=q-1)if(a[first(q)]&a[v])return 0;
        for(int j=0;j<i;++j)if(pc(a[v]&a[lows[j]])>1)return 0;
    }
    if(twice_edges>=8)return 0;
    int bipartite=0;
    for(int i=0;i<4;++i)for(int j=i+1;j<4;++j) {
        mask side=(1u<<lows[i])|(1u<<lows[j]);int valid=1;
        for(int k=0;k<4;++k) {
            int v=lows[k];mask own=side&(1u<<v)?side:low_set^side;
            if(a[v]&own){valid=0;break;}
        }
        if(valid)bipartite=1;
    }
    if(!bipartite)return 0;
    for(int bits=1;bits<16;++bits) {
        mask chosen=0;for(int i=0;i<4;++i)if(bits&(1<<i))chosen|=1u<<lows[i];
        if(pc(chosen&new_cubics)<2)continue;
        int valid=1;
        for(int i=0;i<4;++i) {
            int v=lows[i],neighbors=pc(a[v]&chosen);
            if(neighbors!=(chosen&(1u<<v)?0:1)){valid=0;break;}
        }
        if(valid)return 1;
    }
    return 0;
}

static void process_matching(mask restored) {
    ++inverse_choices;
    mask a[22];memcpy(a,base_graph,sizeof a);mask new_cubics=0;
    for(int i=0;i<subdivisions;++i) {
        int u=edge_list[matching[i]][0],v=edge_list[matching[i]][1],z=base_n+i;
        new_cubics|=1u<<z;
        a[u]=(a[u]&~(1u<<v))|(1u<<z);
        a[v]=(a[v]&~(1u<<u))|(1u<<z);
        a[z]=(1u<<u)|(1u<<v)|(1u<<21);a[21]|=1u<<z;
    }
    for(mask q=restored;q;q&=q-1){int v=first(q);a[v]|=1u<<21;a[21]|=1u<<v;}
    if(!target_family(a,new_cubics))return;
    if(target_limit&&target_choices==target_limit){stopped=1;return;}
    ++target_choices;
    if(count_only)return;
    size=22;target=8;
    if(greedy(a)) {
        if(!verify(a))abort();
        if(putchar(0)==EOF){stopped=1;return;}
        for(int i=0;i<22;++i)if(putchar(order[i])==EOF){stopped=1;return;}
        ++order_proofs;return;
    }
    int permutation[22];
    if(exception_map(a,permutation)) {
        if(putchar(1)==EOF){stopped=1;return;}
        for(int i=0;i<22;++i)if(putchar(permutation[i])==EOF){stopped=1;return;}
        ++exception_proofs;return;
    }
    if(!check(a,22,8)) {
        fprintf(stderr,"UNRESOLVED base=%d inverse=%"PRIu64,base_index,inverse_choices);
        for(int v=0;v<22;++v)fprintf(stderr," %u",a[v]);fputc('\n',stderr);
        unknown=stopped=1;return;
    }
    if(putchar(0)==EOF){stopped=1;return;}
    for(int i=0;i<22;++i)if(putchar(order[i])==EOF){stopped=1;return;}
    ++order_proofs;
}

static void choose_matching(int start,int chosen,mask used,mask restored) {
    if(stopped)return;
    if(chosen==subdivisions){process_matching(restored);return;}
    for(int i=start;i<=edge_count-(subdivisions-chosen);++i) {
        mask endpoints=(1u<<edge_list[i][0])|(1u<<edge_list[i][1]);
        if(endpoints&(used|restored))continue;
        matching[chosen]=i;
        choose_matching(i+1,chosen+1,used|endpoints,restored);
        if(stopped)return;
    }
}

int main(int argc,char **argv) {
    for(int i=1;i<argc;++i) {
        if(!strcmp(argv[i],"--count-only")&&!count_only)count_only=1;
        else if(!strcmp(argv[i],"--max-targets")&&!target_limit&&i+1<argc) {
            char *end;errno=0;target_limit=strtoull(argv[++i],&end,10);
            if(errno||end==argv[i]||*end||!target_limit||argv[i][0]=='-')return 1;
        } else return 1;
    }
    clock_t started=clock();
    if(!count_only&&fwrite("TW42R\1",1,6,stdout)!=6)return 1;
    char line[256];
    while(!stopped&&(base_n=read_graph6(line,sizeof line))>0) {
        if(base_n<17||base_n>19)return 1;
        subdivisions=21-base_n;memset(base_graph,0,sizeof base_graph);
        int bit=0;
        for(int v=1;v<base_n;++v)for(int u=0;u<v;++u,++bit)
            if((line[1+bit/6]-63)>>(5-bit%6)&1){base_graph[u]|=1u<<v;base_graph[v]|=1u<<u;}
        int cubics[4],nlow=0;edge_count=0;
        for(int u=0;u<base_n;++u) {
            if(pc(base_graph[u])==3){if(nlow==4)return 1;cubics[nlow++]=u;}
            else if(pc(base_graph[u])!=4)return 1;
            for(int v=u+1;v<base_n;++v)if(base_graph[u]&(1u<<v)) {
                if(edge_count==36)return 1;
                edge_list[edge_count][0]=u;edge_list[edge_count++][1]=v;
            }
        }
        if(nlow!=8-2*subdivisions||edge_count!=38-subdivisions)return 1;
        int restored=4-subdivisions;
        if(!restored)choose_matching(0,0,0,0);
        else if(restored==1)for(int i=0;i<nlow&&!stopped;++i)choose_matching(0,0,0,1u<<cubics[i]);
        else for(int i=0;i<nlow&&!stopped;++i)for(int j=i+1;j<nlow&&!stopped;++j)
            choose_matching(0,0,0,(1u<<cubics[i])|(1u<<cubics[j]));
        ++base_index;
    }
    if(fflush(stdout)||ferror(stdout))return 1;
    fprintf(stderr,"%s bases=%d inverse=%"PRIu64" target=%"PRIu64" orders=%"PRIu64" exceptions=%"PRIu64" exact_searches=%"PRIu64" cpu=%.3f\n",
            stopped?"INCOMPLETE":"COMPLETE",base_index,inverse_choices,target_choices,order_proofs,exception_proofs,total,(double)(clock()-started)/CLOCKS_PER_SEC);
    return unknown?3:stopped?2:base_n<0||base_index!=467?1:0;
}
