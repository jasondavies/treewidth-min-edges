/* Exhaust completions of the four disjoint-triangle templates. Symmetry
 * reduction fixes processed vertices and permutes indistinguishable future
 * vertices/whole triangles. Upper-bound pruning verifies every order. */
#define STANDALONE
#define TW_MAXN 26
#define main unused_checker_main
#include "treewidth_edge_geng.c"
#undef main
#include <time.h>
#include "treewidth_degree_cover_forbidden.h"

static mask adj[26], forbidden[26], low_mask;
static int max_four_cap;
static int n,kind,r,degree[26],split_depth=-1;
static uint64_t nodes,patterns,leaves,covers,filtered,residues,isomorphism_covers;
#ifndef PREFIX_CANONICAL_SEEN
#define PREFIX_CANONICAL_SEEN(a,n,r,d,v) 0
#endif
static int cover_orders[26][26],cover_valid[26];

static void edge(mask *a,int u,int v){a[u]|=1u<<v;a[v]|=1u<<u;}
static void emit(const mask *a,int count){
    int value=0,bits=0;putchar(63+count);
    for(int v=1;v<count;v++)for(int u=0;u<v;u++){
        value=(value<<1)|!!(a[u]&(1u<<v));
        if(++bits==6){putchar(63+value);bits=value=0;}
    }
    if(bits)putchar(63+(value<<(6-bits)));
    putchar('\n');fflush(stdout);
}
static void initialize(int family){
    assert(family>=22&&family<=26);kind=family;n=family;r=0;
    int fives=104-4*n;
    for(int v=0;v<n;v++)degree[v]=v<fives?5:4;
    low_mask=fives?(1u<<fives)-1:0; /* Here this denotes the high vertices. */
    assert(n==26);

}
/* The high-core exclusion forbids triangular square incidence and
 * forces an edge between opposite corners of disjoint square pairs.
 * The SAT/LRAT certificate also excludes P4 incidence.
 * Matching incidence remains allowed. */
static int forbidden_square_incidence_at(int v){
    for(mask t=adj[v];t;t&=t-1){int u=first(t);
        for(mask q=t&(t-1);q;q&=q-1){int w=first(q);if(pc(adj[u]&adj[w])<2)continue;
            for(mask z=q&(q-1);z;z&=z-1){int x=first(z);
                if(pc(adj[u]&adj[x])>=2&&pc(adj[w]&adj[x])>=2)return 1;
            }
        }
    }
    /* The independently checked SAT/LRAT certificate excludes a P4 in J
     * under the global cap of three squares through each vertex. */
    if(pc(adj[v])==4){
        int ns[4],i=0;mask j[4]={0};for(mask t=adj[v];t;t&=t-1)ns[i++]=first(t);
        for(int a=0;a<4;a++)for(int b=a+1;b<4;b++)
            if(pc(adj[ns[a]]&adj[ns[b]])>=2)edge(j,a,b);
        for(int b=0;b<4;b++)for(mask t=j[b];t;t&=t-1){int c=first(t);
            for(mask q=j[b]&~(1u<<c);q;q&=q-1){int a=first(q);
                if(j[c]&~((1u<<a)|(1u<<b)))return 1;
            }
        }
    }
    return 0;
}
static int forbidden_square_incidence_ball(void){
    for(int v=0;v<n;v++)if(forbidden_square_incidence_at(v))return 1;
    return 0;
}
static int extra_partial(void){
    if(forbidden_square_incidence_ball())return 0;

    int squares[26]={0};
    for(int u=0;u<n;u++)for(int v=u+1;v<n;v++){
        int common=pc(adj[u]&adj[v]&~low_mask);
        int limit=(degree[u]==4&&degree[v]==4)?2:1;
        if(common>limit)return 0;
        if(common==2&&(++squares[u]>max_four_cap||++squares[v]>max_four_cap))return 0;
    }
    for(int v=0;v<n;v++)if(degree[v]==4){
        mask high=adj[v]&low_mask;
        for(mask t=adj[v];t;t&=t-1){int u=first(t);
            for(mask q=adj[u]&adj[v]&t;q;q&=q-1){int w=first(q);
                if(high&~((1u<<u)|(1u<<w)))return 0;
            }
        }
    }
    return 1;
}
/* G-v has width at least ten. Eliminate only vertices whose entire
 * neighborhoods are known; use f(10)>=47 and f(9)>=42 after each step. */
#include "treewidth_threshold_graph35.h"
static int deletion_obstruction(void){return threshold_obstruction(adj,degree,n,52,11,forbidden);}
static int valid_partial(int start){
    if(!extra_partial())return 0;
    for(int v=0;v<n;v++){
        mask ns=adj[v],high=ns&low_mask;
        int twice=0;
        for(mask t=ns;t;t&=t-1)twice+=pc(adj[first(t)]&ns);
        if(twice>0)return 0;
        if(degree[v]==4&&pc(high)>2)return 0;
        for(mask t=high;t;t&=t-1){
            int x=first(t);
            for(mask q=t&(t-1);q;q&=q-1){
                int y=first(q);
                if((adj[x]&(1u<<y))||(x>=start&&y>=start))continue;
                if(degree[v]==4)return 0;
                mask other=ns&~((1u<<x)|(1u<<y));
                for(mask z=other;z;z&=z-1)if(adj[first(z)]&other)return 0;
            }
        }
    }
    return 1;
}
static int symmetry_ok(int v,mask chosen){
#ifndef NO_SYMMETRY
    for(mask t=chosen;t;t&=t-1){
        int w=first(t);
        for(int u=v+1;u<w;u++)if(degree[u]==degree[w]&&!(chosen&(1u<<u))
            &&!((adj[u]^adj[w])&~((1u<<u)|(1u<<w))))return 0;
    }

#endif
    return 1;
}
static void complete(int v);
static void complete_impl(int v);
static unsigned short allowed[6][1024];
static int allowed_count[6];
static void initialize_allowed(void){
    for(int h=3;h<=5;h++)for(int pattern=0;pattern<1024;pattern++){
        if(pc(pattern)>4)continue;
        mask local[5]={0};int bit=0;
        for(int j=1;j<5;j++)for(int i=0;i<j;i++,bit++)if(pattern&(1<<bit)){local[i]|=1u<<j;local[j]|=1u<<i;}
        int valid=1;
        for(int u=0;u<h;u++)for(int v=u+1;v<h;v++)if(!(local[u]&(1u<<v))){
            mask others=31u&~((1u<<u)|(1u<<v));
            for(mask t=others;t;t&=t-1)if(local[first(t)]&others)valid=0;
        }
        if(valid)allowed[h][allowed_count[h]++]=(unsigned short)pattern;
    }
}
static int force_edge(int u,int w,int start,int *changed){
    if(forbidden[u]&(1u<<w))return 0;
    if(adj[u]&(1u<<w))return 1;
    if(u<start||w<start||pc(adj[u])==degree[u]||pc(adj[w])==degree[w])return 0;
    edge(adj,u,w);*changed=1;return 1;
}
static void forbid_edge(int u,int w,int *changed){
    assert(!(adj[u]&(1u<<w)));
    if(!(forbidden[u]&(1u<<w))){forbidden[u]|=1u<<w;forbidden[w]|=1u<<u;*changed=1;}
}
static int force_square_corners(int start,int *changed){
    for(int v=0;v<n;v++)if(pc(adj[v])==4){
        int ns[4],i=0;for(mask t=adj[v];t;t&=t-1)ns[i++]=first(t);
        static const int pairs[3][4]={{0,1,2,3},{0,2,1,3},{0,3,1,2}};
        for(i=0;i<3;i++){
            mask p=adj[ns[pairs[i][0]]]&adj[ns[pairs[i][1]]]&~(1u<<v);
            mask q=adj[ns[pairs[i][2]]]&adj[ns[pairs[i][3]]]&~(1u<<v);
            if(p&&q){if(pc(p)!=1||pc(q)!=1||p==q)return 0;if(!(adj[first(p)]&q)){if(!force_edge(first(p),first(q),start,changed))return 0;return 1;}}
        }
    }
    return 1;
}
#include "treewidth52_quartic_core_constraints_v4.h"
static int propagate(int start){
    int changed;
    do{
        changed=0;
        if(!extra_partial())return 0;
        for(int v=0;v<n;v++)for(mask t=adj[v];t;t&=t-1)if(adj[first(t)]&adj[v])return 0;
        for(int u=0;u<n;u++)for(int w=u+1;w<n;w++)if(!(adj[u]&(1u<<w))){
            if(u<start||w<start||pc(adj[u])==degree[u]||pc(adj[w])==degree[w])forbid_edge(u,w,&changed);
        }
        for(int v=0;v<n;v++){
            mask possible=((1u<<n)-1)&~(1u<<v)&~forbidden[v];
            if(pc(possible)<degree[v])return 0;
            if(pc(possible)==degree[v])for(mask t=possible&~adj[v];t;t&=t-1)
                if(!force_edge(v,first(t),start,&changed))return 0;
        }
        for(int v=0;v<n;v++)if(degree[v]==4){
            mask high=adj[v]&low_mask;
            if(pc(high)>2)return 0;
            if(pc(high)==2){int u=first(high),w=first(high&(high-1));if(!force_edge(u,w,start,&changed))return 0;}
        }
        for(int v=0;v<n;v++)if(degree[v]==5&&pc(adj[v])==5){
            mask high=adj[v]&low_mask;int h=pc(high);if(h<3)continue;
            int ns[5],count=0;
            for(mask t=high;t;t&=t-1)ns[count++]=first(t);
            for(mask t=adj[v]&~low_mask;t;t&=t-1)ns[count++]=first(t);
            int present=0,absent=0,bit=0;
            for(int j=1;j<5;j++)for(int i=0;i<j;i++,bit++){
                int u=ns[i],w=ns[j];
                if(adj[u]&(1u<<w))present|=1<<bit;
                else if(forbidden[u]&(1u<<w))absent|=1<<bit;
            }
            int forced=1023,permitted=0,found=0;
            for(int i=0;i<allowed_count[h];i++){
                int pattern=allowed[h][i];
                if((pattern&present)==present&&!(pattern&absent)){found=1;forced&=pattern;permitted|=pattern;}
            }
            if(!found)return 0;
            forced&=~present;bit=0;
            for(int j=1;j<5;j++)for(int i=0;i<j;i++,bit++)
                if(forced&(1<<bit)){if(!force_edge(ns[i],ns[j],start,&changed))return 0;}
                else if(!(permitted&(1<<bit)))forbid_edge(ns[i],ns[j],&changed);
        }
        int square_count[26]={0};
        for(int u=0;u<n;u++)for(int w=u+1;w<n;w++)if(pc(adj[u]&adj[w])==2){square_count[u]++;square_count[w]++;}
        int triangles[26]={0};
        for(int v=0;v<n;v++)for(mask t=adj[v];t;t&=t-1)triangles[v]+=pc(adj[first(t)]&adj[v]);
        for(int v=0;v<n;v++)triangles[v]/=2;
        for(int u=start;u<n;u++)for(int w=u+1;w<n;w++)if(!((adj[u]|forbidden[u])&(1u<<w))){
            mask common=adj[u]&adj[w];int bad=0,added=pc(common);
            if(triangles[u]+added>0||triangles[w]+added>0)bad=1;
            for(mask t=common;t&&!bad;t&=t-1){int v=first(t);if(triangles[v]+1>0)bad=1;}
            if(degree[w]==4)for(mask t=adj[w];t&&!bad;t&=t-1){int z=first(t);
                int limit=(degree[u]==4&&degree[z]==4)?2:1;
                if(pc(adj[u]&adj[z]&~low_mask)>=limit)bad=1;
            }
            if(degree[u]==4)for(mask t=adj[u];t&&!bad;t&=t-1){int z=first(t);
                int limit=(degree[w]==4&&degree[z]==4)?2:1;
                if(pc(adj[w]&adj[z]&~low_mask)>=limit)bad=1;
            }
            if(degree[u]==4&&degree[w]==5&&triangles[u])bad=1;
            if(degree[w]==4&&degree[u]==5&&triangles[w])bad=1;
            for(mask t=common;t&&!bad;t&=t-1){int z=first(t);
                if(degree[u]==4&&(adj[u]&low_mask&~((1u<<w)|(1u<<z))))bad=1;
                if(degree[w]==4&&(adj[w]&low_mask&~((1u<<u)|(1u<<z))))bad=1;
                if(degree[z]==4&&(adj[z]&low_mask&~((1u<<u)|(1u<<w))))bad=1;
            }
            if(!bad){
                int added_squares=0;mask check_triangle=0;
                for(mask t=adj[u];t;t&=t-1){int x=first(t),gain=pc(adj[x]&adj[w]);
                    added_squares+=gain;if(square_count[x]+gain>max_four_cap)bad=1;
                    if(gain&&square_count[x]+gain>=3)check_triangle|=1u<<x;}
                for(mask t=adj[w];t;t&=t-1){int x=first(t),gain=pc(adj[x]&adj[u]);
                    if(square_count[x]+gain>max_four_cap)bad=1;
                    if(gain&&square_count[x]+gain>=3)check_triangle|=1u<<x;}
                if(square_count[u]+added_squares>max_four_cap||square_count[w]+added_squares>max_four_cap)bad=1;
                if(added_squares&&square_count[u]+added_squares>=3)check_triangle|=1u<<u;
                if(added_squares&&square_count[w]+added_squares>=3)check_triangle|=1u<<w;
                if(!bad&&check_triangle){
                    edge(adj,u,w);
                    for(mask t=check_triangle;t&&!bad;t&=t-1)if(forbidden_square_incidence_at(first(t)))bad=1;
                    adj[u]^=1u<<w;adj[w]^=1u<<u;
                }

            }
            if(bad)forbid_edge(u,w,&changed);
        }
        if(changed)continue;
        if(!force_square_corners(start,&changed))return 0;
        if(changed)continue;
        if(!quartic_core_constraints(start,&changed))return 0;
    }while(changed);
    mask unseen=(1u<<n)-1;
    while(unseen){
        mask component=0,todo=unseen&-unseen;int saturated=1;
        while(todo){int v=first(todo);todo&=todo-1;component|=1u<<v;todo|=adj[v]&~component;
            if(pc(adj[v])!=degree[v])saturated=0;}
        if(saturated&&component!=((1u<<n)-1))return 0;
        unseen&=~component;
    }
    return 1;
}
static void complete(int v){
    mask saved[26],saved_forbidden[26];memcpy(saved,adj,sizeof saved);memcpy(saved_forbidden,forbidden,sizeof forbidden);
    if(propagate(v))complete_impl(v);
    memcpy(adj,saved,sizeof saved);memcpy(forbidden,saved_forbidden,sizeof forbidden);
}
static void swap_vertices(int u,int w){
    if(u==w)return;
    mask pair=(1u<<u)|(1u<<w);
    for(int x=0;x<n;x++)if(!!(adj[x]&(1u<<u))!=!!(adj[x]&(1u<<w)))adj[x]^=pair;
    mask tmp=adj[u];adj[u]=adj[w];adj[w]=tmp;
    for(int x=0;x<n;x++)if(!!(forbidden[x]&(1u<<u))!=!!(forbidden[x]&(1u<<w)))forbidden[x]^=pair;
    tmp=forbidden[u];forbidden[u]=forbidden[w];forbidden[w]=tmp;
}

static int upper_bound(const mask *upper,int depth){
    size=n;target=10;
#ifndef NO_ORDER_CACHE
    if(cover_valid[depth]){
        mask a[26],remaining=(1u<<n)-1;memcpy(a,upper,sizeof a);
        int i=0;
        for(;i<n;i++){
            int w=cover_orders[depth][i];
            if(pc(a[w]&remaining)>10)break;
            eliminate(a,remaining,w);remaining^=1u<<w;
        }
        if(i==n){memcpy(order,cover_orders[depth],n*sizeof(int));assert(verify(upper));return 1;}
    }
#endif
    if(!greedy(upper))return 0;
    assert(verify(upper));
    memcpy(cover_orders[depth],order,n*sizeof(int));cover_valid[depth]=1;
    return 1;
}
static void choose(int v,mask eligible,int need,mask chosen){
    if(!need){
        if(!symmetry_ok(v,chosen))return;
        for(mask t=chosen;t;t&=t-1)edge(adj,v,first(t));
        complete(v+1);
        for(mask t=chosen;t;t&=t-1){int w=first(t);adj[v]^=1u<<w;adj[w]^=1u<<v;}
        return;
    }
    while(pc(eligible)>=need){int w=first(eligible);eligible&=eligible-1;choose(v,eligible,need-1,chosen|(1u<<w));}
}
static void complete_impl(int v){
    nodes++;
#ifndef NO_FILTER
    if(!valid_partial(v)||deletion_obstruction()){filtered++;return;}
#endif
    if(v==split_depth){
        printf("%d %d",kind,v);for(int i=0;i<n;i++)printf(" %u",adj[i]);putchar('\n');patterns++;return;
    }
#ifndef NO_COVER
    if(v<n&&n-v<=14){
        int universal_order[26];
        if(degree_cover(adj,degree,forbidden,n,v,10,universal_order)){covers++;return;}
        mask upper[26];memcpy(upper,adj,sizeof upper);
        for(int u=v;u<n;u++)if(pc(adj[u])<degree[u])
            for(int w=u+1;w<n;w++)if(pc(adj[w])<degree[w]&&!(forbidden[u]&(1u<<w)))edge(upper,u,w);
        if(upper_bound(upper,v)){covers++;return;}
    }
#endif
    if(PREFIX_CANONICAL_SEEN(adj,n,r,degree,v)){isomorphism_covers++;return;}
    if(v==n){
        for(int u=0;u<n;u++)assert(pc(adj[u])==degree[u]);
        leaves++;
#ifdef EMIT_ALL
        emit(adj,n);return;
#endif
        if(!check(adj,n,10)){residues++;emit(adj,n);}
        return;
    }
    for(int u=v;u<n;u++){
        int possible=0;
        for(int w=v;w<n;w++)if(u!=w&&!((adj[u]|forbidden[u])&(1u<<w))&&pc(adj[w])<degree[w])possible++;
        if(pc(adj[u])>degree[u]||pc(adj[u])+possible<degree[u])return;
    }
    int pivot=v;
    for(int w=v+1;w<n;w++)if(degree[w]==degree[v]&&degree[w]-pc(adj[w])<degree[pivot]-pc(adj[pivot]))pivot=w;
    swap_vertices(v,pivot);
    mask eligible=0;
    for(int w=v+1;w<n;w++)if(!((adj[v]|forbidden[v])&(1u<<w))&&pc(adj[w])<degree[w])eligible|=1u<<w;
    choose(v,eligible,degree[v]-pc(adj[v]),0);
    swap_vertices(v,pivot);
}
int main(int argc,char **argv){
    int start=0;initialize_allowed();
    if(argc==4&&!strcmp(argv[1],"split")){
        char *end;long family=strtol(argv[2],&end,10);if(*end||family<22||family>26)return 2;
        split_depth=(int)strtol(argv[3],&end,10);if(*end||split_depth<0||split_depth>18)return 2;
        initialize((int)family);
    }else if(argc==2&&!strcmp(argv[1],"run")){
        int family;if(scanf("%d%d",&family,&start)!=2||family<22||family>26)return 2;
        initialize(family);assert(start>=0&&start<=n);
        for(int v=0;v<n;v++)if(scanf("%u",&adj[v])!=1)return 2;
        for(int v=0;v<n;v++){
            assert(!(adj[v]>>n)&&!(adj[v]&(1u<<v))&&pc(adj[v])<=degree[v]);
            if(v<start)assert(pc(adj[v])==degree[v]);
            for(int w=0;w<n;w++)assert(!!(adj[v]&(1u<<w))==!!(adj[w]&(1u<<v)));
        }
        
    }else return 2;
    assert(start>=5&&adj[0]==30u);
    max_four_cap=0;
    for(int v=1;v<n;v++)if(pc(adj[0]&adj[v])==2)max_four_cap++;
    assert(max_four_cap>=1&&max_four_cap<=6);
    complete(start);
    fprintf(stderr,"TEMPLATE_RESULT {\"kind\":%d,\"nodes\":%llu,\"patterns\":%llu,\"leaves\":%llu,\"covers\":%llu,\"filtered\":%llu,\"residues\":%llu,\"isomorphism_covers\":%llu,\"cpu_seconds\":%.3f}\n",
        kind,(unsigned long long)nodes,(unsigned long long)patterns,(unsigned long long)leaves,
        (unsigned long long)covers,(unsigned long long)filtered,(unsigned long long)residues,
        (unsigned long long)isomorphism_covers,(double)clock()/CLOCKS_PER_SEC);
    return 0;
}
