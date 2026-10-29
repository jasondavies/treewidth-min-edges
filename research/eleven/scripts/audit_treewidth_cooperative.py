"""Check cooperative coverage records; optionally replay every C search slice.

The original completion checker's correctness assumptions still apply.
Replay verifies the saved computation, not the mathematical prerequisites.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess

from run_treewidth_edge_checks import digest
from treewidth_cooperative import parse_run


def main():
    if not __debug__:
        raise RuntimeError('Run without -O.')
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('directory', type=Path)
    p.add_argument('--replay', action='store_true')
    p.add_argument('--verify-cuts', action='store_true', help='Replay cut records; terminal runs retain their original verification.')
    p.add_argument('--workers', type=int, default=1)
    args = p.parse_args()
    if args.workers < 1:
        p.error('Positive worker count required.')
    out = args.directory.resolve()
    config = json.loads((out / 'manifest.json').read_text())
    assert config['format'] == 'cooperative-v1'
    for name, checksum in config['sha256'].items():
        assert digest(Path(name)) == checksum, name
    raw = (out / 'state.json').read_bytes()
    state = json.loads(raw)
    nodes = state['nodes']
    prefix_keys = {}

    def identifiers(prefixes):
        if not prefixes:
            return set()
        missing = list(dict.fromkeys(p for p in prefixes if p not in prefix_keys))
        if missing:
            keys = subprocess.check_output([str(out / 'canonical')], input='\n'.join(missing) + '\n', text=True).splitlines()
            assert len(keys) == len(missing)
            prefix_keys.update(zip(missing, keys))
        result = set()
        for prefix in prefixes:
            key = prefix_keys[prefix]
            kind, depth = map(int, prefix.split()[:2])
            encoded = f'{kind}:{depth}:{key}'
            k = hashlib.sha256(encoded.encode()).hexdigest()
            assert nodes[k]['key'] == encoded
            result.add(k)
        return result

    # Batch nauty calls rather than starting one process per terminal node.
    prefixes = [r['prefix'] for r in nodes.values()]
    for offset in range(0, len(prefixes), 4096):
        identifiers(prefixes[offset:offset + 4096])
    assert identifiers(Path(config['prefixes']).read_text().splitlines()) == set(state['roots'])
    answers = {}
    counts = {'completed_terminal_nodes': 0, 'split_nodes': 0, 'pending_nodes': 0}
    replay_tasks = []

    def visit(k):
        if k in answers:
            return answers[k]
        r = nodes[k]
        assert identifiers([r['prefix']]) == {k}
        if r['status'] == 'pending':
            counts['pending_nodes'] += 1
            answers[k] = False
            return False
        record_path = out / (k + '.json')
        assert digest(record_path) == r['record_sha256']
        record = json.loads(record_path.read_text())
        assert record['input_sha256'] == hashlib.sha256(r['prefix'].encode()).hexdigest()
        prefixes, graphs, report = parse_run(record['stdout'], record['stderr'])
        assert report == record['slice'] and graphs == r['retained_graphs'] == []
        terminal = [json.loads(line.removeprefix('TEMPLATE_RESULT '))
                    for line in record['stderr'].splitlines() if line.startswith('TEMPLATE_RESULT ')]
        assert len(terminal) == 1 and terminal[0]['residues'] == 0
        if args.replay or (args.verify_cuts and prefixes):
            replay_tasks.append((r['prefix'], record['stdout'], report))
        if not prefixes:
            assert r['status'] == 'done'
            counts['completed_terminal_nodes'] += 1
            answers[k] = True
        else:
            assert r['status'] in ('split', 'covered')
            assert all(int(line.split()[1]) > r['depth'] for line in prefixes)
            children = identifiers(prefixes)
            assert children == set(r['children'])
            counts['split_nodes'] += 1
            children_done = [visit(c) for c in sorted(children)]
            answers[k] = all(children_done)
            if r['status'] == 'covered':
                assert answers[k]
        return answers[k]

    completed = [visit(k) for k in state['roots']]

    def replay(task):
        prefix, stdout, report = task
        q = subprocess.run([str(out / 'complete'), 'replay', str(report['cut'])],
                           input=prefix + '\n', capture_output=True, text=True, check=True)
        assert q.stdout == stdout
        assert parse_run(q.stdout, q.stderr)[2] == report

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for _ in pool.map(replay, replay_tasks):
            pass
    print(json.dumps({'status': 'complete_supplied_family' if all(completed) else 'partial_accounting_consistent',
                      'roots': len(completed), 'covered_roots': sum(completed),
                      'reachable_nodes': len(answers), **counts, 'slices_replayed': args.replay,
                      'cuts_replayed': args.replay or args.verify_cuts,
                      'replayed_records': len(replay_tasks),
                      'state_sha256': hashlib.sha256(raw).hexdigest(),
                      'script_sha256': digest(Path(__file__))}, indent=2))


if __name__ == '__main__':
    main()
