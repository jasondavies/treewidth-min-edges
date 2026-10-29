/* Girth-five quartic witness search, with verified supergraph pruning.
 * This is ONLY the regular girth-five subcase of the 52-edge problem.
 * GENREG calls prune after fixing all edges at vertices preceding start.
 */
#define STANDALONE
#define TW_MAXN 26
#define main unused_checker_main
#include "treewidth_edge_geng.c"
#undef main
#ifndef GENREG_WIDTH
#define GENREG_WIDTH 10
#endif
static uint64_t covers,attempts,leaves;
static void masks_from_generator(int n,int **g,mask *a){
 for(int v=0;v<n;v++){a[v]=0;for(int w=0;w<n;w++)if(g[v+1][w+1])a[v]|=1u<<w;}
}
int genreg_tw_prune(int n,int d,int **g,int *degree,int start){
 assert(n<=26&&d==4);
 if(n-start+1>16)return 0;
 mask a[26],upper[26];masks_from_generator(n,g,a);memcpy(upper,a,n*sizeof(mask));
 for(int v=start-1;v<n;v++)if(degree[v+1]<d){
  mask forbidden=a[v]|(1u<<v),step=a[v];
  for(int distance=2;distance<=3;distance++){
   mask next=0;for(mask t=step;t;t&=t-1)next|=a[first(t)];
   forbidden|=next;step=next;
  }
  for(int w=v+1;w<n;w++)if(degree[w+1]<d&&!(forbidden&(1u<<w))){upper[v]|=1u<<w;upper[w]|=1u<<v;}
 }
 size=n;target=GENREG_WIDTH;attempts++;
 if(!greedy(upper))return 0;
 if(!verify(upper)){fputs("SUPERGRAPH ORDER FAILURE\n",stderr);abort();}
 covers++;return 1;
}
void genreg_tw_leaf(int n,int d,int **g){
 mask a[26];masks_from_generator(n,g,a);leaves++;
 for(int v=0;v<n;v++)assert(pc(a[v])==d);
 if(check(a,n,GENREG_WIDTH))return;
 int value=0,bits=0;putchar(n+63);
 for(int v=1;v<n;v++)for(int u=0;u<v;u++){
  value=(value<<1)|!!(a[u]&(1u<<v));if(++bits==6){putchar(value+63);bits=value=0;}
 }
 if(bits)putchar(63+(value<<(6-bits)));
 putchar('\n');fflush(stdout);exit(10);
}
void genreg_tw_summary(unsigned long count){
 assert(count==leaves&&total==leaves);
 fprintf(stderr,"GENREG_TW {\"leaves\":%llu,\"verified\":%llu,\"negative\":%llu,\"covers\":%llu,\"attempts\":%llu}\n",(unsigned long long)leaves,(unsigned long long)verified,(unsigned long long)counterexamples,(unsigned long long)covers,(unsigned long long)attempts);
}
