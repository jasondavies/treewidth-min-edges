static int triangle_twice(const M a[N], int v) {
    int count=0;
    for(M q=a[v];q;q&=q-1)count+=PC(a[FIRST(q)]&a[v]);
    return count;
}
static int iso_search(const M graph[N], const M domains[22], int p[22], M used) {
    int vertex=-1;M available=0;int size=INT_MAX, bound=-1;
    for(int v=0;v<22;++v)if(p[v]<0) {
        M choices=0;
        for(M q=domains[v]&~used;q;q&=q-1) {
            int w=FIRST(q),valid=1;
            for(int u=0;u<22;++u)if(p[u]>=0
                    && !!(graph[v]&(1u<<u)) != !!(exception_graph[w]&(1u<<p[u]))) {
                valid=0;break;
            }
            if(valid)choices|=1u<<w;
        }
        int tied=0;for(M q=graph[v];q;q&=q-1)tied+=p[FIRST(q)]>=0;
        int count=PC(choices);
        if(count<size || (count==size&&tied>bound)) {
            vertex=v;available=choices;size=count;bound=tied;
        }
    }
    if(vertex<0)return 1;
    for(M q=available;q;q&=q-1) {
        int w=FIRST(q);p[vertex]=w;
        if(iso_search(graph,domains,p,used|(1u<<w)))return 1;
        p[vertex]=-1;
    }
    return 0;
}
static int exception_map(const M graph[N], int p[22]) {
    M domains[22];
    M target[N]={0};memcpy(target,exception_graph,sizeof exception_graph);
    for(int v=0;v<22;++v) {
        int low=0;for(M q=graph[v];q;q&=q-1)low+=PC(graph[FIRST(q)])==3;
        domains[v]=0;p[v]=-1;
        for(int w=0;w<22;++w) {
            int target_low=0;
            for(M q=target[w];q;q&=q-1)target_low+=PC(target[FIRST(q)])==3;
            if(PC(graph[v])==PC(target[w]) && low==target_low
                    && triangle_twice(graph,v)==triangle_twice(target,w)) domains[v]|=1u<<w;
        }
    }
    return iso_search(graph,domains,p,0);
}

