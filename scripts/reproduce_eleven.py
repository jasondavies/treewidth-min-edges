#!/usr/bin/env python3
"""Check the retained enumeration inputs and the treewidth-eleven witness.

This is a quick check, not the complete lower-bound verification.
See verification-eleven.md for the full computational route.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / 'research/eleven'


def check_bundle():
    manifest = json.loads((SNAPSHOT / 'SHA256.json').read_text())
    for name, expected in manifest.items():
        with (SNAPSHOT / name).open('rb') as stream:
            actual = hashlib.file_digest(stream, 'sha256').hexdigest()
        if actual != expected:
            raise RuntimeError(f'Snapshot checksum mismatch: {name}')
    print(f'PASS: {len(manifest)} retained enumeration inputs match their original hashes.', flush=True)


def main():
    if not __debug__:
        raise RuntimeError('Run without -O: assertions are verification steps.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hashes-only', action='store_true')
    args = parser.parse_args()
    check_bundle()
    if not args.hashes_only:
        subprocess.run([sys.executable, str(ROOT / 'scripts/verify_witness53.py')], check=True)
        print('PASS: integrity and witness. The complete lower bound was not replayed.')


if __name__ == '__main__':
    main()
