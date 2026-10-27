"""Check the saved 47-edge treewidth-ten certificate with Python only."""
import gzip
import json
from pathlib import Path
from common import decode
from common import verify_width_lower
from common import ROOT,masks,verify_order


def main():
    if not __debug__:raise RuntimeError('Run without -O: assertions are verification steps.')
    record=json.loads(gzip.decompress((ROOT/'sources/witness47.json.gz').read_bytes()))
    a=decode(record['graph6'])
    assert (ROOT/'sources/witness47.g6').read_text().strip()==record['graph6']
    assert len(a)==record['vertices']==23 and sum(map(len,a))//2==record['edges']==47
    assert sorted(map(len,a))==[4]*21+[5]*2
    assert verify_order(a,record['width_ten_order'],10)==10
    closed=set(record['closed_width_nine_states'])
    assert len(closed)==len(record['closed_width_nine_states'])==410333
    assert verify_width_lower(masks(a),9,closed)
    print('PASS: 47 edges, treewidth exactly ten; 410333 closed states verified.')


if __name__=='__main__':main()
