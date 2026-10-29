#!/usr/bin/env python3
"""Verify all forty order-25 profiles from stored proofs and two hand reductions.

Earlier classifications remain explicit premises. --check-new-premises also
replays the three finite ingredients of the cubic-neighbor theorems.
"""
import argparse
import io
import json
from itertools import permutations
from pathlib import Path
import tempfile
import time

from branch_certificate_binary import verify_stream
from branch_certificate_bundle import member_prefix
from cubic_cap_reconstruction import require
from order25_profiles import enumerate_profiles, profile_key
from pack_branch_bundle import input_members, pack_members
from verify_branch_refutation import PREMISE_NOTICE
from verify_order25_claw import verify as verify_claw
from verify_profile_refutation import Interval


def canonical_mapping(prefix, target):
    """Return an explicitly checked high/low-preserving root isomorphism."""
    require(profile_key(prefix) == profile_key(target), 'Different profile classes')
    for high_map in permutations(range(4)):
        groups = {}
        for v in range(4, 25):
            mask = target[2 + v] & 15
            groups.setdefault(mask, []).append(v)
        mapping = list(high_map)
        for v in range(4, 25):
            mask = sum(1 << high_map[u] for u in range(4) if prefix[2 + v] >> u & 1)
            choices = groups.get(mask)
            if not choices:
                break
            mapping.append(choices.pop())
        if len(mapping) != 25:
            continue
        if all(sum(1 << mapping[u] for u in range(25) if prefix[2 + v] >> u & 1)
               == target[2 + mapping[v]] for v in range(25)):
            require(sorted(mapping) == list(range(25)), 'Invalid root permutation')
            return mapping
    raise ValueError('No explicit isomorphism to the canonical profile')


def default_paths(repository):
    sources = Path(repository) / 'sources'
    paths = [sources / 'eleven-order25-refutations.bin.xz']
    for directory in ('eleven-order25-private-cap', 'eleven-order25-broad-cap',
                      'eleven-order25-one-high'):
        paths.extend(sorted((sources / directory).glob('*.bin.xz')))
    return paths


def verify_private_cycle(prefix):
    """Check the exact root hypothesis of the written private-C4 corollary."""
    state = Interval(prefix)
    high = set(range(4))
    require(prefix[0] == 25 and state.upper == [5] * 4 + [4] * 21,
            'Expected the order25 degree profile')
    require(all(state.known[v] == state.possible[v] and len(state.known[v]) == 5
                and len(state.known[v] & high) == 2 for v in high),
            'Expected exact high neighborhoods inducing a four-cycle')
    require(all(len(state.known[v] & high) <= 1 for v in range(4, 25)),
            'The cycle corollary requires private low attachments')
    return {'cubic_boundary_minimum': 18, 'quartic_boundary_maximum': 15}


def finish_coverage(profiles, proved):
    """The two named hand cases cannot silently cover a missing branch proof."""
    cycle = tuple(map(int, '011110'))
    claw = tuple(map(int, '001011'))
    require(cycle in profiles and claw in profiles, 'Missing hand-reduction catalogue roots')
    covered = set(proved) | {cycle, claw}
    require(covered == set(profiles), 'Incomplete order25 coverage')
    return covered


def verify(repository, paths=None, *, workers=1, check_new_premises=False, native=False):
    require(type(workers) is int and workers >= 1, 'Worker count must be positive')
    require(type(check_new_premises) is bool, 'check_new_premises must be a boolean')
    started = time.monotonic()
    repository = Path(repository)
    profiles = enumerate_profiles()
    paths = default_paths(repository) if paths is None else [Path(path) for path in paths]
    seen = set()
    root_maps = []

    def members():
        for path in paths:
            for data in input_members(path, 25):
                prefix = member_prefix(data, 25)
                key = profile_key(prefix)
                require(key in profiles, 'Unknown root')
                mapping = canonical_mapping(prefix, profiles[key])
                require(key not in seen, 'Duplicate profile proof')
                seen.add(key)
                root_maps.append({'profile': ''.join(map(str, key)), 'permutation': mapping})
                yield data

    proof_stats = []
    if workers == 1:
        for data in members():
            prefix = member_prefix(data, 25)
            proof_stats.append(verify_stream(io.BytesIO(data), prefix))
    else:
        # Each worker freshly replays its assigned member. No saved verification
        # report is accepted as input. This optional path requires Python 3.11.
        from verify_branch_bundle_parallel import verify_parallel
        with tempfile.TemporaryDirectory(prefix='tw11-order25-complete-') as directory:
            bundle = Path(directory) / 'proofs.bin'
            pack_members(members(), bundle, 25)
            checked = verify_parallel(bundle, Path(directory) / 'reports', workers)
            require(checked['all_supplied_verified'], 'A supplied branch proof failed')
            require(checked['supplied_members'] == len(seen), 'Parallel member-count mismatch')
            proof_stats = [member['statistics'] for member in checked['members']]
    cycle = verify_private_cycle(profiles[tuple(map(int, '011110'))])
    claw = verify_claw(profiles[tuple(map(int, '001011'))], repository)
    covered = finish_coverage(profiles, seen)
    premises = None
    if check_new_premises:
        from verify_two_k4_incidence import verify_all as verify_two_k4
        from verify_cubic_neighbor_cap import check, order_proposer
        from verify_one_high_cubic_cap import verify_all as verify_one_high
        premises = {'two_k4': verify_two_k4()}
        with order_proposer(native=native) as propose:
            premises['no_isolate_cap'] = check(repository, propose, without_isolate=True)
            premises['one_high_cap'] = verify_one_high(repository, propose)
    return {'status': 'verified-all-order25-profiles-relative-to-stated-premises',
            'catalogue_profiles': len(profiles), 'branch_proofs': len(seen),
            'covered_profiles': len(covered), 'cycle': cycle, 'claw': claw,
            'root_maps': root_maps,
            'proof_statistics': proof_stats, 'new_premises': premises,
            'workers': workers, 'seconds': time.monotonic() - started}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--workers', type=int, default=1,
                        help='optional parallel replay; requires Python 3.11 or later')
    parser.add_argument('--check-new-premises', action='store_true')
    parser.add_argument('--native', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    report = verify(args.repository, workers=args.workers,
                    check_new_premises=args.check_new_premises, native=args.native)
    if args.output:
        args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(f"PASS: {report['covered_profiles']}/{report['catalogue_profiles']} order25 profiles; "
          f"{report['branch_proofs']} freshly checked branch proofs and two hand reductions.")
    print(PREMISE_NOTICE)
    print('Claw reduction additionally requires the stated 29/34/35/36 classifications and weighted-packing check.')
    print('Other vertex counts and the earlier classification proofs remain separate dependencies.')


if __name__ == '__main__':
    main()
