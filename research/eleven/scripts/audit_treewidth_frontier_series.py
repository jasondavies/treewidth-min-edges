"""Compose any number of audited completion frontiers, oldest to newest.

Each exported frontier must equal the reachable pending nodes of its
parent. Its child must start with precisely those canonical roots. This
also handles cooperative continuations whose cuts span several depths.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from run_treewidth_edge_checks import ROOT, digest


def main():
    if not __debug__:
        raise RuntimeError('Run without -O.')
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--runs', type=Path, nargs='+', required=True)
    p.add_argument('--frontiers', type=Path, nargs='*', default=[])
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--replay-cooperative', action='store_true')
    p.add_argument('--verify-cuts', action='store_true')
    p.add_argument('--workers', type=int, default=1)
    p.add_argument('--cached-audit', type=Path, action='append', default=[],
                   help='Reuse an earlier cooperative replay for an identical state; always recheck accounting and source hashes.')
    args = p.parse_args()
    runs = [q.resolve() for q in args.runs]
    assert len(args.frontiers) + 1 == len(runs)
    states, audits = [], []
    cached = {}
    for path in args.cached_audit:
        record = json.loads(path.read_text())
        key = record['state_sha256']
        assert key not in cached, 'Duplicate cached state audit.'
        cached[key] = (path, record)

    for run in runs:
        raw = (run / 'state.json').read_bytes()
        state = json.loads(raw)
        config = json.loads((run / 'manifest.json').read_text())
        checkpoint_hash = hashlib.sha256(raw).hexdigest()
        prior = cached.get(checkpoint_hash)
        reuse = False

        if config.get('format') == 'cooperative-v1':
            command = [sys.executable, str(ROOT / 'scripts/audit_treewidth_cooperative.py'), str(run)]
            if prior:
                previous = prior[1]
                assert previous['script_sha256'] == digest(ROOT / 'scripts/audit_treewidth_cooperative.py')
                reuse = (previous.get('slices_replayed', False) if args.replay_cooperative
                         else previous.get('cuts_replayed', False) if args.verify_cuts else True)
            if args.replay_cooperative and not reuse:
                command.append('--replay')
            elif args.verify_cuts and not reuse:
                command.append('--verify-cuts')
            command.extend(['--workers', str(args.workers)])
        else:
            command = [sys.executable, str(ROOT / 'scripts/audit_treewidth_adaptive.py'), str(run), '--verify-splits']
        report = json.loads(subprocess.check_output(command, text=True))
        assert report['state_sha256'] == hashlib.sha256(raw).hexdigest(), 'Checkpoint changed during audit.'
        if reuse:
            previous = prior[1]
            for field in ('status', 'roots', 'covered_roots', 'reachable_nodes',
                          'completed_terminal_nodes', 'split_nodes', 'pending_nodes',
                          'state_sha256', 'script_sha256'):
                assert report[field] == previous[field], ('Cached audit mismatch', field)
            for field in ('slices_replayed', 'cuts_replayed', 'replayed_records'):
                report[field] = previous[field]
            report['cached_replay_audit'] = str(prior[0].resolve())
            report['cached_replay_audit_sha256'] = digest(prior[0])
        states.append(state)
        audits.append(report)

    def pending(state):
        seen, result = set(), set()

        def visit(k):
            if k in seen:
                return
            seen.add(k)
            row = state['nodes'][k]
            if row['status'] == 'pending':
                result.add(k)
            elif row['status'] in ('split', 'covered'):
                for child in row['children']:
                    visit(child)
            else:
                assert row['status'] == 'done' and not row.get('retained_graphs')

        for k in state['roots']:
            visit(k)
        return result

    for i, frontier in enumerate(args.frontiers):
        f = json.loads((frontier / 'frontier.json').read_text())
        assert Path(f['parent']).resolve() == runs[i]
        assert digest(runs[i] / 'manifest.json') == f['parent_manifest_sha256']
        assert audits[i]['state_sha256'] == f['parent_state_sha256']
        assert digest(frontier / 'prefixes.txt') == f['prefixes_sha256']
        expected = pending(states[i])
        assert expected == set(f['pending_keys']) == set(states[i + 1]['roots'])
        child_config = json.loads((runs[i + 1] / 'manifest.json').read_text())
        assert digest(Path(child_config['prefixes'])) == f['prefixes_sha256']
        lines = (frontier / 'prefixes.txt').read_text().splitlines()
        for run in runs[i:i + 2]:
            keys = subprocess.check_output([str(run / 'canonical')],
                       input='\n'.join(lines) + '\n', text=True).splitlines()
            assert len(keys) == len(lines)
            identifiers = set()
            for line, key in zip(lines, keys):
                kind, depth = map(int, line.split()[:2])
                identifiers.add(hashlib.sha256(f'{kind}:{depth}:{key}'.encode()).hexdigest())
            assert identifiers == expected

    memo = {}

    def covered(i, k):
        if (i, k) in memo:
            return memo[i, k]
        r = states[i]['nodes'][k]
        if r['status'] == 'pending':
            answer = covered(i + 1, k) if i + 1 < len(states) else False
        elif r['status'] in ('split', 'covered'):
            answer = all(covered(i, c) for c in r['children'])
        else:
            assert r['status'] == 'done'
            answer = True
        memo[i, k] = answer
        return answer

    roots = [{'key': k, 'prefix': states[0]['nodes'][k]['prefix'], 'covered': covered(0, k)}
             for k in states[0]['roots']]
    report = {'status': 'complete_original_family' if all(r['covered'] for r in roots)
                        else 'partial_frontier_series_consistent',
              'roots': roots, 'covered_roots': sum(r['covered'] for r in roots),
              'audits': audits, 'runs': list(map(str, runs)),
              'frontier_sha256': {str(f): digest(f / 'frontier.json') for f in args.frontiers},
              'script_sha256': digest(Path(__file__))}
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    print(report['status'], report['covered_roots'], '/', len(roots))


if __name__ == '__main__':
    main()
