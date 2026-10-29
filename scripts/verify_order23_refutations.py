#!/usr/bin/env python3
"""Verify catalogue exclusions against an independently checked order23 cover."""
import argparse
import io
import json
import lzma
from pathlib import Path
from verify_profile_refutation import require
from verify_branch_refutation import PREMISE_NOTICE, verify_certificate
from branch_certificate_binary import verify_stream
from branch_certificate_bundle import MAGIC, iter_members, member_prefix, open_input
from verify_order23_coverage import verify as verify_coverage


def read_json(path):
    raw = path.read_bytes()
    return json.loads(lzma.decompress(raw) if path.suffix == '.xz' else raw)


def verify_bundle(bundle, coverage):
    checked = verify_coverage(coverage)
    required = set(checked['referenced_indices'])
    require(bundle.get('format') == 'order23-refutations-v1', 'Wrong bundle format.')
    require(isinstance(bundle.get('cases'), list), 'Missing cases.')
    seen, statistics = set(), []
    for case in bundle['cases']:
        require(isinstance(case, dict), 'Invalid case.')
        index = case.get('catalogue_index')
        require(type(index) is int and 0 <= index < len(coverage['catalogue']),
                'Invalid catalogue index.')
        require(index not in seen, 'Duplicate catalogue index.')
        statistics.append((index, verify_certificate(case['certificate'],
                                                    coverage['catalogue'][index])))
        seen.add(index)
    return sorted(required - seen), statistics, len(required)



def verify_binary_bundle(stream, coverage):
    """Check each exact catalogue root against independently verified coverage."""
    checked = verify_coverage(coverage)
    required = set(checked['referenced_indices'])
    catalogue = coverage['catalogue']
    indices = {tuple(prefix): index for index, prefix in enumerate(catalogue)}
    require(len(indices) == len(catalogue), 'Duplicate catalogue roots.')
    seen, statistics = set(), []
    for data in iter_members(stream, expected_order=23):
        prefix = member_prefix(data, 23)
        index = indices.get(tuple(prefix))
        require(index is not None and index not in seen,
                'Unknown or duplicate catalogue root.')
        statistics.append((index, verify_stream(io.BytesIO(data), catalogue[index])))
        seen.add(index)
    return sorted(required - seen), statistics, len(required)


def verify_file(path, coverage):
    with open_input(path) as stream:
        binary = stream.read(len(MAGIC)) == MAGIC
        stream.seek(0)
        if binary:
            return verify_binary_bundle(stream, coverage)
        return verify_bundle(json.load(stream), coverage)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle', type=Path)
    parser.add_argument('--coverage', type=Path, default=Path(__file__).resolve().parents[1]
                        / 'sources' / 'eleven-order23-coverage.json.xz')
    args = parser.parse_args()
    missing, statistics, total = verify_file(args.bundle, read_json(args.coverage))
    print(f'Verified {total-len(missing)}/{total} required order23 family exclusions.')
    print(PREMISE_NOTICE)
    if missing:
        print('INCOMPLETE; remaining catalogue indices:', ' '.join(map(str, missing)))
        return 2
    print('PASS: order23 is excluded under the written minimum-counterexample premises.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
