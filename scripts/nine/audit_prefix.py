"""Compare prefix-pruned and unpruned 31-edge core enumeration.

Default orders 9--11 are a moderate audit. --max-order 12 adds the larger
comparison recorded in the original run. Also compare 16 partitions at n=11.
"""
import argparse
import json
from pathlib import Path
import shlex
from tempfile import TemporaryDirectory
from run_treewidth_edge_checks import CC, GENG, ROOT, SOURCE, run


def main():
    if not __debug__:
        raise RuntimeError('Run without -O.')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--max-order',type=int,choices=(11,12),default=11)
    args=parser.parse_args()
    flags=shlex.split(run(['pkg-config','--cflags','--libs','nauty']).stdout)
    rows=[]
    with TemporaryDirectory(prefix='tw9-prefix-audit-') as directory:
        plain=Path(directory)/'plain'; pruned=Path(directory)/'pruned'
        common=['-O3','-DOUTPROC=tw_out','-DTW_MAXN=15','-DTW_TARGET=6']
        run(CC+common+['-DSUMMARY=tw_summary',GENG,SOURCE,*flags,'-o',plain])
        run(CC+common+['-DSUMMARY=prefix_summary','-DPRUNE=prefix_prune','-DPREFIX_BUDGET=128',
                      GENG,ROOT/'scripts/nine/treewidth_core_prune.c',*flags,'-o',pruned])
        for n in range(9,args.max_order+1):
            arguments=['-c','-d4','-D9',n,'31:31']
            expected=run([plain,*arguments]).stdout.splitlines()
            actual=run([pruned,*arguments]).stdout.splitlines()
            assert sorted(expected)==sorted(actual)
            if n==11:
                split=[]
                for i in range(16): split+=run([pruned,*arguments,f'{i}/16']).stdout.splitlines()
                assert sorted(split)==sorted(actual)
            rows.append({'order':n,'retained':len(actual),'agrees':True})
            print('PASS:',rows[-1],flush=True)
    (ROOT/'sources/nine/prefix-audit.json').write_text(json.dumps(rows,indent=2)+'\n')


if __name__=='__main__':
    main()
