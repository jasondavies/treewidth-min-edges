"""Build a verified-checker adapter for Markus Meringer's external GENREG.

Obtain gendef.h, genreg.c, main.c and optmid.c from the official source:
https://svn.code.sf.net/p/genreg/code/trunk/ (revision 5).
The upstream code is not redistributed here. Patches add callbacks only.
"""
import argparse
import json
import os
from pathlib import Path
from run_treewidth_edge_checks import CC,ROOT,SOURCE,digest,run


def build(source,out,width=8,cap=-1,cover=False,stop=False):
    source=source.resolve();out=out.resolve();out.mkdir(parents=True,exist_ok=True)
    upstream=[source/name for name in ('gendef.h','genreg.c','main.c','optmid.c')]
    for path in upstream:
        (out/path.name).write_bytes(path.read_bytes())
    path=out/'genreg.c';s=path.read_bytes().decode('latin-1')
    s=s.replace('#include "gendef.h"','#include "gendef.h"\nextern int genreg_tw_prune(int,int,int**,int*,int);\nextern void genreg_tw_leaf(int,int,int**);',1)
    before=' while(mx<n&&grad[mx]==k)'
    assert s.count(before)==1
    s=s.replace(before,' if(grad[mx]==k && genreg_tw_prune(n,k,g,grad,mx)) return;\n\n'+before,1)
    assert s.count('       anz++;')==1
    s=s.replace('       anz++;','       anz++;\n       genreg_tw_leaf(n,k,g);',1)
    path.write_bytes(s.encode('latin-1'))
    path=out/'main.c';s=path.read_bytes().decode('latin-1')
    s=s.replace('#include "gendef.h"','#include "gendef.h"\nextern void genreg_tw_summary(unsigned long);',1)
    before='\t  storeall,printall,&anz);'
    assert s.count(before)==1
    s=s.replace(before,before+'\n genreg_tw_summary(anz);',1)
    path.write_bytes(s.encode('latin-1'))
    objects=[]
    for name in ('genreg','main','optmid'):
        obj=out/(name+'.o');objects.append(obj)
        run(CC+['-O3','-w','-std=gnu89','-D__UNIX__',f'-Dtime_factor={os.sysconf("SC_CLK_TCK")}',
                '-c',out/(name+'.c'),'-o',obj])
    adapter=ROOT/'scripts/nine/genreg_treewidth_adapter.c';obj=out/'adapter.o';objects.append(obj)
    run(CC+['-O3','-std=c11',f'-DGENREG_WIDTH={width}',f'-DGENREG_CAP={cap}',
            f'-DGENREG_COVER={int(cover)}',f'-DGENREG_STOP={int(stop)}','-c',adapter,'-o',obj])
    exe=out/'genreg-tw';run(CC+[ *objects,'-o',exe])
    manifest={'width':width,'cap':cap,'cover':cover,'stop':stop,
              'upstream':'https://svn.code.sf.net/p/genreg/code/trunk/ (r5)',
              'upstream_sha256':{p.name:digest(p) for p in upstream},
              'source_sha256':{str(p):digest(p) for p in [Path(__file__),adapter,SOURCE]},
              'compiler':run(CC+['--version']).stdout.splitlines()[0]}
    (out/'build.json').write_text(json.dumps(manifest,indent=2)+'\n')
    return exe


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--width',type=int,default=8)
    parser.add_argument('--cap',type=int,default=-1)
    parser.add_argument('--cover',action='store_true')
    parser.add_argument('--stop',action='store_true')
    args=parser.parse_args()
    print(build(args.source,args.output,args.width,args.cap,args.cover,args.stop))
