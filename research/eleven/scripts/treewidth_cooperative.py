"""Build an existing completion checker with reproducible cooperative cuts.

The only search change is at entry to complete(v). After a work budget is
exhausted, save each unvisited subtree instead of throwing away completed
work. The recorded call number allows exact replay without a clock.
"""
from pathlib import Path
import re
import shlex
import subprocess

from run_treewidth_edge_checks import ROOT, digest


PRELUDE = r'''
static unsigned long long slice_calls, slice_cut, slice_replay, slice_frontiers;
static double slice_seconds;
static int slice_start;
static clock_t slice_began;
static int slice_checkpoint(int v){
    ++slice_calls;
    if(!slice_cut && v>slice_start){
        if(slice_replay && slice_calls>=slice_replay) slice_cut=slice_calls;
        else if(!slice_replay && slice_seconds>0 && (slice_calls&255u)==0 &&
                (double)(clock()-slice_began)/CLOCKS_PER_SEC>=slice_seconds)
            slice_cut=slice_calls;
    }
    if(!slice_cut)return 0;
    assert(v>slice_start);
    printf("FRONTIER %d %d",kind,v);
    for(int i=0;i<n;i++)printf(" %u",adj[i]);
    putchar('\n');++slice_frontiers;
    return 1;
}
'''


def dependencies(source, canonical):
    paths = {Path(__file__).resolve(), canonical.resolve()}

    def collect(path):
        path = path.resolve()
        if path in paths:
            return
        paths.add(path)
        for name in re.findall(r'^#include "([^"]+)"', path.read_text(), re.M):
            collect(path.parent / name)

    collect(source)
    return {str(p): digest(p) for p in sorted(paths)}


def instrument(source):
    body = source.read_text()
    marker = 'static void complete(int v){'
    assert body.count(marker) == 1
    body = body.replace(marker, PRELUDE + '\n' + marker + '\n    if(slice_checkpoint(v))return;')
    marker = '}else if(argc==2&&!strcmp(argv[1],"run")){'
    assert body.count(marker) == 1
    body = body.replace(marker, '''}else if((argc==2&&!strcmp(argv[1],"run")) ||
            (argc==3&&(!strcmp(argv[1],"slice")||!strcmp(argv[1],"replay")))){
        if(argc==3){
            char *end;
            if(!strcmp(argv[1],"slice"))slice_seconds=strtod(argv[2],&end);
            else slice_replay=strtoull(argv[2],&end,10);
            if(*end||slice_seconds<0)return 2;
        }
''')
    marker = '    complete(start);'
    assert body.count(marker) == 1
    body = body.replace(marker, '''    slice_start=start;slice_began=clock();
    complete(start);
    fprintf(stderr,"SLICE_RESULT {\\"calls\\":%llu,\\"cut\\":%llu,\\"frontiers\\":%llu}\\n",
            slice_calls,slice_cut,slice_frontiers);
''')
    return body


def build(source, canonical, out):
    generated = out / 'cooperative.c'
    generated.write_text(instrument(source))
    flags = shlex.split(subprocess.check_output(['pkg-config', '--cflags', '--libs', 'nauty'], text=True))
    subprocess.run(['cc', '-O3', '-mpopcnt', '-I', str(ROOT / 'scripts'),
                    str(generated), *flags, '-o', str(out / 'complete')], check=True)
    subprocess.run(['cc', '-O3', str(canonical), *flags, '-o', str(out / 'canonical')], check=True)


def parse_run(stdout, stderr):
    import json
    prefixes, graphs = [], []
    for line in stdout.splitlines():
        if line.startswith('FRONTIER '):
            prefixes.append(line.removeprefix('FRONTIER '))
        else:
            graphs.append(line)
    reports = [json.loads(line.removeprefix('SLICE_RESULT '))
               for line in stderr.splitlines() if line.startswith('SLICE_RESULT ')]
    assert len(reports) == 1
    report = reports[0]
    assert report['frontiers'] == len(prefixes)
    assert bool(report['cut']) == bool(prefixes)
    return prefixes, graphs, report
