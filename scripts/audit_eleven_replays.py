#!/usr/bin/env python3
"""Recheck archived coverage and resume the required deterministic replays.

This supplements, and does not modify, the original source-hashed auditors.
The saved mathematical reductions and enumeration correctness remain required.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys

from replay_cache import ReplayCache, atomic_json, digest, executable_identity, verify_tasks


def main():
    if not __debug__:
        raise RuntimeError('Run without -O: assertions are verification steps.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--snapshot', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True)
    parser.add_argument('--scope', choices=['quartic'], required=True)
    parser.add_argument('--workers', type=int, default=8)
    parser.add_argument('--seconds', type=float, help='Stop scheduling replays after this many seconds; coverage checks are additional.')
    parser.add_argument('--replay-terminals', action='store_true')
    args = parser.parse_args()
    if args.workers < 1 or (args.seconds is not None and args.seconds <= 0):
        parser.error('Positive workers and time budget required.')
    if args.replay_terminals and args.scope != 'quartic':
        parser.error('--replay-terminals requires quartic.')
    snapshot = args.snapshot.resolve()
    work = args.work.resolve()
    sys.path.insert(0, str(snapshot / 'scripts'))
    from treewidth_cooperative import parse_run
    baseline = snapshot / 'sources/treewidth-eleven-quartic-complete-audit.json'
    original = json.loads(baseline.read_text())
    destination = work / ('resumable-' + args.scope)
    destination.mkdir(exist_ok=True)
    accounting = destination / 'accounting.json'
    # Always recheck records, source hashes, adaptive splits and frontier links.
    subprocess.run([sys.executable, str(snapshot / 'scripts/audit_treewidth_frontier_series.py'),
                    '--runs', *original['runs'], '--frontiers', *original['frontier_sha256'],
                    '--output', str(accounting)], check=True)
    series = json.loads(accounting.read_text())
    for field in ('roots', 'covered_roots', 'runs', 'frontier_sha256'):
        if series[field] != original[field]:
            raise RuntimeError(f'Coverage differs from archived series: {field}')
    if series['covered_roots'] != 5:
        raise RuntimeError('Unexpected coverage scope.')
    runs = [Path(p) for p in series['runs']]
    states = [json.loads((run / 'state.json').read_text()) for run in runs]
    visited = [set() for _ in runs]

    def visit(stage, key):
        if key in visited[stage]:
            return
        visited[stage].add(key)
        row = states[stage]['nodes'][key]
        if row['status'] == 'pending':
            if stage + 1 == len(runs):
                raise RuntimeError('Selected an unfinished profile.')
            visit(stage + 1, key)
        elif row['status'] in ('split', 'covered'):
            for child in row['children']:
                visit(stage, child)
        elif row['status'] != 'done' or row.get('retained_graphs'):
            raise RuntimeError('Unresolved graph in selected profile.')

    for root in series['roots']:
        if root['covered']:
            visit(0, root['key'])
    tasks = []
    state_hashes = {}
    for stage, run in enumerate(runs):
        state_hash = digest(run / 'state.json')
        if state_hash != series['audits'][stage]['state_sha256']:
            raise RuntimeError('Checkpoint changed during accounting.')
        state_hashes[str(run)] = state_hash
        config = json.loads((run / 'manifest.json').read_text())
        cooperative = config.get('format') == 'cooperative-v1'
        if not cooperative and not args.replay_terminals:
            continue  # Adaptive splits were replayed by the series auditor.
        executable = run / 'complete'
        binary = executable_identity(executable)
        for key in sorted(visited[stage]):
            node = states[stage]['nodes'][key]
            if node['status'] == 'pending':
                continue
            if not cooperative:
                if node['status'] == 'done':
                    tasks.append({'mode': 'adaptive-terminal',
                                  'executable': str(executable), 'executable_identity': binary,
                                  'state_sha256': state_hash,
                                  'record_sha256': state_hash,
                                  'prefix': node['prefix'], 'key': key,
                                  'stdout': '', 'report': {'kind': int(node['prefix'].split()[0]),
                                                           'patterns': 0, 'residues': 0}})
                continue
            path = run / (key + '.json')
            record_hash = digest(path)
            if record_hash != node['record_sha256']:
                raise RuntimeError(f'Changed record: {path}')
            record = json.loads(path.read_text())
            prefixes, graphs, report = parse_run(record['stdout'], record['stderr'])
            if graphs:
                raise RuntimeError('Unresolved graph in replay record.')
            if prefixes or args.replay_terminals:
                tasks.append({'executable': str(executable), 'executable_identity': binary,
                              'state_sha256': state_hash, 'record_sha256': record_hash,
                              'prefix': node['prefix'], 'key': key,
                              'stdout': record['stdout'], 'report': report})
    identity = {'auditor': digest(Path(__file__)),
                'cache': digest(Path(__file__).with_name('replay_cache.py')),
                'snapshot_inventory': digest(snapshot / 'SHA256.json'),
                'python': sys.version, 'python_executable': digest(sys.executable)}
    cache = ReplayCache(work / 'verified-replays', identity)
    modes = {mode: sum(task.get('mode', 'cooperative') == mode for task in tasks)
             for mode in ('adaptive-terminal', 'cooperative')}
    print(f'Required replay tasks: {len(tasks)}; {modes}', flush=True)
    results = verify_tasks(tasks, cache, parse_run, args.workers, args.seconds)
    for run, expected in state_hashes.items():
        if digest(Path(run) / 'state.json') != expected:
            raise RuntimeError('Checkpoint changed during replay.')
    result = {'status': 'required_replays_verified' if results['complete'] else 'partial_replay',
              'scope': args.scope, 'terminal_replays': args.replay_terminals,
              'covered_roots': series['covered_roots'], 'counts': results, 'task_modes': modes,
              'accounting_sha256': digest(accounting), 'state_sha256': state_hashes,
              'verifier': identity,
              'note': 'Local receipts record previous checks; remove verified-replays for an independent fresh replay.'}
    atomic_json(destination / 'summary.json', result)
    print(json.dumps(result['counts']), flush=True)
    if not results['complete']:
        print('Time budget reached. Rerun with --resume to keep completed checks.', flush=True)
        raise SystemExit(2)


if __name__ == '__main__':
    main()
