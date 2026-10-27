"""Reproduce the treewidth-ten proof in an isolated output directory.

Default: verify the witness, saved girth-five family, and all reconstructions.
--genreg-source: also regenerate the girth-five family from unmodified GENREG.
--full: first regenerate every treewidth-nine prerequisite and its families.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

from ten.common import CC, ROOT, run

GENREG_FILES = ('gendef.h', 'genreg.c', 'main.c', 'optmid.c')
RESIDUES = ('treewidth34-family34.g6', 'treewidth35-all-family.g6', 'treewidth36-family.g6')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    if not __debug__ or os.environ.get('PYTHONOPTIMIZE'):
        raise RuntimeError('Run without Python optimization: assertions verify certificates.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--workers', type=int, default=min(16, os.cpu_count() or 1))
    parser.add_argument('--genreg-source', type=Path)
    parser.add_argument('--full', action='store_true', help='regenerate k<=9 prerequisites too')
    args = parser.parse_args()
    if args.workers < 1:
        parser.error('--workers must be positive')
    if args.full and args.genreg_source is None:
        parser.error('--full requires --genreg-source')
    source = args.genreg_source.resolve() if args.genreg_source else None
    if source:
        for name in GENREG_FILES:
            if not (source / name).is_file():
                parser.error(f'missing GENREG source: {name}')
    out = args.output.resolve()
    if out == ROOT or ROOT in out.parents:
        parser.error('choose an output directory outside the checkout')
    out.mkdir(parents=True, exist_ok=True)
    config = {'full': args.full, 'workers': args.workers, 'compiler': CC,
              'geng_source': os.environ.get('GENG_SOURCE', '/usr/share/nauty/geng.c'),
              'genreg': {name: digest(source / name) for name in GENREG_FILES} if source else None,
              'inputs': {str(p.relative_to(ROOT)): digest(p)
                         for directory in ('scripts', 'sources')
                         for p in sorted((ROOT / directory).rglob('*'))
                         if p.is_file() and '__pycache__' not in p.parts}}
    manifest = out / 'inputs.json'
    workspace = out / 'workspace'
    if manifest.exists():
        if json.loads(manifest.read_text()) != config:
            raise RuntimeError('Inputs/options changed; use a fresh output directory.')
        for name, expected in config['inputs'].items():
            if digest(workspace / name) != expected:
                raise RuntimeError(f'Working copy changed: {name}; use a fresh output directory.')
    else:
        if any(out.iterdir()):
            raise RuntimeError('New output directory must be empty.')
        for directory in ('scripts', 'sources'):
            shutil.copytree(ROOT / directory, workspace / directory,
                            ignore=shutil.ignore_patterns('__pycache__'))
        manifest.write_text(json.dumps(config, indent=2) + '\n')
    results = out / 'runs'
    results.mkdir(exist_ok=True)
    workers = ['--workers', str(args.workers)]

    def invoke(script, *arguments):
        print('Running:', script, flush=True)
        subprocess.run([sys.executable, str(workspace / 'scripts' / script),
                        *map(str, arguments)], cwd=workspace, check=True)

    def report(name):
        return json.loads((results / name / 'summary.json').read_text())

    if args.full:
        prerequisites = out / 'prerequisites-nine'
        invoke('reproduce_nine.py', '--full', '--genreg-source', source,
               '--output', prerequisites, *workers)
        previous = json.loads((prerequisites / 'summary.json').read_text())
        assert previous['status'] == 'complete' and previous['minimum_edges'] == 42
        for name in RESIDUES:
            generated = prerequisites / 'sources/nine' / name
            reference = workspace / 'sources/nine' / name
            assert generated.read_bytes() == reference.read_bytes(), name
            shutil.copy2(generated, reference)

    invoke('ten/verify_treewidth_ten_witness.py')
    invoke('ten/run_treewidth46_four_cycles.py', '--output', results / 'four-cycles', *workers)
    assert report('four-cycles')['status'] == 'all_verified'
    assert report('four-cycles')['graphs'] == 969011
    invoke('ten/audit_treewidth46_four_cycles.py', '--output', results / 'four-cycle-audit', *workers)
    assert report('four-cycle-audit')['status'] == 'complete'
    assert report('four-cycle-audit')['graphs'] == 969011

    if source:
        executable = results / 'genreg'
        run(CC + ['-O3', '-w', '-std=gnu89', '-D__UNIX__',
                  *(source / name for name in GENREG_FILES if name.endswith('.c')), '-o', executable])
        (results / 'genreg-build.json').write_text(json.dumps({
            'upstream_sha256': config['genreg'], 'binary_sha256': digest(executable),
            'compiler': run(CC + ['--version']).stdout.splitlines()[0]}, indent=2) + '\n')
        inputs = ['--genreg', executable]
    else:
        inputs = ['--graphs', workspace / 'sources/ten/treewidth46-girth5.g6']
    invoke('ten/check_treewidth_ten_girth.py', *inputs, '--vertices', 23,
           '--output', results / 'girth23', *workers)
    assert report('girth23')['graphs'] == report('girth23')['verified_width_nine'] == 3917
    assert report('girth23')['candidates'] == 0
    assert (results / 'girth23/graphs.g6').read_bytes() == (
        workspace / 'sources/ten/treewidth46-girth5.g6').read_bytes()
    mode = 'full' if args.full else 'new steps regenerated' if source else 'saved-family certificates'
    summary = {'status': 'complete', 'mode': mode,
               'minimum_edges': 47 if args.full else None,
               'four_cycle_extensions': 969011, 'girth_five_graphs': 3917,
               'note': 'Only --full reruns the completeness of the prerequisite classifications.'}
    (out / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print('PASS:', mode, flush=True)


if __name__ == '__main__':
    main()
