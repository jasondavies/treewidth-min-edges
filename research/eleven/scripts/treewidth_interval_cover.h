/* Uniform cover from an already reduced interval state. */
#include <stdint.h>
#include <string.h>
#include <assert.h>
static int interval_cover(const uint32_t *initial_known,const uint32_t *initial_possible,const int *initial_bound,int count,uint32_t remaining,int width,int *result){
    uint32_t known[26],possible[26];int bound[26];
    memcpy(known,initial_known,count*sizeof *known);
    memcpy(possible,initial_possible,count*sizeof *possible);
    memcpy(bound,initial_bound,count*sizeof *bound);
    int trial=0;
    for(int step=0;remaining;step++){
        int changed;
        do{
            changed=0;
            for(uint32_t t=remaining;t;t&=t-1){
                int v=__builtin_ctz(t),cap=__builtin_popcount(possible[v]&remaining);
                if(bound[v]>cap)bound[v]=cap;
                assert(bound[v]>=__builtin_popcount(known[v]&remaining));
                if(bound[v]==__builtin_popcount(known[v]&remaining)){
                    uint32_t remove=possible[v]&remaining&~known[v];
                    if(remove)changed=1;
                    for(uint32_t q=remove;q;q&=q-1)possible[__builtin_ctz(q)]&=~(1u<<v);
                    possible[v]&=~remove;
                }
            }
        }while(changed);
        int v=-1,score=100000;
        int skip=(step==0&&trial<5)?trial:(step==1&&trial>=5)?trial-4:0;
        uint32_t candidates=remaining;
        do {
        v=-1;score=100000;
        for(uint32_t t=candidates;t;t&=t-1){
            int u=__builtin_ctz(t);
            if(bound[u]<=width){
                int candidate=32*__builtin_popcount(possible[u]&remaining)+bound[u];
                if(candidate<score){v=u;score=candidate;}
            }
        }
        if(v<0)return 0;
        candidates^=1u<<v;
        }while(skip--);
        result[step]=v;
        uint32_t kv=known[v]&remaining,pv=possible[v]&remaining;
        int dv=bound[v];
        for(uint32_t t=pv;t;t&=t-1){
            int u=__builtin_ctz(t),added=__builtin_popcount(pv&~known[u]&~(1u<<u));
            int slots=dv-1-__builtin_popcount(kv&known[u]);
            if(added>slots)added=slots;
            int next=bound[u]-1+added;
            if(!(kv&(1u<<u))&&next<bound[u])next=bound[u];
            bound[u]=next;
        }
        for(uint32_t t=kv;t;t&=t-1){int u=__builtin_ctz(t);known[u]|=kv&~(1u<<u);}
        for(uint32_t t=pv;t;t&=t-1){int u=__builtin_ctz(t);possible[u]|=pv&~(1u<<u);}
        remaining^=1u<<v;
    }
    return 1;
}
