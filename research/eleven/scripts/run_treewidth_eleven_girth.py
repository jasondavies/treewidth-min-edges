"""Checkpointed exhaustive quartic order-26, girth-at-least-five subcase.

Only this subcase is covered. A negative treewidth answer is a candidate
requiring independent certification. GENREG is obtained separately.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path
import subprocess
import threading
import time
from build_genreg_treewidth import build
from run_treewidth_edge_checks import CC, ROOT, SOURCE, digest, run


def atomic_json(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--genreg-source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=16)
    parser.add_argument('--parts', type=int, default=256)
    parser.add_argument('--reuse-first-binary', type=Path)
    parser.add_argument('--reuse-first-log', type=Path)
    args = parser.parse_args()
    if min(args.workers, args.parts) < 1:
        parser.error('Positive worker and partition counts required.')
    if bool(args.reuse_first_binary) != bool(args.reuse_first_log):
        parser.error('Supply both first-partition reuse arguments, or neither.')
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    config = {'vertices': 26, 'degree': 4, 'girth_at_least': 5, 'width_bound': 10,
              'parts': args.parts, 'source_sha256': {str(p.relative_to(ROOT)): digest(p) for p in
                 (Path(__file__).resolve(), ROOT / 'scripts/build_genreg_treewidth.py',
                  ROOT / 'scripts/genreg_treewidth_eleven.c', SOURCE)},
              'upstream_sha256': {name: digest(args.genreg_source / name) for name in
                  ('gendef.h', 'genreg.c', 'main.c', 'optmid.c')},
              'compiler': run(CC + ['--version']).stdout.splitlines()[0]}
    manifest_path = out / 'manifest.json'
    executable = out / 'build/genreg-eleven'
    if manifest_path.exists():
        previous = json.loads(manifest_path.read_text())
        if previous['configuration'] != config or not executable.exists() or digest(executable) != previous['binary_sha256']:
            raise RuntimeError('Configuration or executable changed; use a new output directory.')
    else:
        if list(out.glob('part-*.json')):
            raise RuntimeError('Partition results exist without a manifest.')
        build(args.genreg_source, out / 'build', width=10)
        adapter = ROOT / 'scripts/genreg_treewidth_eleven.c'
        run(CC + ['-O3', '-std=c11', '-c', adapter, '-o', out / 'build/adapter.o'])
        run(CC + [out / ('build/' + name + '.o') for name in ('genreg', 'main', 'optmid', 'adapter')] + ['-o', executable])
        atomic_json(manifest_path, {'configuration': config, 'binary_sha256': digest(executable),
                                   'upstream': 'https://svn.code.sf.net/p/genreg/code/trunk/ (revision 5)'})
        # The generic builder's manifest describes its temporary adapter, not this one.
        atomic_json(out / 'build/build.json', json.loads(manifest_path.read_text()))

    def parse_log(path):
        lines = path.read_text().splitlines()
        summaries = [json.loads(line[len('GENREG_TW '):]) for line in lines if line.startswith('GENREG_TW ')]
        if len(summaries) != 1:
            raise RuntimeError(f'Missing or duplicate summary: {path}')
        row = summaries[0]
        if row['leaves'] != row['verified'] or row['negative'] != 0:
            raise RuntimeError(f'Incomplete positive verification: {path}')
        return row

    if args.reuse_first_binary and not (out / 'part-001.json').exists():
        if args.parts != 256 or digest(args.reuse_first_binary) != digest(executable):
            raise RuntimeError('Cannot reuse the first partition: binary or partition count differs.')
        log = args.reuse_first_log.read_text()
        if 'Teil 1 von 256' not in log:
            raise RuntimeError('Imported log does not identify partition 1 of 256.')
        (out / 'part-001.log').write_text(log)
        (out / 'part-001.g6').write_text('')
        row = parse_log(out / 'part-001.log')
        atomic_json(out / 'part-001.json', {'part': 1, 'status': 'verified', 'imported': True,
                                         'log_sha256': digest(out / 'part-001.log'), **row})

    stop = threading.Event()
    started = time.monotonic()
    processes = set()
    lock = threading.Lock()

    def work(i):
        stem = out / f'part-{i:03d}'
        checkpoint = stem.with_suffix('.json')
        if checkpoint.exists():
            row = json.loads(checkpoint.read_text())
            if row['status'] != 'verified' or row['part'] != i or digest(stem.with_suffix('.log')) != row['log_sha256']:
                raise RuntimeError(f'Invalid checkpoint {checkpoint}')
            if stem.with_suffix('.g6').read_text() or parse_log(stem.with_suffix('.log'))['leaves'] != row['leaves']:
                raise RuntimeError(f'Invalid completed output {stem}')
            return row
        if stop.is_set():
            return None
        command = [str(executable), '26', '4', '5', '-m', str(i), str(args.parts)]
        t0 = time.monotonic()
        with stem.with_suffix('.g6').open('w') as graphs, stem.with_suffix('.log').open('w') as log:
            with lock:
                if stop.is_set():
                    return None
                process = subprocess.Popen(command, stdout=graphs, stderr=log, text=True)
                processes.add(process)
            try:
                code = process.wait()
            finally:
                with lock:
                    processes.discard(process)
        if code == 10:
            stop.set()
            with lock:
                for other in processes:
                    other.terminate()
            return {'part': i, 'status': 'candidate_needs_certificate', 'file': str(stem.with_suffix('.g6'))}
        if code and stop.is_set():
            return None
        if code:
            raise RuntimeError(f'Partition {i} failed with exit {code}; see {stem}.log')
        row = {'part': i, 'status': 'verified', 'seconds': time.monotonic() - t0,
               'log_sha256': digest(stem.with_suffix('.log')), **parse_log(stem.with_suffix('.log'))}
        if stem.with_suffix('.g6').read_text():
            raise RuntimeError(f'Unexpected graph output in partition {i}')
        atomic_json(checkpoint, row)
        return row

    rows = []
    try:
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            for future in as_completed([pool.submit(work, i) for i in range(1, args.parts + 1)]):
                row = future.result()
                if row is None:
                    continue
                rows.append(row)
                verified = sum(r['status'] == 'verified' for r in rows)
                status = 'candidate_needs_certificate' if stop.is_set() else ('complete' if verified == args.parts else 'running')
                report = {'status': status, 'scope': config, 'completed_parts': verified,
                          'wall_seconds': time.monotonic() - started,
                          'leaves': sum(r.get('leaves', 0) for r in rows),
                          'covers': sum(r.get('covers', 0) for r in rows),
                          'attempts': sum(r.get('attempts', 0) for r in rows),
                          'results': sorted(rows, key=lambda r: r['part'])}
                atomic_json(out / 'summary.json', report)
                print(f"{verified}/{args.parts} verified; part {row['part']}: {row['status']}; elapsed {time.monotonic()-started:.1f}s", flush=True)
    finally:
        stop.set()
        with lock:
            for process in processes:
                process.terminate()


if __name__ == '__main__':
    main()
