"""Check the illustrated witness using its compact, self-contained certificate."""
from pathlib import Path
from verify_treewidth_certificate import read_certificate, require, verify

ROOT = Path(__file__).resolve().parents[1] / 'sources'


def main():
    result = verify(*read_certificate(ROOT / 'witness53.twcert.xz'),
                    expected_graph6=(ROOT / 'witness53.g6').read_text().strip())
    require((result['vertices'], result['edges'], result['treewidth']) == (24, 53, 11),
            'Expected a 24-vertex, 53-edge witness of treewidth eleven.')
    print(f'PASS: 24 vertices, 53 edges, treewidth exactly eleven; {result["closed_states"]:,} closed states.')


if __name__ == '__main__':
    main()
