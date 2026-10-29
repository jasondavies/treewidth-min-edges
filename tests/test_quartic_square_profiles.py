from itertools import combinations
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from quartic_square_profiles import (PAIRS,PERMUTATIONS,canonical,catalogue,edge_set,image,
                                     prefix,triangle_free)

class SquareProfileTests(unittest.TestCase):
    def test_complete_orbits(self):
        rows=catalogue();keys={row['mask']for row in rows}
        self.assertEqual(keys,{1,3,7,12,13,30})
        self.assertEqual(sum(row['labeled_count']for row in rows),40)
        for mask in range(1,64):
            if triangle_free(mask):
                self.assertIn(canonical(mask),keys)
                self.assertTrue(all(canonical(image(mask,p))==canonical(mask)for p in PERMUTATIONS))
            else:
                self.assertNotIn(canonical(mask),keys)

    def test_prefix_incidence_and_forced_corners(self):
        for row in catalogue():
            p=row['prefix'];self.assertEqual(p[:2],[26,5])
            graph=[{v for v in range(26)if mask>>v&1}for mask in p[2:]]
            self.assertTrue(all(len(graph[v])==4 for v in range(5)))
            observed=set();corners={}
            for a,b in PAIRS:
                common=(graph[a+1]&graph[b+1])-{0}
                if common:
                    self.assertEqual(len(common),1);observed.add((a,b));corners[a,b]=next(iter(common))
            self.assertEqual(observed,edge_set(row['mask']))
            self.assertTrue(all(len(graph[u]&graph[v])<=2 for u,v in combinations(range(26),2)))
            self.assertTrue(all(not(graph[u]&graph[v])for u in range(26)for v in graph[u]))
            for first,second in combinations(corners,2):
                if not set(first)&set(second):self.assertIn(corners[second],graph[corners[first]])

    def test_invalid_inputs(self):
        for mask in(0,64,-1,True,11):
            with self.assertRaises(ValueError):prefix(mask)


class FourSquareCertificateTests(unittest.TestCase):
    def test_complete_small_certificate_and_coverage_tampering(self):
        import io,lzma
        from branch_certificate_binary import decode
        from verify_branch_refutation import verify_certificate
        from verify_quartic_four_square import verify
        source=Path(__file__).resolve().parents[1]/'sources/eleven-quartic-c4.bin.xz'
        result=verify(source)
        self.assertEqual(result['proof'],{'branches':2,'local_leaves':0,'trace_leaves':13})
        certificate=decode(io.BytesIO(lzma.decompress(source.read_bytes())))
        certificate['proof'][2].pop()
        with self.assertRaises(ValueError):verify_certificate(certificate,prefix(30))
        certificate=decode(io.BytesIO(lzma.decompress(source.read_bytes())))
        certificate['prefix'][2+5] ^= 1<<8
        certificate['prefix'][2+8] ^= 1<<5
        with self.assertRaises(ValueError):verify_certificate(certificate,prefix(30))

class FourSquareDependencyTests(unittest.TestCase):
    def test_maximum_three_rule_cannot_prove_its_own_premise(self):
        import io,lzma,tempfile
        from branch_certificate_binary import MAGIC,read_header
        from verify_quartic_four_square import verify
        source=Path(__file__).resolve().parents[1]/'sources/eleven-quartic-c4.bin.xz'
        raw=lzma.decompress(source.read_bytes());stream=io.BytesIO(raw)
        read_header(stream)
        # Exact C4 prefix, followed by the v9 terminal q opcode21.
        circular=raw[:len(MAGIC)]+bytes([9])+raw[len(MAGIC)+1:stream.tell()]+bytes([21])
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'circular.bin';path.write_bytes(circular)
            with self.assertRaisesRegex(ValueError,'original v1'):
                verify(path)

if __name__=='__main__':unittest.main()
