#!/usr/bin/env python3
"""Finish order23 using checked family proofs and the two-anchor pigeonhole argument.

This is an explicit master verification command. The ordinary partial-bundle
verifier does not invoke this additional argument or claim complete exclusion.
"""
import argparse
import json
import sys
import tempfile
from itertools import combinations
from pathlib import Path

from verify_profile_refutation import Interval, require
from verify_branch_refutation import normalise, choices
from verify_order23_coverage import ROOT, DEGREE, verify as verify_coverage
from verify_order23_refutations import read_json, verify_file

HIGH = set(range(12))
LOW = set(range(12, 23))


def verify_anchor_finish(coverage, verified_indices):
    """Check the global argument, assuming the supplied indices have proved exclusions.

    The command-line entry point obtains these indices only by independently
    checking every supplied mathematical certificate with verify_file().
    """
    checked = verify_coverage(coverage)
    require(coverage.get('format') == 'order23-root-coverage-v2',
            'The anchor finish requires checked v2 refinements.')
    require(isinstance(verified_indices, (set, list, tuple))
            and all(type(i) is int and 0 <= i < len(coverage['catalogue'])
                    for i in verified_indices), 'Invalid verified index set.')
    proved = set(verified_indices)
    dependencies = {int(i): set(targets)
                    for i, targets in checked['refinement_dependencies'].items()}
    memo = {}
    def terminal_dependencies(index):
        if index not in dependencies:
            return {index}
        if index not in memo:
            memo[index] = set().union(*(terminal_dependencies(j)
                                       for j in dependencies[index]))
        return memo[index]
    # Inclusion maps need not preserve the designated completed anchors. Every
    # refinement must therefore be fully discharged before using any fingerprint.
    for index in dependencies:
        require(terminal_dependencies(index) <= proved,
                'A refinement has an unproved terminal dependency.')
    unresolved = set(checked['initial_referenced_indices']) - proved - dependencies.keys()

    root = coverage['proof']
    require(root[0] == 'b' and root[1] == 0, 'The original cover must first complete high vertex 0.')
    family = Interval(ROOT)
    normalise(family.known, family.possible, DEGREE)
    options = list(choices(family.known, family.possible, DEGREE, 0))
    require(len(root[2]) == len(options), 'Incomplete first-anchor coverage.')
    for selected, child in zip(options, root[2]):
        selected_high = [v for v in selected if v in HIGH]
        require(selected_high == list(range(1, len(selected_high) + 1)),
                'The initial high-neighbor class does not permit a designated neighbor at 1.')
        require(child == ['x'] or child[0] == 'r'
                or (child[0] == 'b' and child[1] == 1),
                'The cover must complete high vertex 1 next, or close the branch.')

    fingerprints = {}
    for index in sorted(unresolved):
        target = Interval(coverage['catalogue'][index])
        normalise(target.known, target.possible, DEGREE)
        saturated = [v for v in sorted(HIGH) if len(target.known[v]) == 5]
        require(saturated == [0, 1, 2], 'Exceptional target has different saturated high anchors.')
        high_degrees = [len(target.known[v] & HIGH) for v in saturated]
        require(all(d <= 4 for d in high_degrees),
                'An exceptional anchor need not have a low neighbor.')
        require(all(not (target.known[u] & target.known[v] & LOW)
                    for u, v in combinations(saturated, 2)),
                'Exceptional high anchors share a low neighbor.')
        fingerprints[str(index)] = high_degrees

    # The accompanying proof justifies the two rerootings through twin-orbit
    # branches. Completed anchors cannot be optional neighbors in later branches;
    # the original equality-c maps preserve their complete neighborhoods. Every
    # high has a low neighbor; a low shared by two highs would make them adjacent
    # and could be rooted at 0,1, contradicting the fingerprints above.
    require(len(HIGH) > len(LOW), 'No pigeonhole contradiction.')
    return {'proved_family_count': len(proved),
            'discharged_refinements': sorted(dependencies),
            'pigeonhole_original_indices': sorted(unresolved),
            'high_degrees_at_unresolved_anchors': fingerprints,
            'high_vertices': len(HIGH), 'low_vertices': len(LOW)}


def verify(bundle_path, coverage, workers=1, reports_directory=None):
    require(type(workers) is int and workers >= 1, 'Worker count must be positive.')
    if workers == 1:
        _, statistics, _ = verify_file(bundle_path, coverage)
        proved = {index for index, _ in statistics}
    else:
        require(sys.version_info >= (3, 11), 'Parallel verification requires Python 3.11 or newer.')
        from verify_branch_bundle_parallel import verify_parallel
        with tempfile.TemporaryDirectory(prefix='tw11-anchor-finish-') as directory:
            directory = Path(directory)
            cover_path = directory / 'coverage.json'
            cover_path.write_text(json.dumps(coverage))
            reports = reports_directory if reports_directory is not None else directory / 'reports'
            # This call verifies the actual supplied bytes afresh. No saved
            # report is accepted as evidence by the master command.
            report = verify_parallel(bundle_path, reports, workers, coverage=cover_path)
        require(report['order'] == 23 and report['all_supplied_verified'] is True
                and len(report['members']) == report['supplied_members']
                and all(member['verified'] is True for member in report['members']),
                'Not all supplied mathematical proofs passed verification.')
        proved = {int(member['code']) for member in report['members']}
    return verify_anchor_finish(coverage, proved)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('bundle', type=Path)
    parser.add_argument('--coverage', type=Path,
                        default=Path(__file__).resolve().parents[1]
                        / 'sources' / 'eleven-order23-coverage.json.xz')
    parser.add_argument('--workers', type=int, default=1,
                        help='fresh parallel proof checks; values above 1 require Python 3.11+')
    parser.add_argument('--reports', type=Path, help='optional directory for fresh parallel reports')
    args = parser.parse_args()
    result = verify(args.bundle, read_json(args.coverage), args.workers, args.reports)
    print('PASS: order23 is excluded under the written minimum-counterexample premises.')
    print(result)


if __name__ == '__main__':
    main()
