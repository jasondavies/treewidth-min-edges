"""Exhaust graph-completion families, preserving work at every time slice.

Only an empty completed frontier excludes a family. Results containing
graphs require separate treewidth certificates. STOP requests a clean stop.
"""
import argparse
import fcntl
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
import hashlib
import json
from pathlib import Path
import subprocess
import time

from run_treewidth_edge_checks import digest
from treewidth_cooperative import build, dependencies, parse_run


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'canonical-source', 'output', 'prefixes'):
        p.add_argument('--' + name, type=Path, required=True)
    p.add_argument('--workers', type=int, default=16)
    p.add_argument('--seconds', type=float, default=1800)
    p.add_argument('--slice-seconds', type=float, default=1)
    args = p.parse_args()
    if min(args.workers, args.seconds, args.slice_seconds) <= 0:
        p.error('Positive limits required.')
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    # Separate tool sessions may outlive the session that launched them.
    # Never let two coordinators overwrite the same checkpoint directory.
    lock = (out / '.coordinator.lock').open('w')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise SystemExit(f'Another coordinator is using {out}')
    manifest = {'format': 'cooperative-v1', 'source': str(args.source.resolve()),
                'canonical_source': str(args.canonical_source.resolve()),
                'prefixes': str(args.prefixes.resolve()),
                'sha256': dependencies(args.source, args.canonical_source)}
    manifest['sha256'].update({str(Path(__file__).resolve()): digest(Path(__file__)),
                               str(args.prefixes.resolve()): digest(args.prefixes)})
    mp = out / 'manifest.json'
    if mp.exists():
        assert json.loads(mp.read_text()) == manifest, 'Changed source: use another output directory.'
    else:
        mp.write_text(json.dumps(manifest, indent=2) + '\n')
    build(args.source.resolve(), args.canonical_source.resolve(), out)
    sp = out / 'state.json'
    state = json.loads(sp.read_text()) if sp.exists() else {'roots': [], 'nodes': {}}
    nodes = state['nodes']

    def register(prefixes):
        if not prefixes:
            return []
        keys = subprocess.check_output([str(out / 'canonical')],
                    input='\n'.join(prefixes) + '\n', text=True).splitlines()
        assert len(keys) == len(prefixes)
        result = set()
        for prefix, key in zip(prefixes, keys):
            kind, depth, *_ = map(int, prefix.split())
            encoded = f'{kind}:{depth}:{key}'
            identifier = hashlib.sha256(encoded.encode()).hexdigest()
            if identifier in nodes:
                assert nodes[identifier]['key'] == encoded
            else:
                nodes[identifier] = {'key': encoded, 'prefix': prefix,
                                     'depth': depth, 'status': 'pending'}
            result.add(identifier)
        return sorted(result)

    if not state['roots']:
        state['roots'] = register(args.prefixes.read_text().splitlines())
    began = time.monotonic()
    candidate = any(r.get('retained_graphs') for r in nodes.values())

    def save():
        for k in sorted(nodes, key=lambda k: nodes[k]['depth'], reverse=True):
            r = nodes[k]
            if r['status'] == 'split' and all(nodes[c]['status'] in ('done', 'covered') for c in r['children']):
                r['status'] = 'covered'
        covered = sum(nodes[k]['status'] in ('done', 'covered') for k in state['roots'])
        report = {'status': 'candidate_needs_certificate' if candidate else
                            'complete' if covered == len(state['roots']) else 'partial',
                  'nodes': len(nodes), 'pending': sum(r['status'] == 'pending' for r in nodes.values()),
                  'roots': len(state['roots']), 'covered_roots': covered,
                  'seconds_this_round': time.monotonic() - began}
        tmp = sp.with_suffix('.tmp')
        tmp.write_text(json.dumps(state) + '\n')
        tmp.replace(sp)
        (out / 'summary.json').write_text(json.dumps(report, indent=2) + '\n')
        print(report, flush=True)

    def work(identifier):
        prefix = nodes[identifier]['prefix']
        q = subprocess.run([str(out / 'complete'), 'slice', str(args.slice_seconds)],
                           input=prefix + '\n', text=True, capture_output=True, check=True)
        prefixes, graphs, report = parse_run(q.stdout, q.stderr)
        record = {'input_sha256': hashlib.sha256(prefix.encode()).hexdigest(),
                  'stdout': q.stdout, 'stderr': q.stderr, 'slice': report}
        path = out / (identifier + '.json')
        path.write_text(json.dumps(record) + '\n')
        return prefixes, graphs, digest(path)

    save()
    last_saved = time.monotonic()
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        active = {}
        while True:
            stopping = candidate or time.monotonic() - began >= args.seconds or (out / 'STOP').exists()
            if not stopping:
                pending = sorted((k for k, r in nodes.items() if r['status'] == 'pending' and k not in active.values()),
                                 key=lambda k: (-nodes[k]['depth'], k))
                for k in pending[:args.workers - len(active)]:
                    active[pool.submit(work, k)] = k
            if not active:
                break
            finished, _ = wait(active, return_when=FIRST_COMPLETED)
            for future in finished:
                k = active.pop(future)
                prefixes, graphs, checksum = future.result()
                r = nodes[k]
                assert all(int(line.split()[1]) > r['depth'] for line in prefixes)
                r.update(status='split' if prefixes else 'done', retained_graphs=graphs,
                         record_sha256=checksum)
                if prefixes:
                    r['children'] = register(prefixes)
                if graphs:
                    r['status'] = 'candidate'
                    candidate = True
            if time.monotonic() - last_saved >= 10:
                save()
                last_saved = time.monotonic()
    save()


if __name__ == '__main__':
    main()
