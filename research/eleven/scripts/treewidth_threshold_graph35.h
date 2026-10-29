/* See treewidth-eleven-additional-filters.md for the interval invariant. */
#include "treewidth_interval_cover.h"
#include "treewidth35_partial_graphs.h"
static int threshold_obstruction(const mask *original,const int *degrees,int count,int edge_count,int lower_width,const mask *forbidden){
    static const int minimum[]={0,1,3,6,10,15,21,28,34,42,47,52};
    mask initial_possible[26];memcpy(initial_possible,original,sizeof initial_possible);
    for(int u=0;u<count;u++)if(pc(original[u])<degrees[u])
        for(int v=u+1;v<count;v++)if(pc(original[v])<degrees[v]&&(!forbidden||!(forbidden[u]&(1u<<v))))edge(initial_possible,u,v);
    for(int policy=0;policy<2;policy++)for(int deleted=0;deleted<count;deleted++){
        mask known[26],possible[26],remaining=((1u<<count)-1)&~(1u<<deleted);
        int bound[26],edges=edge_count-degrees[deleted],width=lower_width-1;
        memcpy(known,original,sizeof known);memcpy(possible,initial_possible,sizeof possible);
        for(int v=0;v<count;v++)bound[v]=degrees[v]-!!(original[v]&(1u<<deleted));
        for(;;){
            if(edges<minimum[width])return 1;
            if(width<=1)break;
            if(width==8&&edges<=35&&!partial35_graph_possible(known,possible,bound,count,remaining,edges))return 1;
            /* The complete 34-edge, width-eight classification consists of
             * two triangle-free graphs on 16/17 vertices, plus isolates. */
            if(width==8&&edges==34){
                if(pc(remaining)<16)return 1;
                int nonisolated=0;
                for(mask t=remaining;t;t&=t-1){
                    int v=first(t);mask ns=known[v]&remaining;int d=pc(ns);
                    if(d){nonisolated++;if(d>5||bound[v]<4)return 1;}
                    for(mask q=ns;q;q&=q-1)if(known[first(q)]&ns)return 1;
                }
                if(nonisolated>17)return 1;
            }
            int changed;
            do{
                changed=0;
                for(mask t=remaining;t;t&=t-1){
                    int v=first(t),cap=pc(possible[v]&remaining),certain=pc(known[v]&remaining);
                    if(bound[v]>cap)bound[v]=cap;
                    assert(bound[v]>=certain);
                    if(bound[v]==certain){
                        mask remove=possible[v]&remaining&~known[v];if(remove)changed=1;
                        for(mask q=remove;q;q&=q-1)possible[first(q)]&=~(1u<<v);
                        possible[v]&=~remove;
                    }
                }
            }while(changed);
            int degree_sum=0,known_twice=0;
            for(mask t=remaining;t;t&=t-1){int v=first(t);degree_sum+=bound[v];known_twice+=pc(known[v]&remaining);}
            if(edges>degree_sum/2)edges=degree_sum/2;
            if(edges<minimum[width])return 1;
            mask unseen=remaining,only=0;int possible_components=0,only_edges=0;
            while(unseen){
                mask component=0,todo=unseen&-unseen;
                while(todo){int v=first(todo);todo&=todo-1;component|=1u<<v;todo|=possible[v]&remaining&~component;}
                unseen&=~component;int sum=0,inside_twice=0;
                for(mask t=component;t;t&=t-1){int v=first(t);sum+=bound[v];inside_twice+=pc(known[v]&component);}
                int cap=edges-(known_twice-inside_twice)/2;if(cap>sum/2)cap=sum/2;
                if(pc(component)>width&&cap>=minimum[width]){possible_components++;only=component;only_edges=cap;}
            }
            if(!possible_components)return 1;
            if(possible_components==1&&only!=remaining){remaining=only;edges=only_edges;continue;}
            int next=-1,highest=-1,maximum=0,best_score=100000;
            for(mask t=remaining;t;t&=t-1){
                int v=first(t),d=pc(known[v]&remaining);
                if(d>edges-minimum[width-1])return 1;
                if(d>maximum){highest=v;maximum=d;}
                if(bound[v]<width&&(policy||bound[v]<=3)){
                    int score=32*pc(possible[v]&remaining)+bound[v];
                    if(!policy||score<best_score){next=v;best_score=score;}
                }
            }
            if(next<0){
                int cover_order[26];
                if(interval_cover(known,possible,bound,count,remaining,width-1,cover_order))return 1;
                if(highest<0)break;
                for(mask t=known[highest]&remaining;t;t&=t-1)bound[first(t)]--;
                remaining^=1u<<highest;edges-=maximum;width--;continue;
            }
            mask kv=known[next]&remaining,pv=possible[next]&remaining;
            int dv=bound[next],twice=0;
            for(mask t=kv;t;t&=t-1)twice+=pc(known[first(t)]&kv);
            int change=-100;
            for(int d=pc(kv);d<=dv;d++){
                int value=d*(d-1)/2-d-twice/2;
                if(value>change)change=value;
            }
            edges+=change;
            for(mask t=pv;t;t&=t-1){
                int u=first(t),added=pc(pv&~known[u]&~(1u<<u));
                int slots=dv-1-pc(kv&known[u]);if(added>slots)added=slots;
                int value=bound[u]-1+added;
                if(!(kv&(1u<<u))&&value<bound[u])value=bound[u];
                bound[u]=value;
            }
            for(mask t=kv;t;t&=t-1){int u=first(t);known[u]|=kv&~(1u<<u);}
            for(mask t=pv;t;t&=t-1){int u=first(t);possible[u]|=pv&~(1u<<u);}
            remaining^=1u<<next;
        }
    }
    return 0;
}
