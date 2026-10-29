"""Audit all checkpoints of the 256-partition quartic girth-five exclusion.

This checks run completeness and recorded verification counts. Mathematical
soundness also relies on GENREG and the documented supergraph argument.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    args = parser.parse_args()
    out = args.directory.resolve()
    manifest = json.loads((out / 'manifest.json').read_text())
    config = manifest['configuration']
    expected = {'vertices': 26, 'degree': 4, 'girth_at_least': 5, 'width_bound': 10, 'parts': 256}
    if any(config[k] != v for k, v in expected.items()):
        raise RuntimeError('Unexpected problem parameters.')
    for name, value in config['source_sha256'].items():
        if sha(ROOT / name) != value:
            raise RuntimeError(f'Source differs from recorded run: {name}')
    binary = out / 'build/genreg-eleven'
    if binary.exists() and sha(binary) != manifest['binary_sha256']:
        raise RuntimeError('Built executable differs from its recorded hash.')
    variants = manifest.get('binary_variants', [])
    if variants:
        if len(variants) != 2 or variants[0]['adapter_flags'] != ['-O3', '-std=c11'] or variants[1]['adapter_flags'] != ['-O3', '-mpopcnt', '-std=c11']:
            raise RuntimeError('Unexpected optimized build history.')
        if variants[1]['sha256'] != manifest['binary_sha256']:
            raise RuntimeError('Optimized executable hash is inconsistent.')
        if sha(ROOT / 'scripts/enable_treewidth_eleven_popcnt.py') != manifest['optimization_script_sha256']:
            raise RuntimeError('Optimization script differs from its recorded source.')
        validation = out / 'popcnt-validation/part-001.log'
        if sha(validation) != variants[1]['validation_log_sha256']:
            raise RuntimeError('Optimization validation log has changed.')
        baseline_counts = [json.loads(line[10:]) for line in (out / 'part-001.log').read_text().splitlines() if line.startswith('GENREG_TW ')]
        optimized_counts = [json.loads(line[10:]) for line in validation.read_text().splitlines() if line.startswith('GENREG_TW ')]
        if baseline_counts != optimized_counts or optimized_counts != [variants[1]['validation_counts']]:
            raise RuntimeError('Optimization changed the first-partition counts.')
    names = {f'part-{i:03d}.json' for i in range(1, 257)}
    if {p.name for p in out.glob('part-*.json')} != names:
        raise RuntimeError('The 256 completed partition files are not all present.')
    rows = []
    for i in range(1, 257):
        stem = out / f'part-{i:03d}'
        row = json.loads(stem.with_suffix('.json').read_text())
        text = stem.with_suffix('.log').read_text()
        if row['part'] != i or row['status'] != 'verified' or f'Teil {i} von 256' not in text:
            raise RuntimeError(f'Wrong partition or status: {i}')
        if sha(stem.with_suffix('.log')) != row['log_sha256'] or stem.with_suffix('.g6').read_text():
            raise RuntimeError(f'Log changed or candidate output present: {i}')
        results = [json.loads(line[10:]) for line in text.splitlines() if line.startswith('GENREG_TW ')]
        if len(results) != 1 or any(row.get(k) != v for k, v in results[0].items()):
            raise RuntimeError(f'Summary mismatch: {i}')
        if row['leaves'] != row['verified'] or row['negative'] != 0 or not 0 <= row['covers'] <= row['attempts']:
            raise RuntimeError(f'Invalid verification counts: {i}')
        rows.append(row)
    summary = json.loads((out / 'summary.json').read_text())
    if summary['status'] != 'complete' or summary['completed_parts'] != 256 or summary['scope'] != config:
        raise RuntimeError('Final summary is not complete or has inconsistent parameters.')
    if summary['results'] != rows:
        raise RuntimeError('Final summary does not match individual checkpoints.')
    totals = {key: sum(row[key] for row in rows) for key in ('leaves', 'covers', 'attempts')}
    if any(summary[key] != value for key, value in totals.items()):
        raise RuntimeError('Aggregate count mismatch.')
    print(json.dumps({'status': 'verified_complete', 'partitions': 256, **totals}, indent=2))


if __name__ == '__main__':
    main()
