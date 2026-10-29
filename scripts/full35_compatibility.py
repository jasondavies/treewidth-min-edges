"""Explicit full34/35 classification terminal for P4 theory obligations.

This does not alter ordinary interval rules. Every embedding search is exact;
a node limit raises an error and cannot establish incompatibility.
"""
from hashlib import sha256
from itertools import combinations
from pathlib import Path
from marked_residue_common import decode_graph6

FILES = {
 'treewidth34-family34.g6': '4f0f5209e9a3cf10c88b151649742ca5485b24b56204b47a62f9e0d99a41503f',
 'treewidth35-all-family.g6': '1fcf89ffba866b13dc95de22bdac1c98a284d03687b9d61b927f00daca52fca6',
}

def require(condition,message):
    if not condition:raise ValueError(message)


def templates(repository):
    families=[]
    for name,digest in FILES.items():
        raw=(Path(repository)/'sources/nine'/name).read_bytes()
        require(sha256(raw).hexdigest()==digest,'Wrong earlier classification family')
        family=[decode_graph6(line)for line in raw.decode('ascii').splitlines()]
        edges=34 if '34-' in name else 35
        require(len(family)==(2 if edges==34 else 130),'Wrong classification size')
        for graph in family:
            require(sum(row.bit_count()for row in graph)==2*edges,'Wrong edge count')
            require(min(row.bit_count()for row in graph)>=(4 if edges==34 else 3),'Wrong minimum degree')
            families.append((edges,tuple(graph)))
    for _,a in families[:2]:
        n=len(a)
        for u in range(n):
            b=list(a)+[1<<u];b[u]|=1<<n;families.append((35,tuple(b)))
        families.append((35,tuple(a)+(1<<(n+1),1<<n)))
        for u,v in combinations(range(n),2):
            if not a[u]>>v&1:continue
            b=list(a)+[(1<<u)|(1<<v)]
            b[u]=(b[u]&~(1<<v))|(1<<n);b[v]=(b[v]&~(1<<u))|(1<<n)
            families.append((35,tuple(b)))
    require(len(families)==235,'Incomplete obstruction decoration list')
    return tuple(families)


def traits(graph):
    n=len(graph);result=[]
    for v in range(n):
        neighbors=[u for u in range(n)if graph[v]>>u&1]
        triangle=sum(bool(graph[u]>>w&1)for u,w in combinations(neighbors,2))
        square=sum((graph[v]&graph[u]).bit_count()*((graph[v]&graph[u]).bit_count()-1)//2 for u in range(n)if u!=v)
        result.append((len(neighbors),triangle,square))
    return tuple(result)


class TemplateFamily:
    def __init__(self,repository):
        self.graphs=tuple((edges,g,traits(g))for edges,g in templates(repository))

    def possible(self,state,node_limit=100000):
        require(state.width==8 and state.edges<=35,'Full35 terminal requires width8 and at most35 edges')
        require(type(node_limit)is int and node_limit>0,'Invalid embedding budget')
        vertices=sorted(state.remaining);n=len(vertices)
        k=[sum(1<<i for i,u in enumerate(vertices)if u in state.known[v])for v in vertices]
        p=[sum(1<<i for i,u in enumerate(vertices)if u in state.possible[v])for v in vertices]
        lower=[max(state.lower[v],k[i].bit_count())for i,v in enumerate(vertices)]
        upper=[min(state.upper[v],p[i].bit_count())for i,v in enumerate(vertices)]
        require(all(0<=lower[i]<=upper[i] for i in range(n)),'Invalid residual degree interval')
        low_traits=traits(k);high_traits=traits(p)
        mandatory=sum(1<<i for i in range(n)if lower[i]>0)
        nodes=0
        for edges,target,tt in self.graphs:
            m=len(target)
            if edges>state.edges or m>n or mandatory.bit_count()>m:continue
            options=[]
            for d,tr,sq in tt:
                option=sum(1<<v for v in range(n)if lower[v]<=d<=upper[v]
                           and low_traits[v][1]<=tr<=high_traits[v][1]
                           and low_traits[v][2]<=sq<=high_traits[v][2])
                if not option:break
                options.append(option)
            if len(options)!=m:continue
            def search(left,domains,used):
                nonlocal nodes
                nodes+=1
                require(nodes<=node_limit,'Full35 compatibility search is incomplete (node limit)')
                if not left:return mandatory&~used==0
                union=0;selected=-1;least=n+1
                for u in left:
                    count=domains[u].bit_count()
                    if not count:return False
                    union|=domains[u]
                    if count<least:selected,least=u,count
                required=mandatory&~used
                if required&~union or required.bit_count()>len(left):return False
                rest=left-{selected};choices=domains[selected]
                while choices:
                    bit=choices&-choices;choices-=bit;v=bit.bit_length()-1
                    child=domains.copy();valid=True
                    for u in rest:
                        child[u]&=~bit
                        child[u]&=p[v] if target[selected]>>u&1 else~k[v]
                        if not child[u]:valid=False;break
                    if valid and search(rest,child,used|bit):return True
                return False
            if search(set(range(m)),options,0):return True,nodes
        return False,nodes
