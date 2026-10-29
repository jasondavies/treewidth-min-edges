/* Canonicalize triangle-template prefixes, including their marked triangles,
 * target degrees, and processed vertex set. Compare keys only within the
 * same template kind and row count (so color-class sizes agree). */
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <nauty.h>
#include <gtools.h>

int main(void){
    int kind,start;
    while(scanf("%d%d",&kind,&start)==2){
        assert(kind==26);
        int n=kind,r=0;
        assert(start>=0&&start<=n);
        uint32_t a[26]={0};int degree[26],colors[26],lab[26],ptn[26],orbits[26];
        graph g[26]={0},canonical[26];
        for(int v=0;v<n;v++){
            assert(scanf("%u",&a[v])==1);
            degree[v]=v<104-4*n?5:4;
        }
        for(int v=0;v<n;v++){
            colors[v]=v==0?4:2*(v<start);
            for(int w=0;w<n;w++)if(a[v]&(1u<<w))ADDONEEDGE(g,v,w,1);
        }
        for(int t=0;t<r;t++){
            colors[n+t]=4;
            for(int v=3*t;v<3*t+3;v++)ADDONEEDGE(g,n+t,v,1);
        }
        int p=0;
        for(int color=0;color<=4;color++){
            for(int v=0;v<n;v++)if(colors[v]==color){lab[p]=v;ptn[p++]=1;}
            if(p)ptn[p-1]=0;
        }
        assert(p==n);
        DEFAULTOPTIONS_GRAPH(options);statsblk stats;
        options.getcanon=TRUE;options.defaultptn=FALSE;
        densenauty(g,lab,ptn,orbits,&options,&stats,1,n,canonical);
        fputs(ntog6(canonical,1,n),stdout);
    }
    return 0;
}
