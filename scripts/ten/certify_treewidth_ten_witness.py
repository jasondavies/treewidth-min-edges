"""Independently certify a 47- or 48-edge treewidth-ten witness from graph6 input."""
import argparse
import gzip
import json
from pathlib import Path
import time
from common import decode
from common import width_reachable,verify_width_lower
from common import CC,SOURCE,run,masks,verify_order


def main():
    if not __debug__:raise RuntimeError('Run without -O.')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    s=args.input.read_text().splitlines()[0];a=decode(s);n=len(a);edges=sum(map(len,a))//2
    assert (n,edges) in [(23,47),(24,48)]
    exe=out/'check';run(CC+['-O3','-DSTANDALONE',f'-DTW_MAXN={n}',SOURCE,'-o',exe])
    answer=run([exe,10],input=s+'\n').stdout.split();assert answer[0]=='YES'
    order=list(map(int,answer[1:]));verify_order(a,order,10)
    start=time.monotonic();closed,lower_order=width_reachable(masks(a),9)
    assert lower_order is None
    print('Generated',len(closed),'closed states',flush=True)
    assert verify_width_lower(masks(a),9,closed)
    record={'graph6':s,'vertices':n,'edges':edges,'treewidth':10,'width_ten_order':order,
            'closed_width_nine_states':sorted(closed),'seconds':time.monotonic()-start}
    (out/'witness.json.gz').write_bytes(gzip.compress(json.dumps(record,separators=(',',':')).encode(),mtime=0))
    (out/'summary.json').write_text(json.dumps({k:v for k,v in record.items() if k!='closed_width_nine_states'}|{'closed_states':len(closed)},indent=2)+'\n')
    print('PASS: treewidth exactly ten',len(closed),'closed states',flush=True)


if __name__=='__main__':main()
