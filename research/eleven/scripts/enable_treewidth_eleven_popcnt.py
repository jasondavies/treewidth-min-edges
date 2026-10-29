"""Enable hardware population counts for subsequent girth-search partitions.

The C source and algorithm are unchanged. Validate partition 1 against its
completed baseline before atomically replacing the executable. Processes
already running retain the old executable. Both build hashes are recorded.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
from run_treewidth_edge_checks import CC, ROOT, digest, run


def atomic_json(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.replace(path)


def summary(path):
    values = [json.loads(line[10:]) for line in path.read_text().splitlines() if line.startswith('GENREG_TW ')]
    if len(values) != 1:
        raise RuntimeError(f'Missing or ambiguous result: {path}')
    return values[0]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--reuse-validation-log', type=Path)
    parser.add_argument('--reuse-validation-graphs', type=Path)
    parser.add_argument('--reuse-validation-binary', type=Path)
    args = parser.parse_args()
    reuse = (args.reuse_validation_log, args.reuse_validation_graphs, args.reuse_validation_binary)
    if any(reuse) and not all(reuse):
        parser.error('Supply all three validation files or none.')
    cpu_flags = [line.split(':', 1)[1].split() for line in Path('/proc/cpuinfo').read_text().splitlines()
                 if line.startswith('flags')]
    if not cpu_flags or not all('popcnt' in flags for flags in cpu_flags):
        raise RuntimeError('Every available CPU must support POPCNT.')
    out = args.directory.resolve()
    manifest_path = out / 'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    for name, value in manifest['configuration']['source_sha256'].items():
        if digest(ROOT / name) != value:
            raise RuntimeError(f'Run source has changed: {name}')
    if manifest.get('binary_variants'):
        raise RuntimeError('This run already records a binary optimization.')
    active = out / 'build/genreg-eleven'
    if digest(active) != manifest['binary_sha256']:
        raise RuntimeError('Active binary hash mismatch.')
    baseline = out / 'part-001.log'
    if not (out / 'part-001.json').exists():
        raise RuntimeError('Wait for the baseline first partition to finish.')
    build = out / 'popcnt-validation'
    build.mkdir(exist_ok=True)
    source = ROOT / 'scripts/genreg_treewidth_eleven.c'
    run(CC + ['-O3', '-mpopcnt', '-std=c11', '-c', source, '-o', build / 'adapter.o'])
    candidate = build / 'genreg-eleven'
    run(CC + [out / ('build/' + name + '.o') for name in ('genreg', 'main', 'optmid')]
        + [build / 'adapter.o', '-o', candidate])
    log_path, graph_path = build / 'part-001.log', build / 'part-001.g6'
    if all(reuse):
        if digest(candidate) != digest(args.reuse_validation_binary):
            raise RuntimeError('Reused validation tested a different binary.')
        log_path.write_bytes(args.reuse_validation_log.read_bytes())
        graph_path.write_bytes(args.reuse_validation_graphs.read_bytes())
    else:
        with log_path.open('w') as log, graph_path.open('w') as graphs:
            subprocess.run([str(candidate), '26', '4', '5', '-m', '1', '256'],
                           stdout=graphs, stderr=log, check=True)
    if 'Teil 1 von 256' not in log_path.read_text() or graph_path.read_text() or summary(log_path) != summary(baseline):
        raise RuntimeError('Optimized first partition differs from the baseline.')
    old_hash, new_hash = digest(active), digest(candidate)
    # Keep both exact binaries. The replacement is atomic; running processes
    # continue using the original inode. A same-source compiler optimization
    # does not change the modulo partitioning or any pruning decision.
    (build / 'baseline-executable').write_bytes(active.read_bytes())
    prepared = active.with_suffix('.new')
    prepared.write_bytes(candidate.read_bytes())
    prepared.chmod(0o755)
    activation = datetime.now(timezone.utc).isoformat()
    os.replace(prepared, active)
    manifest['binary_sha256'] = new_hash
    manifest['binary_variants'] = [
        {'sha256': old_hash, 'adapter_flags': ['-O3', '-std=c11']},
        {'sha256': new_hash, 'adapter_flags': ['-O3', '-mpopcnt', '-std=c11'],
         'activated_utc': activation, 'validation_log_sha256': digest(log_path),
         'validation_counts': summary(log_path)}]
    manifest['optimization_script_sha256'] = digest(Path(__file__))
    atomic_json(manifest_path, manifest)
    atomic_json(out / 'build/build.json', manifest)
    print('Activated -mpopcnt; first-partition counts match exactly.', flush=True)


if __name__ == '__main__':
    main()
