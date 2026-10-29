/* A bounded search for an embedding of a 34/35-edge obstruction into an
 * interval graph. Exhaustion proves incompatibility; budget exhaustion
 * explicitly returns unknown, and therefore never prunes. */
#include "treewidth35_graph_data.h"
static int small35_embedding(const mask *tk,int m,const mask *known,const mask *possible,
                            const mask *options,mask remaining,mask used,mask mandatory,int *budget){
    if(!remaining)return !(mandatory&~used);
    if(!*budget)return -1;
    --*budget;
    mask available_union=0;int next=-1,best=100;
    for(mask t=remaining;t;t&=t-1){int u=first(t),count=pc(options[u]);
        if(!count)return 0;available_union|=options[u];
        if(count<best){best=count;next=u;}
    }
    if(((mandatory&~used)&~available_union)||pc(mandatory&~used)>pc(remaining))return 0;
    for(mask t=options[next];t;t&=t-1){int v=first(t);mask following[26],left=remaining^(1u<<next);int valid=1;
        for(mask q=left;q;q&=q-1){int u=first(q);
            following[u]=options[u]&~(1u<<v)&((tk[next]&(1u<<u))?possible[v]:~known[v]);
            if(!following[u]){valid=0;break;}
        }
        if(!valid)continue;
        int result=small35_embedding(tk,m,known,possible,following,left,used|(1u<<v),mandatory,budget);
        if(result)return result;
    }
    return 0;
}
static int partial35_graph_possible(const mask *known,const mask *possible,const int *bound,int count,mask remaining,int edge_limit){
    int lower[26]={0},upper[26]={0},tri_low[26]={0},tri_high[26]={0},sq_low[26]={0},sq_high[26]={0};mask mandatory=0;
    int n=pc(remaining),sum_tri=0,budget=2000;
    for(mask t=remaining;t;t&=t-1){int v=first(t);lower[v]=pc(known[v]&remaining);upper[v]=bound[v];
        int slots=pc(possible[v]&remaining);if(upper[v]>slots)upper[v]=slots;
        if(lower[v])mandatory|=1u<<v;
        for(mask q=known[v]&remaining;q;q&=q-1)tri_low[v]+=pc(known[first(q)]&known[v]&remaining);
        for(mask q=possible[v]&remaining;q;q&=q-1)tri_high[v]+=pc(possible[first(q)]&possible[v]&remaining);
        tri_low[v]/=2;tri_high[v]/=2;sum_tri+=tri_low[v];
        for(mask q=t&(t-1);q;q&=q-1){int w=first(q),lo=pc(known[v]&known[w]&remaining),hi=pc(possible[v]&possible[w]&remaining);
            sq_low[v]+=lo*(lo-1)/2;sq_low[w]+=lo*(lo-1)/2;sq_high[v]+=hi*(hi-1)/2;sq_high[w]+=hi*(hi-1)/2;
        }
    }
    if(pc(mandatory)>19)return 0;
    for(unsigned type=0;type<sizeof small35_graphs/sizeof *small35_graphs;type++){
        int m=small35_graphs[type].n;if(small35_graphs[type].edges>edge_limit||m>n||pc(mandatory)>m)continue;
        int total_tri=0;for(int u=0;u<m;u++)total_tri+=(small35_graphs[type].trait[u]>>3)&31;
        if(sum_tri>total_tri)continue;
        mask options[26]={0};int valid=1;
        for(int u=0;u<m;u++){
            unsigned trait=small35_graphs[type].trait[u];int d=trait&7,tri=(trait>>3)&31,square=trait>>8;
            for(mask t=remaining;t;t&=t-1){int v=first(t);
                if(d>=lower[v]&&d<=upper[v]&&tri>=tri_low[v]&&tri<=tri_high[v]&&square>=sq_low[v]&&square<=sq_high[v])options[u]|=1u<<v;
            }
            if(!options[u]){valid=0;break;}
        }
        if(!valid)continue;
        int result=small35_embedding(small35_graphs[type].a,m,known,possible,options,(1u<<m)-1,0,mandatory,&budget);
        if(result)return 1;
    }
    return 0;
}
