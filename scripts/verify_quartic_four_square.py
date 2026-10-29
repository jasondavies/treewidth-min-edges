#!/usr/bin/env python3
"""Exclude the quartic four-square root using its regenerated incidence catalogue."""
import argparse
import json
import lzma
from pathlib import Path

from quartic_square_profiles import catalogue
from branch_certificate_binary import MAGIC, verify_stream
from verify_profile_refutation import require


def verify(certificate):
    profiles = catalogue()
    maximal = [row for row in profiles if len(row['edges']) == 4]
    require(len(maximal) == 1, 'The four-square catalogue has more than one root.')
    root = maximal[0]
    path = Path(certificate)
    opener = lzma.open if path.suffix == '.xz' else open
    with opener(path, 'rb') as stream:
        require(stream.read(len(MAGIC) + 1) == MAGIC + b'\x01',
                'The C4 premise certificate must use the original v1 rules.')
        stream.seek(0)
        statistics = verify_stream(stream, root['prefix'])
    return {'status': 'PASS-relative-to-stated-lemmas', 'root_mask': root['mask'],
            'incidence_types': len(profiles), 'four_square_types': len(maximal),
            'maximum_square_incidence': 3, 'proof': statistics,
            'scope': 'triangle-free quartic minimum-order 52-edge counterexample'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('certificate', type=Path, nargs='?',
                        default=Path(__file__).resolve().parents[1] / 'sources/eleven-quartic-c4.bin.xz')
    args = parser.parse_args()
    print(json.dumps(verify(args.certificate), sort_keys=True))
    print('Premises: the square-cap and square-direction lemmas, including the marked-H22 '
          'characterization and 983 exceptional quartic lifts; the ordinary branch checker '
          'also uses its minimum-order and earlier-edge-minimum premises.')
    print('This excludes the four-square type, not all quartic graphs or all 52-edge graphs.')


if __name__ == '__main__':
    main()
