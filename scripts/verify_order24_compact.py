#!/usr/bin/env python3
"""Verify complete order-24 coverage using the compact proof components.

The default checks short proofs first, then replays the remaining root proofs.
--check-premises additionally reruns the three new finite lemmas; the earlier
small-edge classifications and minimum-counterexample reduction remain premises.
This command does not establish the full 52-edge exclusion.
"""
import argparse
import io
import json
import os
from pathlib import Path
import time

from branch_certificate_binary import read_header, verify_stream
from branch_certificate_bundle import MAX_MEMBER_BYTES, iter_members, member_prefix, open_input
from verify_order24_catalogue import read_certificate, verify as verify_catalogue
from verify_order24_smoothing import verify as verify_smoothing28
from verify_order24_smoothing29 import verify as verify_smoothing29
from verify_order24_smoothing34 import verify as verify_smoothing34
from verify_order24_smoothing35 import verify as verify_smoothing35
from verify_order24_twenty_residue import verify_recipes
from verify_cubic_neighbor_cap import order_proposer
from verify_profile_refutation import require

PREMISES = (
    'Premises: the minimum-counterexample reduction, earlier edge minima and '
    'the complete earlier 28/29/34/35/specified 36-edge classifications; the '
    'two-K4 incidence lemma, marked-H22 residue theorem and complete exceptional '
    'nonadjacent-pair reconstruction. See proof-eleven-order24-compact.md. '
    'Use --check-premises to regenerate the three new finite checks.'
)
MARKED_INDICES = (35, 37, 155)


def verify_binary_bundle(path, profiles, proved, *, replay_redundant=False, progress=None):
    """Check every exact root; replay bodies not already excluded by a checked proof.

    `proved` is an internal set derived only from successful short checkers.
    Skipped legacy proof bytes are not used as mathematical evidence.
    """
    indices = {tuple(prefix): index for index, prefix in enumerate(profiles)}
    require(len(indices) == len(profiles), 'Duplicate catalogue roots.')
    seen, replayed, skipped = set(), [], []
    for data in iter_members_from_file(path):
        prefix = member_prefix(data, 24)
        index = indices.get(tuple(prefix))
        require(index is not None and index not in seen, 'Unknown or duplicate catalogue root.')
        seen.add(index)
        if index in proved and not replay_redundant:
            skipped.append(index)
        else:
            verify_stream(io.BytesIO(data), profiles[index])
            replayed.append(index)
        if progress and (len(seen) % 25 == 0):
            progress('ordinary_member_progress', {'parsed': len(seen), 'last_root': index,
                     'replayed': len(replayed), 'redundant_bodies_skipped': len(skipped)})
    return {'stored_roots': len(seen), 'replayed_indices': replayed, 'skipped_indices': skipped}


def iter_members_from_file(path):
    with open_input(path) as stream:
        yield from iter_members(stream, expected_order=24)


def verify_marked_member(path, expected_prefix, *, already_proved=False):
    """Require the exact root even when another checked proof makes this body redundant."""
    with open_input(path) as stream:
        _, prefix = read_header(stream)
        require(prefix == expected_prefix, 'Wrong marked-residue root prefix.')
        stream.seek(0)
        if not already_proved:
            verify_stream(stream, expected_prefix)
            return True
        # Validate the complete compressed input while ignoring unused proof bytes.
        remaining = MAX_MEMBER_BYTES
        while remaining:
            chunk = stream.read(min(remaining, 1 << 20))
            if not chunk:
                return False
            remaining -= len(chunk)
        require(not stream.read(1), 'Oversized marked-residue proof.')
        return False


def coverage_summary(total, components):
    """Require exact union coverage; independent redundant proofs are harmless."""
    require(type(total) is int and total > 0, 'Invalid catalogue size.')
    covered, names = set(), set()
    summary = []
    for name, indices in components:
        require(isinstance(name, str) and name and name not in names, 'Duplicate component name.')
        names.add(name)
        require(isinstance(indices, (list, tuple)), 'Invalid component coverage list.')
        require(all(type(index) is int and 0 <= index < total for index in indices),
                'Unknown catalogue index.')
        own = set(indices)
        require(len(own) == len(indices), 'Duplicate root within one component.')
        summary.append({'component': name, 'proved_roots': len(own),
                        'newly_covered_roots': len(own - covered)})
        covered.update(own)
    missing = sorted(set(range(total)) - covered)
    require(not missing, 'Incomplete order-24 coverage; missing roots: ' + repr(missing))
    return {'catalogue_roots': total, 'covered_roots': len(covered), 'components': summary}


def check_new_premises(repository, *, native=False, compiler=None, progress=None):
    # Imports are lazy so ordinary proof replay does not prepare a producer.
    from verify_two_k4_incidence import verify_all as verify_two_k4
    from verify_marked_residue_reconstructions import regenerate
    from verify_exceptional_nonadjacent_pair import verify_all as verify_lifts
    from quartic_order_programs import native_interpreter
    results = {}
    results['two_k4_incidence'] = verify_two_k4()
    if progress:
        progress('two_k4_incidence', results['two_k4_incidence'])
    results['marked_residue'] = regenerate(repository, native=native, compiler=compiler)
    if progress:
        progress('marked_residue', results['marked_residue'])
    command = compiler if compiler is not None else os.environ.get('CC', 'cc')
    if native:
        command += ' -march=native'
    with native_interpreter(command) as interpreter:
        results['exceptional_nonadjacent_pair'] = verify_lifts(interpreter)
    if progress:
        progress('exceptional_nonadjacent_pair', results['exceptional_nonadjacent_pair'])
    return results


def verify_all(repository, *, native=False, compiler=None, check_premises=False,
               smoothing35=None, replay_redundant=False, progress=None):
    repository = Path(repository)
    sources = repository / 'sources'
    profiles = verify_catalogue(read_certificate(sources / 'eleven-order24-catalogue.bin.xz'))['profiles']
    components = []
    if progress:
        progress('catalogue', {'roots': len(profiles)})
    if check_premises:
        check_new_premises(repository, native=native, compiler=compiler, progress=progress)

    for name, filename, checker in (
        ('28_edge_smoothing', 'eleven-order24-smoothing.json', verify_smoothing28),
        ('29_edge_smoothing', 'eleven-order24-smoothing29.json', verify_smoothing29),
        ('34_edge_smoothing', 'eleven-order24-smoothing34.json', verify_smoothing34),
    ):
        result = checker(json.loads((sources / filename).read_text()), profiles)
        components.append((name, result['covered_indices']))
        if progress:
            progress(name, {'roots': len(result['covered_indices'])})

    smoothing35 = Path(smoothing35) if smoothing35 is not None else sources / 'eleven-order24-smoothing35.json'
    result = verify_smoothing35(json.loads(smoothing35.read_text()), profiles)
    components.append(('35_edge_smoothing', result['covered_indices']))
    if progress:
        progress('35_edge_smoothing', {'roots': len(result['covered_indices'])})

    recipes = json.loads((sources / 'eleven-order24-twenty-residue.json').read_text())
    with order_proposer(native=native, compiler=compiler) as propose:
        result = verify_recipes(recipes, profiles, repository, propose)
    components.append(('20_vertex_residue', result['catalogue_indices']))
    if progress:
        progress('20_vertex_residue', result)

    proved = {index for _, indices in components for index in indices}
    branch_report = verify_binary_bundle(sources / 'eleven-order24-refutations.bin.xz',
        profiles, proved, replay_redundant=replay_redundant, progress=progress)
    components.append(('ordinary_branch_proofs', branch_report['replayed_indices']))
    proved.update(branch_report['replayed_indices'])
    if progress:
        progress('ordinary_branch_proofs', branch_report)
    marked_replayed, marked_skipped = [], []
    for index in MARKED_INDICES:
        require(index < len(profiles), 'Missing marked-residue catalogue index.')
        checked = verify_marked_member(sources / f'eleven-order24-marked-{index}.bin.xz',
            profiles[index], already_proved=index in proved and not replay_redundant)
        (marked_replayed if checked else marked_skipped).append(index)
    components.append(('marked_residue_proofs', marked_replayed))
    if progress:
        progress('marked_residue_proofs', {'replayed_indices': marked_replayed,
                                         'skipped_indices': marked_skipped})
    result = coverage_summary(len(profiles), components)
    result.update(status='PASS-relative-to-named-classification-premises',
                  new_finite_premises_replayed=check_premises,
                  legacy_proof_bodies_replayed=len(branch_report['replayed_indices'])+len(marked_replayed),
                  redundant_proof_bodies_skipped=len(branch_report['skipped_indices'])+len(marked_skipped),
                  scope='order-24 minimum-counterexample exclusion only')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repository', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--check-premises', action='store_true',
                        help='Rerun two-K4, marked-H22 and all exceptional nonadjacent-pair lifts.')
    parser.add_argument('--native', action='store_true',
                        help='Enable -march=native in the untrusted C order proposers.')
    parser.add_argument('--compiler', help='C compiler command; defaults to CC or cc.')
    parser.add_argument('--smoothing35', type=Path, help='Alternative short 35-edge recipe file.')
    parser.add_argument('--replay-redundant', action='store_true',
                        help='Also replay legacy proof bodies whose roots already have checked short proofs.')
    args = parser.parse_args()
    started = time.monotonic()
    print(PREMISES, flush=True)
    def progress(component, result):
        print(json.dumps({'component': component, 'seconds': time.monotonic()-started,
                          'result': result}, sort_keys=True), flush=True)
    result = verify_all(args.repository, native=args.native, compiler=args.compiler,
                        check_premises=args.check_premises, smoothing35=args.smoothing35,
                        replay_redundant=args.replay_redundant, progress=progress)
    result['seconds'] = time.monotonic()-started
    print(json.dumps(result, sort_keys=True))
    print('PASS: every independently verified order-24 catalogue root is excluded.')
    print('This does not establish the full 52-edge exclusion.')


if __name__ == '__main__':
    main()
