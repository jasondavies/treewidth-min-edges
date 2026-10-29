/* Consequence of the completed high-degree core exclusion. For a square
 * x-a-y-b-x, delete x,y and smooth a,b. Its four cubic vertices form a
 * proper subgraph of K2,2. Every independent set S that dominates each
 * other cubic vertex exactly once produces a minimum-degree-four core
 * on eliminating S. Its maximum degree must be <=5, so distinct members
 * of S cannot have a common neighbor outside the four cubic vertices. */
static unsigned char quartic_core_pair_masks[16];
static int quartic_core_masks_ready;
static void initialize_quartic_core_masks(void){
    if(quartic_core_masks_ready)return;
    quartic_core_masks_ready=1;
    for(int pattern=0;pattern<15;pattern++){
        mask a[4]={0};int bit=0;
        for(int u=0;u<2;u++)for(int v=2;v<4;v++,bit++)if(pattern&(1<<bit))edge(a,u,v);
        for(mask set=1;set<16;set++){
            int good=1;
            for(int v=0;v<4;v++)if(set&(1u<<v)){if(a[v]&set)good=0;}
            else if(pc(a[v]&set)!=1)good=0;
            if(!good)continue;
            bit=0;
            for(int u=0;u<4;u++)for(int v=u+1;v<4;v++,bit++)
                if((set&(1u<<u))&&(set&(1u<<v)))quartic_core_pair_masks[pattern]|=1u<<bit;
        }
        assert(quartic_core_pair_masks[pattern]);
    }
}
static int quartic_core_constraints(int start,int *changed){
    assert(n==26);initialize_quartic_core_masks();mask full=(1u<<26)-1;
    for(int x=0;x<26;x++)if(pc(adj[x])==4)for(int y=x+1;y<26;y++)if(pc(adj[y])==4&&!(adj[x]&(1u<<y))){
        mask common=adj[x]&adj[y];if(pc(common)!=2)continue;
        int a=first(common),b=first(common&(common-1));
        if(pc(adj[a])!=4||pc(adj[b])!=4)continue;
        mask removed=(1u<<x)|(1u<<y)|common,remaining=full&~removed;
        mask left=adj[x]&~common,right=adj[y]&~common,low=left|right;
        assert(pc(left)==2&&pc(right)==2&&pc(low)==4);
        int vertices[4]={first(left),first(left&(left-1)),first(right),first(right&(right-1))};
        mask h[26];for(int v=0;v<26;v++)h[v]=(remaining&(1u<<v))?(adj[v]&remaining):0;
        mask ends=adj[a]&remaining;assert(pc(ends)==2);edge(h,first(ends),first(ends&(ends-1)));
        ends=adj[b]&remaining;assert(pc(ends)==2);edge(h,first(ends),first(ends&(ends-1)));
        int bad_pairs=0,bit=0,present=0,absent=0;
        for(int u=0;u<4;u++)for(int v=u+1;v<4;v++,bit++)
            if(h[vertices[u]]&h[vertices[v]]&remaining&~low)bad_pairs|=1u<<bit;
        bit=0;
        for(int u=0;u<2;u++)for(int v=2;v<4;v++,bit++){
            if(adj[vertices[u]]&(1u<<vertices[v]))present|=1u<<bit;
            if(forbidden[vertices[u]]&(1u<<vertices[v]))absent|=1u<<bit;
        }
        int intersection=15,united=0,found=0;
        for(int pattern=0;pattern<15;pattern++)if((pattern&present)==present&&!(pattern&absent)&&!(quartic_core_pair_masks[pattern]&bad_pairs)){
            intersection&=pattern;united|=pattern;found=1;
        }
        if(!found)return 0;
        bit=0;
        for(int u=0;u<2;u++)for(int v=2;v<4;v++,bit++){
            int p=vertices[u],q=vertices[v];
            if((intersection&(1u<<bit))&&!(adj[p]&(1u<<q))){if(!force_edge(p,q,start,changed))return 0;return 1;}
            else if(!(united&(1u<<bit))&&!(adj[p]&(1u<<q)))forbid_edge(p,q,changed);
        }
    }
    return 1;
}
