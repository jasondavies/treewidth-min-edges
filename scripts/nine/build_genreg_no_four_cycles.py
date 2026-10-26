"""Build GENREG using the quartic codegree restriction and exact-key cache."""
import json
from pathlib import Path
from build_genreg_treewidth import build as original_build
from run_treewidth_edge_checks import CC,ROOT,SOURCE,digest,run


def build(source,out,width=8,cap=-1,cover=False,stop=False):
    exe=original_build(source,out,width,cap,cover,stop)
    out=out.resolve()
    adapter=ROOT/'scripts/nine/genreg_treewidth_no_four_cycles.c'
    run(CC+['-O3','-std=c11',f'-DGENREG_WIDTH={width}',f'-DGENREG_CAP={cap}',
            f'-DGENREG_COVER={int(cover)}',f'-DGENREG_STOP={int(stop)}','-c',adapter,'-o',out/'adapter.o'])
    run(CC+[out/(name+'.o') for name in ['genreg','main','optmid','adapter']]+['-o',exe])
    p=out/'build.json';data=json.loads(p.read_text())
    for source in [Path(__file__),adapter]:data['source_sha256'][str(source)]=digest(source)
    p.write_text(json.dumps(data,indent=2)+'\n')
    return exe
