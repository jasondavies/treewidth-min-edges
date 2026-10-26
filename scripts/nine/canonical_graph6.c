/* Canonicalize small graph6 graphs using the installed nauty library. */
#include <assert.h>
#include <nauty.h>
#include <gtools.h>
int main(void)
{
    char line[256];graph g[20],canon[20];int lab[20],ptn[20],orbits[20];
    DEFAULTOPTIONS_GRAPH(options);statsblk stats;options.getcanon=TRUE;
    while(fgets(line,sizeof line,stdin)) {
        if(line[0]=='\n')continue;
        int n=graphsize(line);assert(n>=1 && n<=20);stringtograph(line,g,1);
        densenauty(g,lab,ptn,orbits,&options,&stats,1,n,canon);
        fputs(ntog6(canon,1,n),stdout);
    }
    return 0;
}
